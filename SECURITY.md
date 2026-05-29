# Security Policy

## Supported Versions

Security fixes are applied to the `main` branch until formal releases are
published.

## Reporting A Vulnerability

Do not open a public issue with exploit details. Use GitHub private
vulnerability reporting when it is enabled for the repository. If it is not
enabled, open a minimal issue asking for a private maintainer contact and omit
the vulnerability details until a private channel is available.

Include:

- Affected version or commit.
- Steps to reproduce.
- Impact and expected behavior.
- Any relevant logs, generated files, or environment details.

Maintainers should acknowledge the report, investigate, prepare a fix when
needed, and publish a public advisory or release note after users have a
reasonable upgrade path.

## Security Scope

The most important security-sensitive areas are:

- `install.sh`, especially streamed install behavior.
- Any command execution in `src/llm_wiki_installer/`.
- GitHub and npm network bootstrapping.
- Generated shell scripts under `src/llm_wiki_installer/templates/`.
- Template rendering and target path safety checks.

Never commit secrets, tokens, private machine paths, or user-specific
configuration.
