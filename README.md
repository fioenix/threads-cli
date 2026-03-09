# threads-cli

CLI for the official Meta Threads API (graph.threads.net).

## Install (CLI)

Recommended:

```bash
pipx install threads-cli
threads --help
```

Or (dev/editable):

```bash
python -m pip install -e '.[dev]'
threads --help
```

## Configure

Create an env file (do **not** commit it):

- `skills/threads/.env` (when using the OpenClaw skill)

Required:

- `THREADS_ACCESS_TOKEN` (long-lived token)

## Usage

Pass env file explicitly:

```bash
threads --env-file skills/threads/.env me
threads --env-file skills/threads/.env publish create --media-type TEXT --text 'hello'
```

Also works:

```bash
python -m threads_cli --env-file skills/threads/.env me
```

## OpenClaw Skill install

This repo includes an OpenClaw skill at `skills/threads/`.

```bash
npx skills add fioenix/threads-cli@threads -g -y
```

## License

MIT — see [LICENSE](./LICENSE).
