# LLM-Native Obsidian PKB Technical Design

Verification date: 2026-05-28

This design uses Karpathy's LLM Wiki as the primary methodology. It treats an Obsidian Markdown repository as a long-lived knowledge system that LLMs continuously compile, retrieve, review, and write back to. Obsidian is only the Markdown IDE / viewer, not the architectural source of truth. Git is the rollback boundary. The Agent Harness is the execution boundary. `raw/` and `wiki/` together form the knowledge source of truth.

---

## 1. Current Recommendation

Core flow:

```text
capture -> inbox -> raw -> wiki -> query -> fileback -> review -> export/archive
```

Core layers:

```text
inbox/    = unprocessed input buffer; agents may write here
raw/      = user-approved source evidence layer; read-only for agents by default
wiki/     = long-term Markdown Wiki compiled by LLMs
outputs/  = current deliverables, exports, and externally facing artifacts
archive/  = old outputs archive; not a knowledge archive
AGENTS.md = repository-level canonical agent policy
.agents/  = project-local selected skills and skill manifest
.codex/   = Codex adapter / hooks; does not carry long-term rules
.scripts/ = fixed project scripts
.obsidian/ = stable Obsidian settings, pinned plugin assets, and theme files
```

Core principle:

```text
Keep the top level constrained; let wiki evolve internally.
```

Top-level directories should only express evidence boundaries, compilation boundaries, processing state, deliverable state, and execution constraints. The internal structure of `wiki/` should not be locked in prematurely; LLMs should progressively create pages or subdirectories from real content within a clear task scope.

---

## 2. Design Goals

This system is not ordinary note categorization, and it is not one-off RAG Q&A. Its goal is:

```text
Enable agents to compile approved raw sources into a continuously maintained, queryable, auditable, and rollbackable Markdown Wiki.
```

The design must satisfy:

1. **Long-term stability**: File and directory rules are clear and do not depend on private Obsidian capabilities.
2. **LLM friendliness**: Agents can quickly understand entry points, boundaries, retrieval order, and write rules.
3. **Traceable evidence**: Original sources live in `raw/`, long-term conclusions live in `wiki/`, and important judgments can be traced back.
4. **Reviewability**: All writes are reviewed through Git diff, logs, postrun checks, and index/log consistency checks.
5. **Compounding value**: High-value answers are written back to the wiki instead of disappearing into chat history.
6. **Repeatable artifacts**: Setup, rules, scripts, manifest, selected or skipped upstream versions, and diff output must be reviewable.

---

## 3. Architecture Model

LLM Wiki analogy:

| Software engineering concept | Equivalent in this system |
| --- | --- |
| source code | original sources in `raw/` |
| compiler | agents such as Codex / Claude Code / Gemini CLI / OpenCode |
| compiled output | long-term Markdown pages, maps, index, and log in `wiki/` |
| runtime | wiki-first query workflow |
| tests | postrun, index/log check, dead-link check, Git diff review |
| schema | `AGENTS.md`, Skill manifest, hooks, scripts |
| rollback | Git branch, diff, restore, revert |

Difference from traditional RAG:

```text
Traditional RAG: retrieve raw chunks at query time -> assemble answer -> answer stays in chat history
LLM Wiki: raw is compiled into wiki first -> queries read wiki first -> good answers file back -> wiki compounds over time
```

Primary source of truth:

```text
truth source = raw/ + wiki/
retrieval accelerator = wiki/index.md + wiki/maps/ + rg + fzf
```

---

## 4. Directory Structure

```text
./
├─ inbox/                       # unprocessed input; low-friction capture buffer; agents may write
├─ raw/                         # user-approved original sources; immutable evidence layer; read-only for agents by default
├─ wiki/                        # long-term Markdown Wiki compiled by LLMs
│  ├─ maps/                     # topic entry points: MOC / Topic Map / Project Map / Learning Map
│  ├─ index.md                  # global machine/human entry point; maintained automatically by agents
│  └─ log.md                    # append-only compilation and change ledger
├─ outputs/                     # current final deliverables, exports, externally facing artifacts
├─ archive/                     # old outputs that are not currently needed; not a knowledge archive
├─ AGENTS.md                    # repository-level canonical agent policy
├─ README.md                    # human entry point: operations guide, design idea, directory explanation
├─ .agents/
│  ├─ skills/
│  │  └─ upstream/              # selected upstream skills, namespaced by source repo
│  ├─ skill-manifest.md         # human-readable version pins, install state, skipped records
│  └─ skill-manifest.json       # machine-readable version pins, install state, skipped records
├─ .codex/
│  ├─ hooks/                    # LLM hook triggers; does not carry long-term rules
│  └─ config.toml               # Codex adapter config
├─ .scripts/                    # fixed project scripts
└─ .gitignore
```

Do not create:

```text
.codex/rules/
projects/
areas/
resources/
core/
work/
_agent/
.cache/agents/
tests/
fixtures/
examples/
```

`tests/`, `fixtures/`, and test artifacts may only be generated temporarily during setup. They must be deleted after success and must not remain in the final repository.

---

## 5. Directory Responsibilities and Lifecycles

| Path | Responsibility | Agent permission | Lifecycle |
| --- | --- | --- | --- |
| `inbox/` | unprocessed input, temporary capture, material awaiting judgment | may add and organize | may be cleaned; may move into raw/wiki |
| `raw/` | user-approved original evidence | read-only by default; deletable only with user authorization | immutable by default; tracked by Git by default |
| `wiki/` | long-term knowledge layer compiled by LLMs | may write autonomously within clear scope | long-term maintenance; continuous evolution |
| `wiki/maps/` | topic entry points; does not copy body text | writable | evolves with topics |
| `wiki/index.md` | global entry point for machines and humans | maintained automatically by agents | must remain consistent with wiki discoverability |
| `wiki/log.md` | append-only compilation and change ledger | append-only | audit record; does not replace Git log |
| `outputs/` | current deliverables | writable within a clear task | regenerable; archivable |
| `archive/` | cold storage for old outputs | writable within a clear archive task | does not carry knowledge structure |
| `.agents/skills/upstream/` | selected upstream Skills, namespaced by source repo | maintained by setup | recorded by manifest |
| `.agents/skill-manifest.md` | selected upstream versions, skipped records, and generated artifacts lockfile | maintained by setup | updated on every setup/update |
| `.agents/skill-manifest.json` | machine-readable mirror of installer, tool, upstream pin, and generated artifact state | maintained by setup | updated on every setup/update |
| `.codex/hooks/` | LLM hook triggers | maintained by adapter | does not carry long-term rules |
| `.scripts/` | general project scripts | maintained by setup | reviewable and testable |
| `.obsidian/` | stable Obsidian settings, pinned community plugin assets, and theme files | maintained by setup | workspace state remains ignored |

Before adding a new top-level directory, all conditions must hold:

```text
1. It has an independent lifecycle.
2. It has an independent permission boundary.
3. It has independent cleanup / archive rules.
4. It cannot be expressed by wiki/maps/.
```

---

## 6. Input, Compilation, and Feedback Rules

### 6.1 Capture: External Input Goes to inbox First

Default flow:

```text
external web page / PDF / image / meeting note / idea / AI draft -> inbox/
```

Agents may write to `inbox/` for low-friction capture and temporary organization.

### 6.2 inbox -> raw

`inbox/ -> raw/` is not an automatic agent behavior. It can only be triggered by:

```text
1. The user manually moving the material.
2. The user explicitly asking the LLM to approve a specific inbox item into raw/.
```

Entering `raw/` means the material has become an approved original source. `raw/` is tracked by Git by default.

### 6.3 raw -> wiki

`raw/ -> wiki/` is an autonomous LLM compilation responsibility, but it must have a clear scope.

Allowed scopes:

```text
user-specified raw file
user-specified raw directory
user-specified topic ingest task
follow-up compilation task after a user-triggered inbox -> raw action
user-explicit wiki ingest / rebuild / lint task
```

Forbidden:

```text
whole-vault recompilation with no task, no scope, and no review
automatically writing external material directly into raw/
automatically modifying raw/
automatically deleting raw/
```

### 6.4 outputs -> inbox -> wiki

`outputs/` is not the wiki source of truth. If old reports, exports, or deliverables need to flow back into the wiki, they must go through:

```text
outputs/ -> inbox/ -> review -> wiki/
```

This prevents final deliverables from back-contaminating the long-term knowledge layer.

---

## 7. raw Boundary

`raw/` is the approved original evidence layer.

Rules:

```text
raw/ is not modified by default
raw/ is not deleted by default
raw/ is not added by agents by default
raw/ is not moved by agents by default
raw/ does not receive automatic capture/import by default
```

Exceptions:

```text
After explicit user authorization, agents may delete specified raw files.
After an explicit user trigger, agents may move specified inbox items into raw/.
All raw deletions / moves must be written to wiki/log.md.
```

Large files in `raw/` are tracked by Git by default. If repository size becomes a problem later, introduce Git LFS or an external storage manifest then; do not make the starter version complex prematurely.

---

## 8. wiki Compilation Layer

`wiki/` is the main body of the system. It is not a temporary scratchpad and not a single-file note dump.

Only this structure is fixed at startup:

```text
wiki/
├─ maps/
├─ index.md
└─ log.md
```

Agents may create pages or subdirectories under `wiki/`, but the content must satisfy:

```text
1. It has a clear topic, question, or long-term reuse value.
2. It is not a mechanical copy of raw.
3. It is not a one-off chat answer unless it will be reusable later.
4. Important facts, judgments, inferences, conflicts, and outdated information are clearly expressed.
5. It can be discovered from wiki/index.md or a map.
6. Meaningful writes must append wiki/log.md.
```

The internal structure of `wiki/` should evolve naturally from content under LLM guidance. This technical design does not predefine a fixed taxonomy.

---

## 9. index, maps, log

### 9.1 `wiki/index.md`

`index.md` is the global entry point, not a pretty homepage.

Purpose:

```text
Let agents read the index first, then decide which maps/pages to read.
Let humans quickly see the core pages in the wiki.
Avoid whole-vault search for every query.
```

Agents maintain `wiki/index.md` automatically.

Update triggers:

```text
new wiki page
deleted wiki page
moved / renamed wiki page
new / deleted important map
important page status change
important wiki structure change
```

### 9.2 `wiki/maps/`

`maps/` contains topic entry points.

Boundary:

```text
index = global entry point
map   = topic entry point
```

Maps may express project views, topic views, learning paths, research paths, and source navigation. They must not copy body text, become a second index, or replace a task management system.

### 9.3 `wiki/log.md`

`log.md` is an append-only ledger. It does not replace Git log.

Only meaningful events are recorded:

```text
ingest
fileback
important query with writes
wiki structure change
index update
map update
schema / script / skill update
outputs export
outputs archive
file deletion / move / rename
major review
```

Ordinary read-only queries do not write to the log.

---

## 10. Log Entry Schemas

### 10.1 Delete File

```md
- type: delete
  scope: path/to/file.md
  reason: "Why this file is safe to delete."
  authorized_by: user | explicit-task
  review: self-reviewed
  impact:
    index_updated: true | false | not-needed
    references_checked: true | false
  files:
    - path/to/file.md
```

### 10.2 Move / Rename File

```md
- type: move
  scope: old/path.md -> new/path.md
  reason: "Why this move is needed."
  authorized_by: user | explicit-task
  review: self-reviewed
  impact:
    index_updated: true | false | not-needed
    references_checked: true | false
  files:
    - old/path.md
    - new/path.md
```

### 10.3 wiki Compilation

```md
- type: ingest
  scope: raw/source.pdf -> wiki/page.md
  reason: "Compiled durable knowledge from raw source."
  review: self-reviewed
  impact:
    index_updated: true
    references_checked: true
  files:
    - raw/source.pdf
    - wiki/page.md
    - wiki/index.md
```

### 10.4 outputs Archive

```md
- type: archive-output
  scope: outputs/report-v1.md -> archive/report-v1.md
  reason: "Old deliverable no longer active."
  review: self-reviewed
  impact:
    index_updated: not-needed
    references_checked: true
  files:
    - outputs/report-v1.md
    - archive/report-v1.md
```

---

## 11. Markdown and Metadata Rules

Long-term knowledge files should prefer GFM-compatible Markdown:

```text
standard Markdown headings
standard Markdown links
tables
task lists
code blocks
YAML frontmatter
```

Do not depend on Obsidian plugins or private syntax as the only representation.

Recommended minimal frontmatter:

```yaml
---
title: ""
type: source | entity | concept | comparison | synthesis | question | map | decision | playbook | note
tags: []
created: 2026-05-28
updated: 2026-05-28
---
```

Put complex source information in body sections such as `Sources` / `Evidence`; do not pile up complex nested metadata.

Important content must distinguish:

```text
facts
inferences
opinions
conflicts
outdated information
to-be-verified items
```

---

## 12. Agent Harness Boundary

The goal of the Agent Harness:

```text
Allow AI to participate aggressively in wiki compilation, while using engineering boundaries to prevent it from polluting raw, creating unreviewable large diffs, or generating unreproducible setup results.
```

Rule source priority:

```text
AGENTS.md > llm-wiki generation guide > upstream skills > adapter hooks/config > one-off task prompt
```

Cross-agent principles:

```text
AGENTS.md is the canonical agent policy.
The llm-wiki generation guide is the canonical generation spec.
Codex / Claude / Gemini / OpenCode adapters are derived artifacts.
Adapters must not become the rule source in reverse.
```

Default write boundaries:

```text
Agents may write inbox/.
Agents may write wiki/ within a clear scope.
Agents may automatically maintain wiki/index.md.
Agents may append wiki/log.md.
Agents may write outputs/ within a clear task.
Agents may write archive/ within a clear archive task.
Agents may maintain .agents/skill-manifest.md, .scripts/, .codex/hooks/, and .codex/config.toml.
Agents may maintain generated .obsidian settings and pinned asset templates when the generator contract changes.
Agents may not write raw/ by default.
Agents may not create .codex/rules/.
Agents may not create ad hoc Obsidian plugin directories outside generated, pinned assets.
```

Deletion boundaries:

```text
Agents may delete / move / rename files only with user authorization or a clear task requirement.
Deleting / moving / renaming any file must append wiki/log.md.
Deletes / moves / renames that affect wiki discoverability must also update wiki/index.md.
```

---

## 13. Retrieval Layer

Selectable retrieval tools:

```text
ripgrep = fast full-text search
fzf     = interactive fuzzy selection
```

Interactive setup presents rg and fzf in a default-all selector. Up/Down moves,
Space toggles, and Enter accepts. Non-interactive setup uses the all-selected
default. Skipped tools are recorded in `.agents/skill-manifest.md`.

Upstream Skill sources are installed from release-pinned commit SHAs, not from
mutable branch tips. The generated Markdown and JSON manifests record the pinned
commit, resolved commit, install result, and installed Skill count for each
source.

Retrieval order:

```text
1. wiki/index.md
2. relevant wiki/maps/
3. relevant wiki pages
4. rg / fzf
5. raw/ verification when needed
```

Tool positioning:

| Tool | Role | Is not |
| --- | --- | --- |
| `wiki/index.md` | global entry point | pretty homepage |
| `wiki/maps/` | topic entry points | top-level classification directories |
| `rg` | fast full-text search | semantic understanding |
| `fzf` | interactive selection | source of truth |

Do not install, require, or include in this design:

```text
Dataview
Omnisearch
Obsidian Bases automation
Canvas automation
.obsidian/workspace.json
.obsidian/workspaces.json
```

---

## 14. Core Workflows

### 14.1 Capture

```text
external input -> inbox/
```

Agents may write high-value chat material, links to process, and text to organize into `inbox/`.

### 14.2 Review to raw

```text
inbox/ -> raw/
```

This is triggered by the user or performed manually. After entering `raw/`, the material becomes part of the evidence layer.

### 14.3 Ingest

```text
raw/source -> wiki/page.md
```

LLMs compile autonomously within a clear scope and update these files when needed:

```text
wiki/index.md
wiki/maps/*
wiki/log.md
```

### 14.4 Query

```text
read index -> read maps/pages -> rg/fzf -> raw verification -> answer
```

Ordinary read-only queries do not write to the log. Important filebacks or writes must write to the log.

### 14.5 Fileback

High-value answers should not remain only in chat history.

Destination:

| Answer type | Destination |
| --- | --- |
| temporary content awaiting review | `inbox/` |
| reusable FAQ | `wiki/` |
| multi-source synthesis | `wiki/` |
| multi-option comparison | `wiki/` |
| topic navigation | `wiki/maps/` |
| final report | `outputs/` |

### 14.6 Export

```text
wiki/pages/maps/synthesis -> outputs/*.md / pdf / ppt / html / zip
```

`outputs/` is regenerable and does not become the wiki source of truth in reverse.

### 14.7 Archive

Only archive old outputs:

```text
outputs/old-report.md -> archive/old-report.md
```

Archiving must be written to `wiki/log.md`.

### 14.8 Review

After writes, run:

```bash
bash .scripts/postrun.sh
bash .scripts/check-index-log.sh
git --no-pager diff --stat
git --no-pager diff
```

If a check fails, the LLM must report the failure reason, fix it, and retry. It must not claim success.

---

## 15. setup and Testing Principles

setup must generate repeatable and auditable artifacts:

```text
fixed directories
fixed filenames
fixed templates
fixed diff output
fixed manifest
latest selected upstream Skill versions and skipped sources recorded in the manifest
```

Installer implementation must keep control flow and generated content separate:

```text
install.sh = compatibility launcher
src/llm_wiki_installer/installer.py = top-level install orchestration
src/llm_wiki_installer/install_options.py = CLI option parsing
src/llm_wiki_installer/terminal_ui.py = interactive selectors
src/llm_wiki_installer/toolchain.py = dependency tool checks and versions
src/llm_wiki_installer/upstream_skills.py = upstream Skill installation
src/llm_wiki_installer/target_layout.py = target directory and file generation
src/llm_wiki_installer/template_renderer.py = packaged template rendering
src/llm_wiki_installer/command_runner.py = subprocess execution
src/llm_wiki_installer/templates/ = generated target file templates
```

setup must run full unit tests:

```text
use pytest for Python unit tests
install Python development dependencies through a local venv and requirements-dev.txt
create temporary test directory
verify directory generation
verify AGENTS.md generation
verify README.md generation
verify index/log generation
verify postrun.sh
verify check-index-log.sh failure strategy
verify rg/fzf existence
verify upstream skill existence detection
verify skill-manifest.md generation
delete test files, test data, and temporary directory
```

After successful tests, the final repository must not retain:

```text
tests/
fixtures/
example content
temporary test artifacts
```

---

## 16. Risks and Antipatterns

Main risks:

| Risk | Symptom | Control |
| --- | --- | --- |
| raw pollution | agents automatically write raw | raw is read-only by default; inbox->raw requires user trigger |
| wiki dump | many low-quality pages | clear scope, small diffs, index/log, review |
| stale index | new pages are undiscoverable | check-index-log failure |
| false log | deletes/moves have no record | deletes/moves must be logged |
| uncontrolled whole-vault recompilation | large unscoped edits | prohibit whole-vault recompilation without scope |
| outputs polluting wiki | reports become truth source in reverse | outputs->inbox->wiki |
| Skill fork | hand-written replacement for upstream Skill | reuse open-source Skills as-is; generate only the setup wrapper, AGENTS policy, and scripts |
| adapter becomes truth source | different agents have inconsistent rules | AGENTS.md is canonical |
| plugin lock-in | relying on Obsidian plugins as the knowledge format | generate pinned assets; keep knowledge GFM-compatible |
| unreviewable setup drift | different files generated without version evidence | manifest, fixed templates, resolved upstream commits, fixed diff |

Antipatterns:

```text
putting all input directly into raw
letting agents automatically capture/import into raw
letting agents recompile the whole vault without scope
letting outputs write directly back to wiki
using archive to store knowledge
turning MOCs into a second index
creating a page for every term
creating top-level PARA directories
enabling upstream Skills as runtime policy without AGENTS.md precedence
hand-writing a local Skill substitute to replace upstream Skills
keeping test fixtures that pollute the initial repository
making Obsidian plugins architectural dependencies for knowledge meaning
```
