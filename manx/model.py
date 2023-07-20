"""Model offers boostrapped T5 model instance."""

# Standard library imports
from contextlib import redirect_stdout, redirect_stderr

# Third-party library imports
with open("/dev/null") as f:
    with redirect_stderr(f), redirect_stdout(f):
        from simplet5 import SimpleT5

# Local library imports
from manx.config import settings


class T5:
    def predict(
        self,
        text: str,
        prefix: str = settings.T5_PREFIX
    ) -> list[str]:
        "Generate prediction from T5 model for the given text."
        text = prefix + ": " + text
        return self.model.predict(text)

    @property
    def model(self) -> SimpleT5:
        """Underlying T5 model initialized with the first invokation."""
        if hasattr(self, "_model"):
            return self._model
        self._model = SimpleT5()
        self._model.load_model(
            model_type=settings.MODEL_TYPE,
            model_dir=settings.MODEL_DIR,
            use_gpu=settings.USE_GPU,
        )
        return self._model


t5 = T5()
