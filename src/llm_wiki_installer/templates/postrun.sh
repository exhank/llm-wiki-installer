#!/usr/bin/env bash
set -euo pipefail

fail() {
  echo "ERROR: $1" >&2
  exit 1
}

changed_paths() {
  git diff --name-only -- "$@" || true
  git diff --cached --name-only -- "$@" || true
  git ls-files --others --exclude-standard -- "$@" || true
}

echo "== Post-run checks =="

if [ -d ".codex/rules" ]; then
  fail ".codex/rules/ must not exist."
fi

if [ -d ".obsidian/plugins" ]; then
  fail ".obsidian/plugins/ must not exist."
fi

if git status --porcelain=v1 -- .codex/rules .obsidian/plugins | grep -q .; then
  fail "Forbidden paths are present in git status."
fi

unauthorized_skill_paths="$(
  find . \
    \( -path './.git' -o -path './node_modules' -o -path './.cache' \) -prune -o \
    -name SKILL.md -print \
    | grep -v -E '^\./\.agents/skills/upstream/[^/]+/.+/SKILL\.md$' \
    || true
)"

if [ -n "$unauthorized_skill_paths" ]; then
  printf "%s\n" "$unauthorized_skill_paths" >&2
  fail "Unauthorized SKILL.md found outside .agents/skills/upstream/<repo>/<skill-name>/."
fi

bad_generated_names="$(
  changed_paths wiki outputs .scripts .codex \
    | grep -E '(^|/)(New Note|untitled|tmp|note)\.md$|[[:space:]]|[A-Z]' \
    || true
)"

if [ -n "$bad_generated_names" ]; then
  printf "%s\n" "$bad_generated_names" >&2
  fail "Generated wiki/output/script/config-description filenames must use lowercase kebab-case."
fi

if git status --porcelain=v1 | grep -q .; then
  echo "-- Changed files --"
  git status --short
fi

if changed_paths raw | grep -q .; then
  if [ "${ALLOW_RAW_CHANGE:-0}" != "1" ]; then
    fail "raw/ changed. Set ALLOW_RAW_CHANGE=1 only when the user explicitly authorized this raw change."
  fi

  if ! changed_paths wiki/log.md | grep -q .; then
    fail "raw/ changed but wiki/log.md was not updated."
  fi
fi

{{QMD_POSTRUN_CHECK}}

echo "-- Diff stat --"
git --no-pager diff --stat || true

echo "Post-run OK. Review diff before commit."
