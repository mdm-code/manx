"""Prons module takes care of LAEME pronoun tagging disambiguation.."""

# Standard library imports
from __future__ import annotations


# class Attribs(TypedDict, total=False):
#     strip: list[str]


class Pruner:
    @classmethod
    def __call__(cls, form: str) -> str:
        return cls.prune(form)

    @classmethod
    def prune(cls, form: str) -> str:
        if (idx := form.find("{rh}")) != -1:
            offset = len("{rh}")
            return cls.prune(form[:idx] + form[idx + offset :])
        if (idx := form.find("+")) != -1:
            offset = len("+X")  # NOTE: X stands for any single ASCII codepoint
            return cls.prune(form[:idx] + form[idx + offset :])
        return form


class Memo:
    def __init__(self, form: str) -> None:
        self._form = form
        self.pruner = Pruner()

    @property
    def form(self) -> str:
        return self.pruner(self._form)

    @property
    def base(self) -> str:
        return self.form[:3]

    @property
    def reminder(self) -> str:
        return self.form[3:]


class PronounMapper:
    """PronounMapper replaces personal pronoun grammels with familiar labels.

    The process of mapping has no theoretical basis on is purely practical.
    The LAEME personal pronoun grammel labelling system is complex. A simpler
    system is needed for users with little or no practice with LAEME grammel
    labels.
    """

    @staticmethod
    def infer(_: str) -> str:
        return ""
