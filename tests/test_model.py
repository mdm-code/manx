# Standard library imports
from contextlib import nullcontext as does_not_raise

# Local library imports
from manx.model import t5


def test_t5_predict(monkeypatch) -> None:
    """Test T5 predict with mocked SimpleT5 method calls."""
    def _mocked_predict(*args, **kwargs) -> str: ...
    monkeypatch.setattr("manx.model.SimpleT5.predict", _mocked_predict)

    def _mocked_load_model(*args, **kwargs) -> None: ...
    monkeypatch.setattr("manx.model.SimpleT5.load_model", _mocked_load_model)

    with does_not_raise():
        t5.predict(
            "NIyIG HIS DEYD~ ME BURIICTH HIM COVE COMEZ yE yUNGE STRUPLING"
        )
