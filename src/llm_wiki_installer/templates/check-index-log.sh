#!/usr/bin/env bash
set -euo pipefail

# Structural consistency lint. Hard failures are limited to structural
# changes that would break vault discoverability or auditability. Naming
# issues are warnings so normal human edits are never rejected.

fail() {
  echo "ERROR: $1" >&2
  exit 1
}

tmp_changed="$(mktemp)"
tmp_new="$(mktemp)"
tmp_structural="$(mktemp)"
trap 'rm -f "$tmp_changed" "$tmp_new" "$tmp_structural"' EXIT

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

{
  git ls-files --others --exclude-standard || true
  {
    git diff --name-status --diff-filter=A || true
    git diff --cached --name-status --diff-filter=A || true
  } | awk '$1 == "A" {print $2}'
} | sed '/^$/d' | sort -u \
  | grep -E '^wiki/' \
  | grep -v -E '^wiki/(index\.md|tags\.md|log\.jsonl)$|/\.gitkeep$' \
  > "$tmp_new" || true

if [ -s "$tmp_new" ]; then
  if ! has_changed '^wiki/index\.md$'; then
    cat "$tmp_new" >&2
    fail "new wiki pages were added but wiki/index.md was not updated."
  fi
  if ! has_changed '^wiki/log\.jsonl$'; then
    cat "$tmp_new" >&2
    fail "new wiki pages were added but wiki/log.jsonl was not updated."
  fi
fi

{
  {
    git diff --name-status --diff-filter=DRC || true
    git diff --cached --name-status --diff-filter=DRC || true
  } | awk '$1 ~ /^[DRC]/ {print}'
  git status --porcelain=v1 | grep -E '^( D|D |R |RM|RD| C|C )' || true
} | sed '/^$/d' > "$tmp_structural"

if [ -s "$tmp_structural" ]; then
  has_changed '^wiki/log\.jsonl$' || fail "file deleted, moved, renamed, or copied but wiki/log.jsonl was not updated."
fi

bad_generated_names="$(
  grep -E '^(wiki|outputs|\.scripts)/' "$tmp_changed" \
    | grep -E '(^|/)(New Note|untitled|tmp|note)\.md$|[[:space:]]|[A-Z]' \
    || true
)"

if [ -n "$bad_generated_names" ]; then
  printf "%s\n" "$bad_generated_names" >&2
  echo "WARNING: agent-generated wiki/output/script filenames should use lowercase kebab-case." >&2
fi

echo "Index/log checks OK."
