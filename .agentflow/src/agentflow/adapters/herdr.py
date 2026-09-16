import asyncio
import json
import subprocess
from pathlib import Path

from agentflow.agents.base import Agent, AgentContext
from agentflow.models import AgentResult

from .codex import AdapterError, AgentTimeoutError, InvalidAgentResultError


class HerdrAdapter(Agent):
    """Run a persistent Codex agent through a Herdr pane."""

    def __init__(self, pane_id: str, root: Path, timeout: float = 3600) -> None:
        self.pane_id = pane_id.removeprefix("herdr:pane:")
        self.root = root
        self.timeout = timeout

    @staticmethod
    def _result_from_output(output: str) -> AgentResult:
        decoder = json.JSONDecoder()
        latest: AgentResult | None = None
        for index in (i for i, char in enumerate(output) if char == "{"):
            try:
                # Herdr's terminal reader can insert visual line breaks inside
                # long JSON strings. Whitespace is safe to normalize here;
                # Pydantic still performs the authoritative contract check.
                candidate = output[index:].replace("\r", " ").replace("\n", " ")
                value, _ = decoder.raw_decode(candidate)
                latest = AgentResult.model_validate(value)
            except (json.JSONDecodeError, ValueError):
                continue
        if latest is not None:
            return latest
        raise InvalidAgentResultError(
            "Herdr output did not contain a valid AgentResult JSON object"
        )

    def _run(self, prompt: str) -> AgentResult:
        self._submit(prompt)
        try:
            return self._read_result()
        except InvalidAgentResultError:
            repair = (
                "Your previous response did not match the required AgentResult contract. "
                "Reply with ONLY one valid JSON object containing exactly these fields: "
                "status, route, summary, issues, metadata. "
                "Do not include state, changes, verification, markdown, or explanations. "
                "For completed Developer work, use status completed and route tester."
            )
            self._submit(repair)
            return self._read_result()

    def _submit(self, prompt: str) -> None:
        command = [
            "herdr",
            "agent",
            "prompt",
            self.pane_id,
            prompt,
            "--wait",
            "--until",
            "idle",
            "--until",
            "done",
            "--until",
            "blocked",
            "--timeout",
            str(int(self.timeout * 1000)),
        ]
        try:
            subprocess.run(  # noqa: S603 - executable and arguments are controlled
                command, capture_output=True, text=True, check=True
            )
        except subprocess.TimeoutExpired as exc:
            raise AgentTimeoutError(self.pane_id) from exc
        except (OSError, subprocess.CalledProcessError) as exc:
            details = getattr(exc, "stderr", "") or str(exc)
            raise AdapterError(f"Herdr agent failed: {details.strip()}") from exc

    def _read_result(self) -> AgentResult:
        try:
            read = subprocess.run(  # noqa: S603 - executable and arguments are controlled
                [  # noqa: S607 - executable is a controlled Herdr command
                    "herdr",
                    "agent",
                    "read",
                    self.pane_id,
                    "--source",
                    "recent-unwrapped",
                    "--lines",
                    "1000",
                    "--format",
                    "text",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
        except subprocess.TimeoutExpired as exc:
            raise AgentTimeoutError(self.pane_id) from exc
        except (OSError, subprocess.CalledProcessError) as exc:
            details = getattr(exc, "stderr", "") or str(exc)
            raise AdapterError(f"Herdr agent failed: {details.strip()}") from exc
        return self._result_from_output(read.stdout)

    async def run(self, context: AgentContext) -> AgentResult:
        role = {"development": "developer", "testing": "tester", "review": "reviewer"}[
            context.state
        ]
        handoff = {
            "development": "completed work must use status completed and route tester",
            "testing": (
                "a passing test run must use status completed and route reviewer; "
                "only test work still needed may use status changes_required and route tester"
            ),
            "review": (
                "approval must use status approved and route done; "
                "package-by-feature structure is mandatory, and a non-trivial feature "
                "must not combine repository, service, DTO, mapper, serializer, and "
                "controller code in one file; use singular responsibility filenames such as "
                "controller.py when there is one controller, not controllers.py"
            ),
        }[context.state]
        role_contract = {
            "developer": (
                "You own production code only. Do not create, edit, or delete tests. "
                "Use package-by-feature with errors.py, repository.py, service.py, dto.py, "
                "mapper.py, serializer.py, controller.py, and urls.py as applicable. "
                "Exceptions belong in errors.py. Finish with completed/tester."
            ),
            "tester": (
                "You own tests, fixtures, and coverage only. Do not modify production code "
                "and do not perform the Reviewer's architecture approval. Verify the feature "
                "and report production defects to developer. Pass with completed/reviewer."
            ),
            "reviewer": (
                "You are the final source-level reviewer. Do not modify code or tests. Inspect "
                "the actual changed files, including errors.py, DTO ownership, singular module "
                "names, service/repository boundaries, and exception messages. Never trust "
                "previous summaries. Approve only when every rule is verified."
            ),
        }[role]
        prompt = (
            f"You are the {role} agent. {role_contract}\n\n"
            f"Task JSON: {context.task.model_dump_json()}. "
            f"Return ONLY AgentResult JSON. State: {context.state}. "
            f"Handoff rule: {handoff}. "
            f"Recent findings: {[item.model_dump() for item in context.findings[-3:]]}"
        )
        return await asyncio.wait_for(asyncio.to_thread(self._run, prompt), self.timeout)
