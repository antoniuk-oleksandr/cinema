# Cinema project agent instructions

This repository uses three OpenClaw agents with Codex as the coding runtime:

- Developer: `.openclaw/roles/developer.md`
- Tester: `.openclaw/roles/tester.md`
- Reviewer: `.openclaw/roles/reviewer.md`

Read the role file matching your assigned agent before every task. All agents
share this working tree and must follow the existing project architecture,
configuration, migration, API, observability, documentation, and safety rules.

The `main` OpenClaw agent is the supervisor. It is the only agent that decides
which role runs next. Use one OpenClaw native persistent task session for the
entire workflow; do not create another Python or shell orchestrator.

The workflow is strictly sequential:

```text
Developer -> Tester -> Reviewer -> Done
                 ^          |
                 |----------+
```

The Developer owns production code. The Tester owns tests and coverage. The
Reviewer diagnoses and routes findings but does not modify production code or
tests. Never approve a production change without a successful Tester pass.

## Handoff protocol

Every role must return one JSON object with exactly these fields:

```json
{"status":"completed|changes_required|approved|blocked|error","route":"developer|tester|reviewer|both|done|human_required","summary":"...","issues":[],"metadata":{}}
```

The reviewer must classify every finding with `type: "production"` or
`type: "testing"`. Use `route: "both"` only when both categories are present.
The supervisor must pass the reviewer's complete `issues` array verbatim to the
next role, together with a short instruction describing that role's ownership.

Routing is mandatory:

- Developer completed -> Tester.
- Tester finds a production issue -> Developer -> Tester.
- Tester finds a test or coverage issue -> Tester again.
- Tester passes -> Reviewer.
- Reviewer finds production issues -> Developer -> Tester -> Reviewer.
- Reviewer finds testing issues -> Tester -> Reviewer.
- Reviewer finds both -> Developer -> Tester -> Reviewer.
- Reviewer approved -> Done.

Never route Reviewer directly to Reviewer after production changes. Never let
the Reviewer edit source or tests. Do not treat a prose response, a tool log,
or a claim of passing tests as a valid handoff unless the final JSON validates
against the contract above. If a role is blocked or returns malformed output,
stop and report the task as human-required.

For each task, include the feature Markdown path or full feature text, the
current route, the previous result, and only the relevant accumulated findings.
Do not repeatedly paste the entire conversation or unrelated role history.
Before spawning a role, inspect existing background tasks. Reuse an already
running worker for the same feature instead of spawning a duplicate. New
workers must use a unique feature-and-attempt label; never reuse a fixed label.

Task-session policy: create exactly one persistent child session when a new
user task begins. That same session must receive every stage handoff for that
task through `sessions_send`: Developer, Tester, Reviewer, and corrections.
Do not create separate Developer, Tester, or Reviewer sessions. Create one
new task session only for a new user task or an explicit task-session reset.
Never use `sessions_spawn` for a later stage, retry, or Reviewer correction.

Do not commit, merge, reset Git history, delete source files, or force-push.
Do not implement features outside the submitted task.
