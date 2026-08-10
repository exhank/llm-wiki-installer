#!/usr/bin/env bash
set -euo pipefail

# Hard boundary checks only. Everything advisory lives in check-index-log.sh.

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

raw_changes="$(changed_paths raw | grep -v -E '^raw/\.gitkeep$' || true)"
if [ -n "$raw_changes" ]; then
  if [ "${ALLOW_RAW_CHANGE:-0}" != "1" ]; then
    printf "%s\n" "$raw_changes" >&2
    fail "raw/ changed. Set ALLOW_RAW_CHANGE=1 only when the user explicitly authorized this raw change."
  fi

  if ! changed_paths wiki/log.jsonl | grep -q .; then
    fail "raw/ changed but wiki/log.jsonl was not updated."
  fi
fi

if git status --porcelain=v1 | grep -q .; then
  echo "-- Changed files --"
  git status --short
fi

echo "-- Diff stat --"
git --no-pager diff --stat || true

echo "Post-run OK. Review diff before commit."
