# OpenClaw project setup

This directory contains the project-owned OpenClaw instructions. The role
files and workflow are safe to commit and are shared by the team.

OpenClaw itself stores machine-specific configuration in
`~/.openclaw/openclaw.json`. Start from `openclaw.example.json`, replace every
`/absolute/path/to/cinema` with the local checkout path, and merge it into the
local configuration. Do not commit that personal configuration: it can contain
OAuth credentials, Slack tokens, machine paths, and session state.

## First-time setup

From the repository root:

```bash
openclaw plugins enable codex
openclaw gateway install
openclaw gateway start
```

Authenticate Codex with the local Codex/OpenAI login available on your
machine. Slack is optional; configure it only when Slack notifications are
needed. Never put Slack or OpenAI tokens in this repository.

The `main` agent supervises one persistent task session. That same session
receives the Developer, Tester, and Reviewer stages for the task. A new task
gets a new task session.

Project instructions are loaded from:

- `AGENTS.md`
- `OPENCLAW_WORKFLOW.md`
- `.openclaw/roles/developer.md`
- `.openclaw/roles/tester.md`
- `.openclaw/roles/reviewer.md`

Inspect the installation with:

```bash
openclaw status
openclaw agents list
openclaw channels status --probe
```
