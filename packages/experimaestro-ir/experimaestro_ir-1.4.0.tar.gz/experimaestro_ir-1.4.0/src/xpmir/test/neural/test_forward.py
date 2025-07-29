import logging
from typing import List, Tuple
import itertools
import pytest
import torch
from collections import defaultdict
from experimaestro import Constant
from datamaestro_text.data.ir import TextItem, create_record
from datamaestro.record import Record
from datamaestro_text.data.ir import TextItem
from xpmir.index import Index
from xpmir.learning import Random, ModuleInitMode
from xpmir.neural.dual import CosineDense, DotDense
from xpmir.letor.records import (
    PairwiseRecord,
    PairwiseRecords,
    PointwiseRecord,
    PointwiseRecords,
    ProductRecords,
)
from xpmir.text.tokenizers import Tokenizer
from xpmir.text.encoders import (
    TokenizedTextEncoderBase,
    DualTextEncoder,
    TokensRepresentationOutput,
    TokenizerOptions,
    RepresentationOutput,
)
from xpmir.text.adapters import MeanTextEncoder


class TestTokenizer(Tokenizer):
    def __init__(self):
        self.map = {}
        self._dummy_params = torch.nn.Parameter(torch.Tensor())

    def tok2id(self, tok: str) -> int:
        try:
            return self.map[tok]
        except KeyError:
            tokid = len(self.map)
            self.map[tok] = tokid
            return tokid


class RandomTokensEncoder(TokenizedTextEncoderBase[Record, TokensRepresentationOutput]):
    DIMENSION = 7
    MAX_WORDS = 100

    def __initialize__(self, options):
        super().__initialize__(options)
        self.embed = torch.nn.Embedding.from_pretrained(
            torch.randn(RandomTokensEncoder.MAX_WORDS, RandomTokensEncoder.DIMENSION)
        )
        self.tokenizer = TestTokenizer().instance()

    @property
    def dimension(self) -> int:
        return RandomTokensEncoder.DIMENSION

    @property
    def pad_tokenid(self) -> int:
        return 0

    def forward(self, records: List[Record], options=None):
        options = options or TokenizerOptions()
        tok_texts = self.tokenizer.batch_tokenize(
            [record[TextItem].text for record in records], maxlen=options.max_length, mask=True
        )
        return TokensRepresentationOutput(self.embed(tok_texts.ids), tok_texts)

    def static(self) -> bool:
        return False


class CustomIndex(Index):
    id: Constant[int] = 1

    @property
    def documentcount(self):
        return 50

    def term_df(self, term: str):
        return 1


# ---
# --- Model factories
# ---

modelfactories = []


def registermodel(method):
    modelfactories.append(
        pytest.param(method, marks=pytest.mark.dependency(name=f"model-{method}"))
    )
    return method


@registermodel
def drmm():
    """Drmm factory"""
    from xpmir.neural.interaction.drmm import Drmm
    from xpmir.neural.interaction.common import CosineSimilarity

    drmm = Drmm(
        encoder=RandomTokensEncoder(),
        index=CustomIndex(),
        similarity=CosineSimilarity(),
    )
    return drmm.instance()


@registermodel
def colbert_cos():
    """Colbert model factory"""
    from xpmir.neural.interaction.colbert import Colbert
    from xpmir.neural.interaction.common import CosineSimilarity

    return Colbert(
        encoder=RandomTokensEncoder(), similarity=CosineSimilarity()
    ).instance()


@registermodel
def dotdense():
    """Dense model factory"""
    return DotDense(
        encoder=MeanTextEncoder(encoder=RandomTokensEncoder()),
        query_encoder=MeanTextEncoder(encoder=RandomTokensEncoder()),
    ).instance()


@registermodel
def cosinedense():
    """Cosine model factory"""
    return CosineDense(
        encoder=MeanTextEncoder(encoder=RandomTokensEncoder()),
        query_encoder=MeanTextEncoder(encoder=RandomTokensEncoder()),
    ).instance()


class DummyDualTextEncoder(DualTextEncoder):
    def __init__(self):
        super().__init__()
        self.cache = defaultdict(lambda: torch.randn(1, 13))

    @property
    def dimension(self) -> int:
        return 13

    def static(self):
        return False

    def forward(self, texts: List[Tuple[str, str]]):
        return RepresentationOutput(torch.cat([self.cache[text] for text in texts]))


@registermodel
def cross_scorer():
    """Cross-scorer classifier factory"""
    from xpmir.neural.cross import CrossScorer

    return CrossScorer(max_length=100, encoder=DummyDualTextEncoder()).instance()


# ---
# --- Input factory
# ---

QUERIES = [
    create_record(text="purple cat"),
    create_record(text="yellow house"),
]
DOCUMENTS = [
    create_record(id="1", text="the cat sat on the mat"),
    create_record(id="2", text="the purple car"),
    create_record(id="3", text="my little dog"),
    create_record(id="4", text="the truck was on track"),
]


def pointwise():
    # Pointwise inputs
    inputs = PointwiseRecords()

    # Implicit order (Q0, D0) (Q1, D0) (Q0, D1) (Q1, D1)
    inputs.add(PointwiseRecord(QUERIES[0], DOCUMENTS[0], 0.0))
    inputs.add(PointwiseRecord(QUERIES[0], DOCUMENTS[0], 0.0))
    inputs.add(PointwiseRecord(QUERIES[1], DOCUMENTS[2], 0.0))
    inputs.add(PointwiseRecord(QUERIES[1], DOCUMENTS[1], 0.0))
    return inputs


def pairwise():
    # Implicit order (Q0, D0) (Q1, D0) (Q0, D1) (Q1, D1)
    inputs = PairwiseRecords()
    inputs.add(PairwiseRecord(QUERIES[0], DOCUMENTS[0], DOCUMENTS[1]))
    inputs.add(PairwiseRecord(QUERIES[1], DOCUMENTS[2], DOCUMENTS[3]))
    return inputs


def product():
    # Implicit order (Q0, D0) (Q0, D1) (Q1, D0)
    inputs = ProductRecords()
    inputs.add_topics(QUERIES[0], QUERIES[1])
    inputs.add_documents(DOCUMENTS[0], DOCUMENTS[1])

    return inputs


inputfactories = [pointwise, pairwise, product]


@pytest.mark.parametrize("modelfactory", modelfactories)
@pytest.mark.parametrize("inputfactory", inputfactories)
@pytest.mark.dependency()
def test_forward_types(modelfactory, inputfactory):
    """Test that each record type is handled"""
    model = modelfactory()
    random = Random().instance().state
    model.initialize(ModuleInitMode.RANDOM.to_options(random))

    inputs = inputfactory()

    logging.debug("%s", model(inputs, None))


@pytest.mark.parametrize("modelfactory", modelfactories)
@pytest.mark.parametrize(
    "inputfactoriescouple",
    (
        pytest.param((f1, f2), id=f"{f1.__name__}-{f2.__name__}")
        for f1, f2 in itertools.combinations(inputfactories, 2)
    ),
)
def test_forward_consistency(modelfactory, inputfactoriescouple):
    """Test that outputs are consistent between the different records types"""
    model = modelfactory()
    random = Random().instance().state
    model.initialize(ModuleInitMode.DEFAULT.to_options(random))

    outputs = []
    maps = []
    with torch.no_grad():
        for f in inputfactoriescouple:
            input = f()
            outputs.append(model(input, None))
            maps.append(
                {
                    (qr[TextItem].text, dr[TextItem].text): ix
                    for ix, (qr, dr) in enumerate(zip(input.queries, input.documents))
                }
            )

    inter = set(maps[0].keys() & maps[1].keys())
    assert len(inter) > 0, "No common query/document pair"
    for key in inter:
        s1 = outputs[0][maps[0][key]].item()
        s2 = outputs[1][maps[1][key]].item()
        assert s1 == pytest.approx(
            s2, abs=1e-6
        ), f"{s1} different from {s2} in {outputs[0]}, {outputs[1]}"
