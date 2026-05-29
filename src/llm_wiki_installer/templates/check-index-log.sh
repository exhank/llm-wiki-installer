#!/usr/bin/env bash
set -euo pipefail

fail() {
  echo "ERROR: $1" >&2
  exit 1
}

tmp_changed="$(mktemp)"
trap 'rm -f "$tmp_changed"' EXIT

{
  git diff --name-only || true
  git diff --cached --name-only || true
  git ls-files --others --exclude-standard || true
} | sed '/^$/d' | sort -u > "$tmp_changed"

has_changed() {
  grep -E "$1" "$tmp_changed" >/dev/null
}

if [ ! -s "$tmp_changed" ]; then
  echo "No changed files."
  exit 0
fi

wiki_content_changed="$(
  grep -E '^wiki/' "$tmp_changed" \
    | grep -v -E '^wiki/index\.md$|^wiki/log\.md$' \
    || true
)"

if [ -n "$wiki_content_changed" ]; then
  has_changed '^wiki/index\.md$' || fail "wiki content changed but wiki/index.md was not updated."
  has_changed '^wiki/log\.md$' || fail "wiki content changed but wiki/log.md was not updated."
fi

raw_changed="$(
  grep -E '^raw/' "$tmp_changed" \
    || true
)"

if [ -n "$raw_changed" ]; then
  has_changed '^wiki/log\.md$' || fail "raw/ changed but wiki/log.md was not updated."
fi

file_structure_changed="$(
  {
    git diff --name-status --diff-filter=DRC || true
    git diff --cached --name-status --diff-filter=DRC || true
    git status --porcelain=v1 | grep -E '^( D|D |R |RM|RD| C|C )' || true
  } | sed '/^$/d'
)"

if [ -n "$file_structure_changed" ]; then
  has_changed '^wiki/log\.md$' || fail "file deleted, moved, renamed, or copied but wiki/log.md was not updated."
fi

bad_generated_names="$(
  grep -E '^(wiki|outputs|\.scripts|\.codex)/' "$tmp_changed" \
    | grep -E '(^|/)(New Note|untitled|tmp|note)\.md$|[[:space:]]|[A-Z]' \
    || true
)"

if [ -n "$bad_generated_names" ]; then
  printf "%s\n" "$bad_generated_names" >&2
  fail "Generated wiki/output/script/config-description filenames must use lowercase kebab-case."
fi

if has_changed '^wiki/log\.md$'; then
  if {
      git diff --unified=0 -- wiki/log.md || true
      git diff --cached --unified=0 -- wiki/log.md || true
      if git ls-files --others --exclude-standard -- wiki/log.md | grep -q '^wiki/log\.md$'; then
        sed 's/^/+/' wiki/log.md
      fi
    } \
    | grep -E '^\+.*type: (ingest|fileback|delete|move|archive-output|schema-update|rename|lint|index-update|map-update)' >/dev/null; then
    :
  else
    fail "wiki/log.md changed but no recognized log entry type was added."
  fi
fi

echo "Index/log checks OK."
