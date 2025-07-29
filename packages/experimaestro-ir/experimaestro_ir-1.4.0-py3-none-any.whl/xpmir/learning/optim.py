from dataclasses import dataclass
from enum import Enum
import threading
from typing import Any, Callable, List, Optional, TYPE_CHECKING, Union
from pathlib import Path
import numpy as np
import torch
import re

from experimaestro import (
    Config,
    Param,
    tagspath,
    Task,
    PathSerializationLWTask,
    experiment,
    RunMode,
)
from experimaestro.scheduler import Job, Listener
from experimaestro.utils import cleanupdir
from xpmir.utils.logging import easylog, LazyJoin
from experimaestro.scheduler.services import WebService
from xpmir.context import Hook, Context
from xpmir.utils.utils import Initializable, foreach
from xpmir.learning.metrics import ScalarMetric
from .schedulers import Scheduler

if TYPE_CHECKING:
    from xpmir.learning.context import TrainerContext

logger = easylog()


class Optimizer(Config):
    def __call__(self, parameters) -> torch.optim.Optimizer:
        raise NotImplementedError()


class SGD(Optimizer):
    """Wrapper for SGD optimizer in Pytorch"""

    lr: Param[float] = 1e-5
    """Learning rate"""

    weight_decay: Param[float] = 0.0
    """Weight decay (L2)"""

    def __call__(self, parameters):
        from torch.optim import SGD

        return SGD(parameters, lr=self.lr, weight_decay=self.weight_decay)


class Adafactor(Optimizer):
    """Wrapper for Adafactor optimizer in Transformers library

    See :class:`transformers.optimization.Adafactor` for full documentation
    """

    lr: Param[Optional[float]] = None
    """Learning rate"""

    weight_decay: Param[float] = 0.0
    """Weight decay (L2)"""

    relative_step: Param[bool] = True
    """If true, time-dependent learning rate is computed instead of external
    learning rate"""

    def __call__(self, parameters):
        from transformers.optimization import Adafactor

        return Adafactor(
            parameters,
            lr=self.lr,
            weight_decay=self.weight_decay,
            relative_step=self.relative_step,
        )


class Adam(Optimizer):
    """Wrapper for Adam optimizer in PyTorch"""

    lr: Param[float] = 1e-3
    """Learning rate"""

    weight_decay: Param[float] = 0.0
    """Weight decay (L2)"""

    eps: Param[float] = 1e-8

    def __call__(self, parameters):
        from torch.optim import Adam

        return Adam(
            parameters, lr=self.lr, weight_decay=self.weight_decay, eps=self.eps
        )


class AdamW(Optimizer):
    """Adam optimizer that takes into account the regularization

    See the `PyTorch documentation
    <https://pytorch.org/docs/stable/generated/torch.optim.AdamW.html>`_
    """

    lr: Param[float] = 1e-3
    weight_decay: Param[float] = 1e-2
    eps: Param[float] = 1e-8

    def __call__(self, parameters):
        from torch.optim import AdamW

        return AdamW(
            parameters, lr=self.lr, weight_decay=self.weight_decay, eps=self.eps
        )


class ModuleInitMode(Enum):
    """Initialization mode"""

    #: Default initialization (i.e. can load default parameters or initialize randomly)
    DEFAULT = 0

    #: No parameter initialization (just initialize the structure of the model)
    NONE = 1

    #: Random initialization (initialize the structure, then use a the random
    #: number generator to initialize the values)
    RANDOM = 2

    def to_options(self, random: Optional[np.random.RandomState] = None):
        return ModuleInitOptions(self, random)


@dataclass
class ModuleInitOptions:
    #: Initialization mode
    mode: ModuleInitMode

    #: Random generator (only defined when mode is RANDOM)
    random: Optional[np.random.RandomState] = None


class Module(Config, Initializable, torch.nn.Module):
    """A module contains parameters"""

    def __init__(self):
        Initializable.__init__(self)
        torch.nn.Module.__init__(self)

    def __initialize__(self, options: ModuleInitOptions):
        """Initialize a module

        :param options: The initialization options
        """
        pass

    def __call__(self, *args, **kwargs):
        return torch.nn.Module.__call__(self, *args, **kwargs)

    def to(self, *args, **kwargs):
        return torch.nn.Module.to(self, *args, **kwargs)


class ModuleList(Module, Initializable):
    """Groups different models together, to be used within the Learner"""

    sub_modules: Param[List[Module]]

    def __post_init__(self):
        # Register sub-modules
        for ix, sub_module in enumerate(self.sub_modules):
            self.add_module(str(ix), sub_module)

    def __initialize__(self, options: ModuleInitOptions):
        for module in self.sub_modules:
            module.initialize(options)

    def __call__(self, *args, **kwargs):
        raise AssertionError("This module cannot be used as such")

    def to(self, *args, **kwargs):
        return torch.nn.Module.to(self, *args, **kwargs)


class ModuleLoader(PathSerializationLWTask):
    def execute(self):
        """Loads the model from disk using the given serialization path"""
        logger.info("Loading model from disk: %s", self.path)
        self.value.initialize(ModuleInitMode.NONE.to_options())
        data = torch.load(self.path)
        self.value.load_state_dict(data)


class ParameterFilter(Config):
    """One abstract class which doesn't do the filtrage"""

    def __call__(self, name, params) -> bool:
        """Returns true if the parameters should be optimized with the
        associated optimizer"""
        return True


class RegexParameterFilter(ParameterFilter):
    """gives the name of the model to do the filtrage
    Precondition: Only and just one of the includes and excludes can be None"""

    includes: Param[Optional[List[str]]] = None
    """The str of params to be included from the model"""

    excludes: Param[Optional[List[str]]] = None
    """The str of params to be excludes from the model"""

    def __init__(self):
        self.name = set()

    def __validate__(self):
        return self.includes or self.excludes

    def __repr__(self) -> str:
        return f"RegexParameterFilter({self.includes}, {self.excludes})"

    def __call__(self, name, params) -> bool:
        # Look first at included
        if self.includes:
            for regex in self.includes:
                if re.search(regex, name):
                    return True

            # Include if not excluded
            if not self.excludes:
                return False

        for regex in self.excludes:
            if re.search(regex, name):
                return False

        return True


class ParameterOptimizer(Config):
    """Associates an optimizer with a list of parameters to optimize"""

    optimizer: Param[Optimizer]
    """The optimizer"""

    scheduler: Param[Optional[Scheduler]]
    """The optional scheduler"""

    module: Param[Optional[Module]]
    """The module from which parameters should be extracted"""

    filter: Param[Optional[ParameterFilter]] = ParameterFilter.C()
    """How parameters should be selected for this (by default, use them all)"""

    def create_optimizer(
        self, module: Module, filter: Callable[[str, Any], bool]
    ) -> torch.optim.Optimizer:
        """Returns a (pytorch) optimizer"""
        module = self.module or module
        params = {
            name: param
            for name, param in module.named_parameters()
            if (self.filter is None or self.filter(name, param)) and filter(name, param)
        }
        if not params:
            logger.warning(
                "Parameter list: %s", [name for name, _ in module.named_parameters()]
            )
            raise RuntimeError(f"Parameter list is empty with {self.filter}")

        logger.debug(
            "Optimizing with %s parameters [%s]",
            self.filter,
            LazyJoin(",", params.keys()),
        )
        optimizer = self.optimizer(params.values())
        return optimizer


class DuplicateParameterFilter:
    """Filters out already optimized parameters"""

    def __init__(self):
        self.parameters = set()

    def __call__(self, name, params):
        if params in self.parameters:
            return False
        self.parameters.add(params)
        return True


class OptimizationHook(Hook):
    """Base class for all optimization hooks"""

    pass


class GradientHook(OptimizationHook):
    """Hooks that are called when the gradient is computed

    The gradient is guaranteed to be unscaled in this case.
    """

    pass


class GradientClippingHook(GradientHook):
    """Gradient clipping"""

    max_norm: Param[float]
    """Maximum norm for gradient clipping"""

    def __call__(self, main: "ScheduledOptimizer"):
        torch.nn.utils.clip_grad_norm_(main.module.parameters(), self.max_norm)


class GradientLogHook(GradientHook):
    """ "Log the gradient norm"""

    name: Param[str] = "gradient_norm"

    def __call__(self, main: "ScheduledOptimizer"):
        sum_norms = 0.0
        n_params = 0
        with torch.no_grad():
            for param in main.module.parameters():
                if param.grad is not None:
                    n_params += param.grad.numel()
                    sum_norms += param.grad.numel() * param.grad.norm() ** 2

        main.trainer_context.writer.add_scalar(
            self.name, sum_norms / n_params, main.trainer_context.state.step
        )


class ScheduledOptimizer:
    def initialize(
        self,
        param_optimizers: List[ParameterOptimizer],
        num_training_steps: int,
        module: Module,
        use_scaler: bool,
        hooks: List[OptimizationHook] = [],
        trainer_context: Optional["TrainerContext"] = None,
    ):
        self.schedulers = []
        self.scheduler_factories = []
        self.optimizers = []
        self.scheduler_steps = -1  # Number of scheduler steps
        self.num_training_steps = num_training_steps
        self.module = module
        self.context = Context(hooks)
        self.trainer_context = trainer_context

        try:
            next(module.parameters())
        except StopIteration:
            raise RuntimeError(f"No parameters to optimize in the module {module}")

        filter = DuplicateParameterFilter()
        for param_optimizer in param_optimizers:
            optimizer = param_optimizer.create_optimizer(module, filter)
            self.optimizers.append(optimizer)
            self.scheduler_factories.append(param_optimizer.scheduler)

        self.reset_schedulers()

        assert len(self.schedulers) == len(self.optimizers)

        if use_scaler:
            logger.info("Using GradScaler when optimizing")
        self.scaler = torch.amp.GradScaler('cuda') if use_scaler else None

    def load_state_dict(self, state):
        for optimizer, optimizer_state in zip(self.optimizers, state["optimizers"]):
            optimizer.load_state_dict(optimizer_state)

        if self.scaler is not None:
            self.scaler.load_state_dict(state["scaler"])

        # Re-create schedulers
        self.scheduler_steps = state["scheduler_steps"]
        self.reset_schedulers()

    def reset_schedulers(self):
        self.schedulers = []
        for optimizer, scheduler_factory in zip(
            self.optimizers, self.scheduler_factories
        ):
            if scheduler_factory is None:
                self.schedulers.append(None)
            else:
                self.schedulers.append(
                    scheduler_factory(
                        optimizer,
                        self.num_training_steps,
                        last_epoch=self.scheduler_steps,
                    )
                )

    def state_dict(self):
        return {
            "optimizers": [optimizer.state_dict() for optimizer in self.optimizers],
            "scaler": None if self.scaler is None else self.scaler.state_dict(),
            "scheduler_steps": self.scheduler_steps,
        }

    def scale(self, loss: torch.Tensor):
        if self.scaler is None:
            return loss
        return self.scaler.scale(loss)

    def zero_grad(self):
        """Zero-grad for all optimizers"""
        for optimizer in self.optimizers:
            optimizer.zero_grad()

    def optimizer_step(self, context: "TrainerContext"):
        """Performs an optimizer step (using the scaler if defined)"""
        if self.scaler is None:
            # Apply gradient hooks
            foreach(
                self.context.hooks(GradientHook),
                lambda hook: hook(self),
            )

            for optimizer in self.optimizers:
                optimizer.step()

        else:
            # Unscale first
            for optimizer in self.optimizers:
                self.scaler.unscale_(optimizer)

            # Apply gradient hooks
            foreach(
                self.context.hooks(GradientHook),
                lambda hook: hook(self),
            )

            # Step
            for optimizer in self.optimizers:
                self.scaler.step(optimizer)
            context.add_metric(
                ScalarMetric("gradient/scaler", self.scaler.get_scale(), 1)
            )
            self.scaler.update()

    def scheduler_step(self, context: "TrainerContext"):
        """Performs a step for all the schedulers"""
        for ix, scheduler in enumerate(self.schedulers):
            if scheduler is not None:
                for p_ix, lr in enumerate(scheduler.get_last_lr()):
                    context.add_metric(
                        ScalarMetric(f"gradient/scheduler/{ix+1}/{p_ix+1}", lr, 1)
                    )
                scheduler.step()
        self.scheduler_steps += 1


Optimizers = Union[ParameterOptimizer, Optimizer, List[ParameterOptimizer]]
"""Defines a set of optimizers"""


def get_optimizers(optimizers: Optimizers):
    """Returns a list of ParameterOptimizer"""
    if isinstance(optimizers, list):
        return optimizers

    if isinstance(optimizers, ParameterOptimizer):
        return [optimizers]

    return [ParameterOptimizer(optimizer=optimizers)]


class TensorboardServiceListener(Listener):
    def __init__(self, source: Path, target: Path):
        self.source = source
        self.target = target

    def job_state(self, job: Job):
        if not job.state.notstarted():
            if not self.source.is_symlink():
                try:
                    self.source.symlink_to(self.target)
                except Exception:
                    logger.exception(
                        "Cannot symlink %s to %s", self.source, self.target
                    )


class TensorboardService(WebService):
    id = "tensorboard"

    def __init__(self, xp: experiment, path: Path):
        super().__init__()

        self.path = path
        self.url = None
        self.run_mode = xp.run_mode

        if self.run_mode == RunMode.NORMAL:
            cleanupdir(self.path)
            self.path.mkdir(exist_ok=True, parents=True)
            logger.info("You can monitor learning with:")
            logger.info("tensorboard --logdir=%s", self.path)

    def add(self, task: Task, path: Path):
        # Wait until config has started
        if self.run_mode == RunMode.NORMAL:
            if job := task.__xpm__.job:
                if job.scheduler is not None:
                    tag_path = tagspath(task)
                    if tag_path:
                        job.scheduler.addlistener(
                            TensorboardServiceListener(self.path / tag_path, path)
                        )
                    else:
                        logger.error(
                            "The task is not associated with tags: "
                            "cannot link to tensorboard data"
                        )
                else:
                    logger.debug("No scheduler: not adding the tensorboard data")
            else:
                logger.error(
                    "Task was not started: cannot link to tensorboard job path"
                )

    def description(self):
        return "Tensorboard service"

    def close(self):
        if self.server and self.run_mode == RunMode.NORMAL:
            self.server.shutdown()

    def _serve(self, running: threading.Event):
        if self.run_mode != RunMode.NORMAL:
            return

        import tensorboard as tb

        try:
            logger.info("Starting %s service", self.id)
            self.program = tb.program.TensorBoard()
            self.program.configure(
                host="localhost",
                logdir=str(self.path.absolute()),
                path_prefix=f"/services/{self.id}",
                port=0,
            )
            self.server = self.program._make_server()

            self.url = self.server.get_url()
            running.set()
            self.server.serve_forever()
        except Exception:
            logger.exception("Error while starting tensorboard")
            running.set()
