# Contributing

Thanks for contributing!

## Dev setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e '.[dev]'
ruff format .
ruff check .
pytest
```

## Style

- Use `ruff format` + `ruff check`.
- Prefer small PRs with clear descriptions.
