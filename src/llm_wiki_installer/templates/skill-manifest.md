# Skill Manifest

Generated: {{TODAY}}

## Canonical Policy

- AGENTS.md is the canonical agent policy.
- This guide is the canonical generation spec.
- Agent adapters are derived outputs.

## qmd

| Field | Value |
| --- | --- |
| Source | <https://github.com/tobi/qmd> |
| Package | @tobilu/qmd |
| Install Command | npm install -g @tobilu/qmd |
| Result | {{QMD_RESULT}} |
| Version | {{QMD_VERSION}} |
| Node Version | {{NODE_VERSION}} |
| npm Version | {{NPM_VERSION}} |
| Collection | knowledge-vault |
| Collection Path | {{TARGET}} |
| Indexed Scope | repository root |

## Tools

| Tool | Version | Result |
| --- | --- | --- |
| qmd | {{QMD_VERSION}} | {{QMD_RESULT}} |
| rg | {{RG_VERSION}} | {{RG_RESULT}} |
| fzf | {{FZF_VERSION}} | {{FZF_RESULT}} |

## Upstream Skills

| Repo | Source Type | Pinned Commit SHA | Resolved Commit SHA | License Review | Install Date | Installed Skills | Result |
| --- | --- | --- | --- | --- | --- | ---: | --- |
| <https://github.com/Ar9av/obsidian-wiki> | third-party upstream artifact | {{AR9AV_PINNED_COMMIT}} | {{AR9AV_COMMIT}} | review upstream repository at pinned commit | {{TODAY}} | {{AR9AV_COUNT}} | {{AR9AV_RESULT}} |
| <https://github.com/kepano/obsidian-skills> | third-party upstream artifact | {{KEPANO_PINNED_COMMIT}} | {{KEPANO_COMMIT}} | review upstream repository at pinned commit | {{TODAY}} | {{KEPANO_COUNT}} | {{KEPANO_RESULT}} |

## llm-wiki Installer

| Field | Value |
| --- | --- |
| Name | {{INSTALLER_NAME}} |
| Version | {{INSTALLER_VERSION}} |
| Role | setup wrapper / generator suite |
| Runtime Coordinator | AGENTS.md |
| Project-Owned Skill | not generated |

## Generated Files

- AGENTS.md
- README.md
- wiki/index.md
- wiki/log.md
- .scripts/postrun.sh
- .scripts/check-index-log.sh
- .codex/config.toml
- .agents/skill-manifest.md
- .agents/skill-manifest.json
- .gitignore
