"""Prons module takes care of LAEME pronoun tagging disambiguation."""

# Standard library imports
from __future__ import annotations


class Pruner:
    """Pruner removes unnecessary elements of LAEME pronoun grammels."""

    @classmethod
    def __call__(cls, form: str) -> str:
        return cls.prune(form)

    @classmethod
    def prune(cls, form: str) -> str:
        # NOTE: Do not reorder if statements unless you know what you're doing
        # NOTE: X stands for any single ASCII codepoint
        if (idx := form.find("{rh}")) != -1:
            offset = len("{rh}")
            return cls.prune(form[:idx] + form[idx + offset :])
        if (idx := form.find("+")) != -1 and form[
            idx : idx + len("+ward")
        ] != "+ward":
            offset = len("+X")
            return cls.prune(form[:idx] + form[idx + offset :])
        if (idx := form.find("-voc")) != -1:
            offset = len("-voc")
            return cls.prune(form[:idx] + form[idx + offset :])
        if (idx := form.find("-a")) != -1 and form[
            idx : idx + len("-av")
        ] != "-av":
            offset = len("-aX")
            return cls.prune(form[:idx] + form[idx + offset :])
        if (idx := form.find("-Gn")) != -1:
            offset = len("-Gn")
            return cls.prune(form[:idx] + form[idx + offset :])
        if (idx := form.find("pn")) != -1:
            offset = len("pn")
            return cls.prune(form[:idx] + form[idx + offset :])
        if (idx := form.find("pl")) != -1:
            offset = len("pl")
            return cls.prune(form[:idx] + form[idx + offset :])
        if (idx := form.find("int")) != -1:
            offset = len("int")
            return cls.prune(form[:idx] + form[idx + offset :])
        if (idx := form.find(">=")) != -1:
            offset = len(">=")
            return cls.prune(form[:idx] + form[idx + offset :])
        if (idx := form.rfind("<")) != -1 and form[
            idx : idx + len("<pr")
        ] != "<pr":
            offset = len("<")
            return cls.prune(form[:idx] + form[idx + offset :])
        if (idx := form.rfind(">")) != -1 and form[
            idx : idx + len(">pr")
        ] != ">pr":
            offset = len(">")
            return cls.prune(form[:idx] + form[idx + offset :])
        return form


class PronounMapper:
    """PronounMapper swaps LAEME pronoun grammels for familiar labels."""

    def __init__(self) -> None:
        self.callables = {
            "P01": self.infer_P01,
            "P02": self.infer_P02,
            "P11": self.infer_P11,
            "P12": self.infer_P12,
        }

    def __call__(self, p: Pronoun) -> str:
        return self.infer(p)

    def infer(self, p: Pronoun) -> str:
        # TODO: this can be handled w/o match statement
        # callable = self.callables.get(p.base, None)
        # if callable: return callable(p)
        match p.base:
            case "P01":
                return self.callables[p.base](p)
            case "P02":
                return self.callables[p.base](p)
            case "P11":
                return self.callables[p.base](p)
            case "P12":
                # TODO: Implement the second person singular
                return self.callables[p.base](p)
            case _:
                return ""

    def infer_P01(self, p: Pronoun) -> str:
        if "G" in p.remainder:
            return "our"
        if "N" in p.remainder:
            return "we"
        if "X" in p.remainder:
            # NOTE: account for words like VSSELVEN
            if len(p.form) > 3:
                return "usself"
            return "us"
        if any(v in p.remainder for v in ["<pr", ">pr", "Oi", "Od"]):
            return "us"
        return "we"

    def infer_P02(self, p: Pronoun) -> str:
        if "G" in p.remainder:
            return "your"
        if "N" in p.remainder:
            return "you"
        if any(
            v in p.remainder for v in ["<pr", ">pr", "Oi", "Od", "X"]
        ):
            return "you"
        return "you"

    def infer_P11(self, p: Pronoun) -> str:
        if "+ward" in p.remainder:
            return "meward"
        if "X" in p.remainder:
            if len(p.form) > 2:
                return "meself"
            return "me"
        if "G" in p.remainder:
            if (
                len(p.form) > 2 and any(
                    v in p.form for v in ["n", "N"]
                )
            ):
                return "mine"
            return "my"
        if "N" in p.remainder:
            return "I"
        if any(v in p.remainder for v in ["<pr", ">pr", "Oi", "Od"]):
            return "me"
        return "I"

    def infer_P12(self, p: Pronoun) -> str:
        # NOTE: N has to come after G
        if "+ward" in p.remainder:
            return "theeward"
        if "X" in p.remainder:
            if len(p.form) > 2:
                return "theeself"
            return "thee"
        if "G" in p.remainder:
            if (
                len(p.form) > 2 and any(
                    v in p.form for v in ["n", "N"]
                )
            ):
                return "thine"
            return "thy"
        if "N" in p.remainder:
            return "thou"
        if any(v in p.remainder for v in ["<pr", ">pr", "Oi", "Od", "-av"]):
            return "thee"
        return "thou"


class Pronoun:
    def __init__(self, lexel: str, form: str) -> None:
        self._lexel = lexel
        self._form = form

        self.pruner = Pruner()
        self.mapper = PronounMapper()

    @property
    def lexel(self) -> str:
        return self.pruner(self._lexel)

    @property
    def mapped(self) -> str:
        return self.mapper(self)

    @property
    def form(self) -> str:
        return self._form

    @property
    def base(self) -> str:
        return self.lexel[:3]

    @property
    def remainder(self) -> str:
        return self.lexel[3:]
