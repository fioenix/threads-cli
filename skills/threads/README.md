# threads (Skill)

Agent-agnostic skill docs for operating the official Meta Threads API.

- Works with **any agent runtime** (OpenClaw, Claude Code, etc.)
- Uses the `threads-cli` Python CLI shipped in this repo

## Install the CLI

```bash
pipx install threads-cli
threads --help
```

## Configure

Create a local env file:

```bash
cp skills/threads/.env.example skills/threads/.env
# edit skills/threads/.env
```

## Run

```bash
threads --env-file skills/threads/.env me
threads --env-file skills/threads/.env auth-local
```

For full CLI command reference, see the repo root README.
