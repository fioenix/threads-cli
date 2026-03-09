# AGENTS.md (for agent runtimes)

This file is for **AI agents** (Claude Code / OpenClaw / similar) operating this repo.
Humans should start with **README.md**.

## What this repo contains

- **CLI**: `threads` (Python package `threads_cli`)
- **Agent skill docs**: `skills/threads/` (skill-creator style: SKILL.md + references + evals)

## Non-goals / constraints

- The official Threads API does **not** provide Home / For You / Following feed access.
- Do not claim feed-reading capabilities.

## Setup (recommended)

Install CLI:

```bash
pipx install threads-cli
threads --help
```

Create env for agent runs:

```bash
cp .env.example skills/threads/.env
# edit skills/threads/.env (never commit)
```

## Execution pattern

Always pass `--env-file` explicitly and keep outputs as JSON:

```bash
threads --env-file skills/threads/.env me
threads --env-file skills/threads/.env auth-local
```

## Safety: publish approval gate (MUST)

Treat requests as **draft-first**.

- “OK / looks good” approves the draft text only.
- Only publish when the user clearly expresses public intent:
  - EN: publish / post it / go live
  - VI: đăng bài / post bài / public lên / đẩy lên

Before publishing, echo the final payload and ask for explicit confirmation.

## Where to read next

- Skill instructions: `skills/threads/SKILL.md`
- Copy/paste commands: `skills/threads/references/cli-cheatsheet.md`
- Setup checklist: `skills/threads/references/setup-meta-app.md`
- Endpoint map: `skills/threads/references/endpoints.md`

## Contributing workflow (agent)

- Keep changes small and reversible.
- Prefer updating references over bloating `SKILL.md` (>500 lines).
- Keep skill bundle minimal (avoid adding scripts/venvs under `skills/threads/`).
- Run CI equivalents locally when possible:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
ruff format .
ruff check .
python -m build
pytest
```
