# Contributing

Thanks for helping improve `llm-wiki-installer`. This repository builds the
installer; it is not a generated vault. Keep changes focused on the generator,
templates, docs, or tests.

## Development Setup

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pip install --no-build-isolation --no-deps -e .
```

Install the optional local hooks after setup:

```bash
.venv/bin/pre-commit install
```

## Before Opening A Pull Request

Run the narrowest meaningful checks while developing, then run the full stack
before review:

```bash
make verify
```

For Python-only changes, `make lint`, `make typecheck`, and `make test` are the
minimum useful checks. For installer launcher, templates, generated scripts,
tool checks, upstream Skill installation, or target layout changes,
run `make verify`.

## Generated Contract Changes

When a change affects generated vault behavior:

- Update the relevant template in `src/llm_wiki_installer/templates/`.
- Update `docs/technical-design.md` or `docs/llm-wiki-generation-guide.md` if
  the contract changed.
- Update unit tests and the shell integration harness for the new contract.
- Do not create generated vault artifacts in this repository root.

## Pull Request Checklist

- The change is scoped and has tests for changed behavior.
- Generated behavior, docs, templates, and tests stay aligned.
- `make verify` passes, or the PR clearly explains any local blocker.
- No secrets, private machine paths, build artifacts, or generated vault output
  are committed.

## Release Publishing

Release tags use `.github/workflows/release.yml` to build the source
distribution and wheel, smoke test both console entry points, upload GitHub
Release artifacts, and publish to PyPI with Trusted Publishing.

The project is published on PyPI as
[`llm-wiki-installer`](https://pypi.org/project/llm-wiki-installer/). Users can
run a release directly with:

```bash
uvx llm-wiki-installer /path/to/knowledge-vault
uvx llm-wiki-installer==<version> --dry-run --json /path/to/knowledge-vault
```

The package version is sourced from `src/llm_wiki_installer/__init__.py`; do not
add a second literal version in `pyproject.toml`.

GitHub release notes are generated from merged pull requests using
`.github/release.yml`. Keep PR labels meaningful so release notes stay useful.

The PyPI project `llm-wiki-installer` is configured with this GitHub Actions
trusted publisher:

- owner: `exhank`
- repository: `llm-wiki-installer`
- workflow: `release.yml`
- environment: `pypi`

The release workflow intentionally publishes without a PyPI API token. For
future releases, keep the build job separate from the PyPI publish job, keep
`id-token: write` scoped to the jobs that need OIDC, and verify both the GitHub
Release and PyPI project page after a tag publish completes.
