# OpenClaw workflow

Use the `main` agent as the supervisor for feature work in this repository.
The `main` agent supervises one persistent child session per user task. The
same child session performs the Developer, Tester, and Reviewer stages in
sequence and uses the same working tree at `/home/alex/projects/cinema`.

When the user submits a feature, execute this loop through native OpenClaw
agent/session tools:

Create exactly one persistent visible child session only when a genuinely new
user task starts. Give it a unique task label such as
`cinema-<feature>-<attempt>`, and create it with `mode: "session"`, not
`mode: "run"`. Store or discover its session key through OpenClaw's session
tools.

After the task session exists, never call `sessions_spawn` for a route within
the same task. Use `sessions_send` to that same task session instead. This
includes retries, Reviewer-to-Developer corrections, Tester self-retries, and
re-reviews. A new child session is allowed only after the user submits a new
feature task or explicitly asks to reset the current task session.

Before sending a handoff, inspect the current task/session list. If the task
session is busy, wait for its completion event; do not create a duplicate.

1. Send the feature and `developer.md` instructions to the task session with
   the explicit role `developer`.
2. Send the developer result and any production findings to the same task
   session with the explicit role `tester`.
3. If Tester reports a production defect, send only that defect to the same
   task session with the explicit role `developer`,
   then run Tester again.
4. If Tester reports a test/coverage defect, send it to the same task session
   again with the explicit role `tester`.
5. When Tester passes, send the feature, implementation summary, Tester result,
   and prior review findings to the same task session with the explicit role
   `reviewer`.
6. Route Reviewer findings exactly as follows:
   - production -> developer -> tester -> reviewer
   - testing -> tester -> reviewer
   - both -> developer -> tester -> reviewer
   - approved/done -> finish

The reviewer is a routing authority, not an implementation worker. It must
return concrete issues with file paths, symbols, evidence, and a requested
owner. The supervisor must forward those issues unchanged to the owning role.
Do not ask the Developer to write tests or the Tester to modify production
code. Do not ask the Reviewer to modify either.

Every handoff must end with exactly one JSON object matching the contract in
`AGENTS.md`. Do not use prose or terminal output for routing. If a role needs
approval, becomes blocked, times out at the OpenClaw runtime level, or returns
invalid JSON, stop with a human-required result and preserve the transcript.

Keep handoffs compact: include the feature path/text, current state, previous
result, and relevant findings. Do not paste the full conversation repeatedly.

Suggested supervisor request:

> Implement `<feature-file-or-request>` in `/home/alex/projects/cinema`.
> Run the Developer → Tester → Reviewer workflow from `OPENCLAW_WORKFLOW.md`.
> Continue routing reviewer findings until approved. Do not stop after a
> successful Developer or Tester result.
