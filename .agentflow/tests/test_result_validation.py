import pytest
from agentflow.models import AgentResult


def test_invalid_route_combination() -> None:
    with pytest.raises(ValueError):
        AgentResult(status="approved", route="tester")


def test_completed_developer_handoff_to_tester_is_valid() -> None:
    result = AgentResult(status="completed", route="tester")

    assert result.route.value == "tester"
