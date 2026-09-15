import pytest


@pytest.mark.e2e
@pytest.mark.skip(reason="E2E scenarios will be added with the first customer workflow")
def test_e2e_smoke_placeholder() -> None:
    """Reserved entry point for full application E2E coverage."""
    assert True
