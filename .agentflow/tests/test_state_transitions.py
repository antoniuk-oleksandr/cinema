import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))
from agentflow.models import AgentResult


def test_result_contract() -> None:
    assert AgentResult(status="approved", route="done").route.value == "done"
    try:
        AgentResult(status="approved", route="tester")
    except ValueError:
        pass
    else:
        raise AssertionError("invalid result was accepted")
