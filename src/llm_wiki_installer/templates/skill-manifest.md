# Skill Manifest

Generated: {{TODAY}}

## Canonical Policy

- AGENTS.md is the canonical agent policy.
- This guide is the canonical generation spec.
- Agent adapters are derived outputs.

## Tools

| Tool | Version | Result |
| --- | --- | --- |
| rg | {{RG_VERSION}} | {{RG_RESULT}} |
| fzf | {{FZF_VERSION}} | {{FZF_RESULT}} |

## Upstream Skills

| Repo | Source Type | Pinned Commit SHA | Resolved Commit SHA | License Review | Install Date | Installed Skills | Result |
| --- | --- | --- | --- | --- | --- | ---: | --- |
| <https://github.com/Ar9av/obsidian-wiki> | third-party upstream artifact | {{AR9AV_PINNED_COMMIT}} | {{AR9AV_COMMIT}} | review upstream repository at pinned commit | {{TODAY}} | {{AR9AV_COUNT}} | {{AR9AV_RESULT}} |
| <https://github.com/kepano/obsidian-skills> | third-party upstream artifact | {{KEPANO_PINNED_COMMIT}} | {{KEPANO_COMMIT}} | review upstream repository at pinned commit | {{TODAY}} | {{KEPANO_COUNT}} | {{KEPANO_RESULT}} |

## Obsidian Assets

| Asset | Source Type | Version | Result |
| --- | --- | --- | --- |
| Things theme | bundled Obsidian theme template | 2.2.3 | installed |
| obsidian-git plugin | bundled Obsidian community plugin template | 2.38.3 | installed |

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
- wiki/log.jsonl
- .scripts/postrun.sh
- .scripts/check-index-log.sh
- .obsidian/app.json
- .obsidian/appearance.json
- .obsidian/backlink.json
- .obsidian/community-plugins.json
- .obsidian/core-plugins.json
- .obsidian/graph.json
- .obsidian/hotkeys.json
- .obsidian/plugins/obsidian-git/data.json
- .obsidian/plugins/obsidian-git/main.js
- .obsidian/plugins/obsidian-git/manifest.json
- .obsidian/plugins/obsidian-git/obsidian_askpass.sh
- .obsidian/plugins/obsidian-git/styles.css
- .obsidian/themes/Things/manifest.json
- .obsidian/themes/Things/theme.css
- .codex/config.toml
- .codex/hooks.json
- .agents/skill-manifest.md
- .agents/skill-manifest.json
- .gitignore
