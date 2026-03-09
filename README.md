# threads-cli

A clean CLI for the official **Meta Threads API** (`graph.threads.net`).

> Note: The official Threads API does **not** provide Home / For You / Following feed access.

## Install

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

## Configure (.env)

Create a local env file (never commit secrets):

```bash
cp .env.example .env
# edit .env
```

Minimum you’ll typically need:

- `THREADS_ACCESS_TOKEN` (long‑lived token)

## Quick sanity check

```bash
threads --env-file .env me
```

## Publish (create → publish)

```bash
threads --env-file .env publish create --media-type TEXT --text "Hello Threads"
# then publish using the returned creation_id:
threads --env-file .env publish publish <creation_id>
```

## For AI agents

See **AGENTS.md**.

## License

MIT — see [LICENSE](./LICENSE).
