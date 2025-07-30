# Fauthy Python SDK

## Setup locally

```bash
uv sync
```

## Run tests

```bash
pytest
```

## Add dependencies

```bash
uv add <package_name>
```

Then update `requirements.txt` for Heroku:

```bash
uv pip compile pyproject.toml -o requirements.txt
```