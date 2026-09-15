import pytest
from agentflow.models import AgentResult


def test_invalid_route_combination() -> None:
    with pytest.raises(ValueError):
        AgentResult(status="approved", route="tester")
