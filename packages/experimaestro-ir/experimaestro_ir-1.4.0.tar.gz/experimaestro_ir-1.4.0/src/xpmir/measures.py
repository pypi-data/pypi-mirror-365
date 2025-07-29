from typing import Optional
import ir_measures as irm
from experimaestro import Param
from datamaestro_text.data.ir import Measure as BaseMeasure


class Measure(BaseMeasure):
    """Mirrors the ir_measures metric object"""

    identifier: Param[str]
    """main identifier"""

    rel: Param[int] = 1
    """minimum relevance score to be considered relevant (inclusive)"""

    cutoff: Param[Optional[int]]
    """Cutoff value"""

    def __matmul__(self, cutoff):
        return Measure.C(identifier=self.identifier, rel=self.rel, cutoff=int(cutoff))

    def __call__(self):
        measure = irm.parse_measure(self.identifier)
        if self.cutoff is not None:
            measure = measure @ self.cutoff
        return measure

    def __repr__(self):
        return f"{self.identifier}@{self.cutoff}/rel={self.rel}"


AP = Measure.C(identifier="AP")
"""Average precision metric"""

P = Measure.C(identifier="P")
"""Precision at rank"""

RR = Measure.C(identifier="RR")
"""Reciprocical rank"""

nDCG = Measure.C(identifier="nDCG")
"""Normalized Discounted Cumulated Gain"""

R = Measure.C(identifier="R")
"""Recall at rank"""

Success = Measure.C(identifier="Success")
"""1 if a document with at least rel relevance is found in the first cutoff
documents, else 0."""
