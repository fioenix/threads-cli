# threads-cli

A clean, agent-friendly CLI for the official **Meta Threads API** (`graph.threads.net`).

- **Humans**: use it as a normal CLI (pipx).
- **Agents** (Claude Code / OpenClaw / others): use it as a deterministic command surface.

> Note: The official Threads API does **not** provide Home / For You / Following feed access.

---

## 1) For humans (CLI users)

### Install

```bash
pipx install threads-cli
threads --help
```

(Dev/editable):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
threads --help
```

### Configure (.env)

Create a local env file (never commit secrets):

```bash
cp .env.example .env
# edit .env
```

Minimum you’ll typically need:

- `THREADS_ACCESS_TOKEN` (long‑lived token)

### Quick sanity check

```bash
threads --env-file .env me
```

### Publish (create → publish)

```bash
threads --env-file .env publish create --media-type TEXT --text "Hello Threads"
# then publish using the returned creation_id:
threads --env-file .env publish publish <creation_id>
```

---

## 2) For agents (Claude Code / OpenClaw / similar)

### Why this repo is agent-friendly

- The CLI is a stable interface (`threads ...`) that maps closely to API endpoints.
- Skill docs are bundled under `skills/threads/` using a minimal, skill-creator style layout.
- The skill is **agent-agnostic**: it works anywhere a tool can run shell commands.

### Install the skill (Skills CLI ecosystem)

```bash
npx skills add fioenix/threads-cli@threads -g -y
```

### Agent execution pattern

Agents should run commands explicitly with `--env-file` and capture JSON output:

```bash
threads --env-file skills/threads/.env me
threads --env-file skills/threads/.env auth-local
```

To create the env file for the skill:

```bash
cp .env.example skills/threads/.env
# edit skills/threads/.env
```

### Safety (publish gate)

When an agent drafts content, treat it as **draft-only** until the user explicitly says publish/đăng bài.

---

## License

MIT — see [LICENSE](./LICENSE).
