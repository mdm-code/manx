"""Prons module takes care of LAEME pronoun grammel disambiguation."""

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
            # TODO: implement P23
            "P13": lambda x: x,
            "P21": self.infer_P21,
            "P22": self.infer_P22,
            "P23": self.infer_P23,
        }

    def __call__(self, p: Pronoun) -> str:
        return self.infer(p)

    def infer(self, p: Pronoun) -> str:
        try:
            return self.callables[p.base](p)
        except KeyError:
            # NOTE: Fall back to stripped grammel form
            return p.lexel

    def infer_P01(self, p: Pronoun) -> str:
        if "X" in p.remainder:
            if len(p.form) > 3:
                return "usself"
            return "us"
        if "G" in p.remainder:
            return "our"
        if "N" in p.remainder:
            return "we"
        if any(v in p.remainder for v in ["<pr", ">pr", "Oi", "Od"]):
            return "us"
        return "we"

    def infer_P02(self, p: Pronoun) -> str:
        if "G" in p.remainder:
            return "your"
        if "N" in p.remainder:
            return "you"
        if any(v in p.remainder for v in ["<pr", ">pr", "Oi", "Od", "X"]):
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
            if len(p.form) > 2 and any(v in p.form for v in ["n", "N"]):
                return "mine"
            return "my"
        if "N" in p.remainder:
            return "I"
        if any(v in p.remainder for v in ["<pr", ">pr", "Oi", "Od"]):
            return "me"
        return "I"

    def infer_P12(self, p: Pronoun) -> str:
        if "+ward" in p.remainder:
            return "theeward"
        if "X" in p.remainder:
            if len(p.form) > 2:
                return "theeself"
            return "thee"
        if "G" in p.remainder:
            if len(p.form) > 2 and any(v in p.form for v in ["n", "N"]):
                return "thine"
            return "thy"
        if "N" in p.remainder:
            return "thou"
        if any(v in p.remainder for v in ["<pr", ">pr", "Oi", "Od", "-av"]):
            return "thee"
        return "thou"

    def infer_P21(self, p: Pronoun) -> str:
        if "D" in p.remainder:
            if "G" in p.remainder:
                if len(p.form) > 3:
                    return "unker"
                return "unk"
            if "N" in p.remainder:
                return "wit"
            if any(v in p.remainder for v in ["<pr", ">pr", "Oi", "Od"]):
                return "unk"
            return "wit"
        if "X" in p.remainder:
            if len(p.form) > 3:
                return "usself"
            return "us"
        if "G" in p.remainder:
            return "our"
        if "N" in p.remainder:
            return "we"
        if any(v in p.remainder for v in ["<pr", ">pr", "Oi", "Od"]):
            return "us"
        return "we"

    def infer_P22(self, p: Pronoun) -> str:
        if "D" in p.remainder:
            if "X" in p.remainder:
                if len(p.form) > 4:
                    return "inkself"
                return "ink"
            if "G" in p.remainder:
                if len(p.form) > 4:
                    return "inker"
                return "ink"
            if "N" in p.remainder:
                return "git"
            if any(v in p.remainder for v in ["<pr", ">pr", "Oi", "Od"]):
                return "ink"
            return "git"
        if "X" in p.remainder:
            if len(p.form) > 4:
                return "youself"
            return "you"
        if "G" in p.remainder:
            return "your"
        if "N" in p.remainder:
            return "you"
        if any(v in p.remainder for v in ["<pr", ">pr", "Oi", "Od"]):
            return "you"
        return "you"

    def infer_P23(self, p: Pronoun) -> str:
        if "X" in p.remainder:
            if len(p.form) > 4:
                return "themself"
            return "them"
        if "G" in p.remainder:
            return "their"
        if "N" in p.remainder:
            return "they"
        if any(v in p.remainder for v in ["<pr", ">pr", "Oi", "Od"]):
            return "them"
        return "they"


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
