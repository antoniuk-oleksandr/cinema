import argparse
import asyncio
from pathlib import Path

from agentflow.agents.mock import MockAgent
from agentflow.config import Config
from agentflow.models import AgentResult, Task
from agentflow.orchestrator import Orchestrator
from agentflow.session_store import SessionStore

ROOT = Path(__file__).resolve().parents[2]


def run(feature=None, task=None):
    text = task or (feature.read_text() if feature else "")
    title = feature.stem if feature else "Ad hoc feature"
    t = Task(title=title, description=text)
    from agentflow.adapters.codex import CodexAdapter
    from agentflow.adapters.herdr import HerdrAdapter

    sessions = SessionStore(ROOT / "runtime/sessions.json").load()
    timeout = Config.load(ROOT / "config/config.toml").pipeline.agent_timeout_seconds
    agents = {
        n: (
            HerdrAdapter(sessions[n], timeout)
            if sessions[n] and sessions[n].startswith("herdr:pane:")
            else CodexAdapter(n, ROOT, timeout, sessions[n])
        )
        for n in ("developer", "tester", "reviewer")
    }
    return asyncio.run(
        Orchestrator(t, agents, ROOT, Config.load(ROOT / "config/config.toml")).run()
    )


def mock(scenario="happy") -> None:

    def r(status, route, summary="mock"):
        return AgentResult(status=status, route=route, summary=summary)

    scenarios = {
        "happy": (
            [r("completed", "tester")],
            [r("completed", "reviewer")],
            [r("approved", "done")],
        ),
        "production": (
            [r("completed", "tester"), r("completed", "tester")],
            [r("changes_required", "developer"), r("approved", "done")],
            [r("completed", "reviewer")],
        ),
        "tests": (
            [r("completed", "tester")],
            [r("completed", "reviewer"), r("completed", "reviewer")],
            [r("changes_required", "tester"), r("approved", "done")],
        ),
        "both": (
            [r("completed", "tester")],
            [r("completed", "tester")],
            [r("changes_required", "both"), r("approved", "done")],
        ),
    }
    d, tv, rv = scenarios.get(scenario, scenarios["happy"])
    agents = {
        "developer": MockAgent("developer", d),
        "tester": MockAgent("tester", tv),
        "reviewer": MockAgent("reviewer", rv),
    }
    print(asyncio.run(Orchestrator(Task(title="mock"), agents, ROOT).run()).value)


def doctor() -> None:
    import shutil

    print(
        f"python: ok\ncodex: {'found' if shutil.which('codex') else 'missing'}\nherdr: {'found' if shutil.which('herdr') else 'missing'}"
    )


def setup() -> None:
    from agentflow.adapters.herdr_provision import HerdrProvisioner, HerdrProvisionError

    try:
        sessions = HerdrProvisioner(ROOT).provision()
    except HerdrProvisionError as exc:
        print(f"Herdr setup failed: {exc}")
        raise SystemExit(2) from exc
    print("Persistent Herdr agents ready:")
    for role, session_id in sessions.items():
        print(f"  {role}: {session_id}")


def status() -> None:
    p = ROOT / "runtime/current_run.json"
    print(p.read_text() if p.exists() else "No current run")


def reset() -> None:

    p = ROOT / "runtime"
    [x.unlink() for x in p.glob("*.json*")] if p.exists() else None
    print("Runtime state reset")


def main() -> None:
    p = argparse.ArgumentParser(prog="agentflow")
    sub = p.add_subparsers(dest="command")
    r = sub.add_parser("run")
    r.add_argument("feature", nargs="?")
    r.add_argument("--task")
    m = sub.add_parser("mock")
    m.add_argument("--scenario", default="happy")
    sub.add_parser("doctor")
    sub.add_parser("setup")
    sub.add_parser("status")
    sub.add_parser("reset")
    a = p.parse_args()
    if a.command == "run":
        state = run(Path(a.feature) if a.feature else None, a.task)
        print(f"Agentflow finished with state: {state.value}")
        raise SystemExit(0 if state.value == "done" else 2)
    if a.command == "mock":
        mock(a.scenario)
    elif a.command == "doctor":
        doctor()
    elif a.command == "setup":
        setup()
    elif a.command == "status":
        status()
    elif a.command == "reset":
        reset()
    else:
        p.print_help()


if __name__ == "__main__":
    main()
