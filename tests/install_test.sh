#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
TEST_TMP="$(mktemp -d "${TMPDIR:-/tmp}/llm-wiki-install-tests.XXXXXX")"
REAL_PYTHON3="$(command -v python3)"
PASS_COUNT=0
FAIL_COUNT=0

trap 'rm -rf "$TEST_TMP"' EXIT

fail_assertion() {
  echo "ASSERTION FAILED: $1" >&2
  return 1
}

assert_file() {
  [ -f "$1" ] || fail_assertion "expected file: $1"
}

assert_dir() {
  [ -d "$1" ] || fail_assertion "expected directory: $1"
}

assert_not_dir() {
  [ ! -d "$1" ] || fail_assertion "unexpected directory: $1"
}

assert_executable() {
  [ -x "$1" ] || fail_assertion "expected executable: $1"
}

assert_contains() {
  local file="$1"
  local expected="$2"
  grep -F -- "$expected" "$file" >/dev/null || {
    echo "----- $file -----" >&2
    sed -n '1,220p' "$file" >&2
    fail_assertion "expected '$expected' in $file"
  }
}

assert_not_contains() {
  local file="$1"
  local unexpected="$2"
  ! grep -F -- "$unexpected" "$file" >/dev/null || {
    echo "----- $file -----" >&2
    sed -n '1,220p' "$file" >&2
    fail_assertion "did not expect '$unexpected' in $file"
  }
}

write_stub_tools() {
  local bin="$1"
  mkdir -p "$bin"

  cat >"$bin/python3" <<EOF_PYTHON3
#!/usr/bin/env bash
exec "$REAL_PYTHON3" "\$@"
EOF_PYTHON3

  cat >"$bin/rg" <<'EOF_RG'
#!/usr/bin/env bash
set -euo pipefail
if [ "${1:-}" = "--version" ]; then
  echo "ripgrep 14.1.0"
fi
EOF_RG

  cat >"$bin/fzf" <<'EOF_FZF'
#!/usr/bin/env bash
set -euo pipefail
if [ "${1:-}" = "--version" ]; then
  echo "0.56.0 (test)"
fi
EOF_FZF

  cat >"$bin/curl" <<'EOF_CURL'
#!/usr/bin/env bash
set -euo pipefail
url="${*: -1}"
case "$url" in
  *github.com/exhank/llm-wiki-installer/releases/latest)
    printf '%s' "${STUB_LATEST_RELEASE_URL:-https://github.com/exhank/llm-wiki-installer/releases/tag/v9.8.7}"
    ;;
  *raw.githubusercontent.com/exhank/llm-wiki-installer/*/install.sh)
    if [ -n "${TEST_CURL_LOG:-}" ]; then
      echo "curl $url" >>"$TEST_CURL_LOG"
    fi
    if [ -z "${TEST_CURL_RAW_INSTALL_SOURCE:-}" ]; then
      echo "TEST_CURL_RAW_INSTALL_SOURCE is required for raw install.sh requests" >&2
      exit 2
    fi
    cat "$TEST_CURL_RAW_INSTALL_SOURCE"
    ;;
  *)
    echo "unexpected curl URL: $url" >&2
    exit 2
    ;;
esac
EOF_CURL

  cat >"$bin/git" <<'EOF_GIT'
#!/usr/bin/env bash
set -euo pipefail

contains_arg() {
  local expected="$1"
  shift
  local arg=""
  for arg in "$@"; do
    [ "$arg" = "$expected" ] && return 0
  done
  return 1
}

repo_dir=""
if [ "${1:-}" = "-C" ]; then
  repo_dir="$2"
  shift 2
fi

while [ "${1:-}" = "-c" ]; do
  shift 2
done

if [ "${1:-}" = "--no-pager" ]; then
  shift
fi

cmd="${1:-}"
case "$cmd" in
  clone)
    repo_url="${@: -2:1}"
    target="${@: -1}"
    mkdir -p "$target"
    if [ "${STUB_GIT_EMPTY_REPO:-0}" = "1" ]; then
      exit 0
    fi
    if [ "${STUB_GIT_NO_SKILL:-0}" = "1" ]; then
      mkdir -p "$target/.skills/empty"
      echo "no skill here" >"$target/.skills/empty/README.md"
      exit 0
    fi
    case "$repo_url" in
      *Ar9av*)
        mkdir -p "$target/.skills/ar9av-skill"
        echo "# Ar9av Skill" >"$target/.skills/ar9av-skill/SKILL.md"
        ;;
      *kepano*)
        mkdir -p "$target/skills/kepano-skill"
        echo "# Kepano Skill" >"$target/skills/kepano-skill/SKILL.md"
        ;;
      *)
        mkdir -p "$target/.skills/default-skill"
        echo "# Default Skill" >"$target/.skills/default-skill/SKILL.md"
        ;;
    esac
    ;;
  remote)
    ;;
  fetch)
    if [ -n "${TEST_GIT_BOOTSTRAP_LOG:-}" ]; then
      echo "git -C $repo_dir fetch ${*:2}" >>"$TEST_GIT_BOOTSTRAP_LOG"
    fi
    ;;
  checkout)
    if [ -n "${TEST_GIT_BOOTSTRAP_SOURCE:-}" ]; then
      cp "$TEST_GIT_BOOTSTRAP_SOURCE/install.sh" "$repo_dir/install.sh"
      mkdir -p "$repo_dir/src" "$repo_dir/tests"
      cp -R "$TEST_GIT_BOOTSTRAP_SOURCE/src/." "$repo_dir/src/"
    fi
    ;;
  init)
    target="."
    if [ "$#" -gt 1 ]; then
      target="${@: -1}"
    fi
    mkdir -p "$target/.git"
    ;;
  rev-parse)
    case "$repo_dir" in
      *Ar9av*) echo "347e85704c52474d13470a3919e4a5cd7e3809cb" ;;
      *kepano*) echo "553ef99aa3306dd23f268e1ba9af752577684f69" ;;
      *) echo "cccccccccccccccccccccccccccccccccccccccc" ;;
    esac
    ;;
  diff)
    if contains_arg "--name-only" "$@"; then
      printf '%s\n' "${STUB_GIT_DIFF_NAMES:-}" | sed '/^$/d'
    elif contains_arg "--name-status" "$@"; then
      printf '%s\n' "${STUB_GIT_NAME_STATUS:-}" | sed '/^$/d'
    elif contains_arg "--unified=0" "$@"; then
      printf '%s\n' "${STUB_GIT_LOG_DIFF:-}" | sed '/^$/d'
    fi
    ;;
  status)
    printf '%s\n' "${STUB_GIT_STATUS:-}" | sed '/^$/d'
    ;;
  ls-files)
    printf '%s\n' "${STUB_GIT_OTHERS:-}" | sed '/^$/d'
    ;;
  *)
    ;;
esac
EOF_GIT

  chmod +x "$bin/python3" "$bin/rg" "$bin/fzf" "$bin/curl" "$bin/git"
}

setup_case() {
  CASE_DIR="$TEST_TMP/$1"
  STUB_BIN="$CASE_DIR/bin"
  mkdir -p "$CASE_DIR"
  write_stub_tools "$STUB_BIN"
}

run_with_stubs() {
  PATH="$STUB_BIN:/usr/bin:/bin:/usr/sbin:/sbin" "$@"
}

run_install() {
  local output="$1"
  shift
  run_with_stubs bash "$ROOT/install.sh" "$@" >"$output" 2>&1
}

expect_install_failure() {
  local output="$1"
  shift
  if run_install "$output" "$@"; then
    sed -n '1,220p' "$output" >&2
    fail_assertion "expected install failure"
  fi
}

test_help() {
  setup_case help
  local out="$CASE_DIR/out.txt"
  run_install "$out" --help
  assert_contains "$out" "Usage: bash install.sh [options] [path/to/knowledge-vault]"
  assert_contains "$out" "--no-interactive"
  assert_contains "$out" "--dry-run"
}

test_lib_only_mode_exits_without_bootstrap() {
  setup_case lib-only
  local out="$CASE_DIR/out.txt"

  LLM_WIKI_INSTALL_LIB_ONLY=1 run_with_stubs bash "$ROOT/install.sh" >"$out" 2>&1

  [ ! -s "$out" ] || fail_assertion "expected lib-only mode to produce no output"
}

test_streamed_bootstrap_is_quiet_for_json_output() {
  setup_case streamed-bootstrap-json
  local out="$CASE_DIR/out.txt"
  local launcher_dir="$CASE_DIR/launcher"
  local target="$CASE_DIR/vault"
  mkdir -p "$launcher_dir"
  cp "$ROOT/install.sh" "$launcher_dir/install.sh"

  TEST_GIT_BOOTSTRAP_SOURCE="$ROOT" \
    LLM_WIKI_INSTALLER_REPO_URL="https://example.invalid/llm-wiki-installer" \
    LLM_WIKI_INSTALLER_REF="v0.1.0" \
    run_with_stubs bash "$launcher_dir/install.sh" --dry-run --json --tools none --skills none "$target" >"$out" 2>&1

  assert_contains "$out" '"action": "dry-run"'
  assert_not_contains "$out" "Cloning into"
  assert_not_contains "$out" "is not a commit"
  assert_not_contains "$out" "detached HEAD"
}

test_streamed_bootstrap_defaults_to_latest_release_ref() {
  setup_case streamed-bootstrap-latest-ref
  local out="$CASE_DIR/out.txt"
  local git_log="$CASE_DIR/git.log"
  local launcher_dir="$CASE_DIR/launcher"
  local target="$CASE_DIR/vault"
  mkdir -p "$launcher_dir"
  cp "$ROOT/install.sh" "$launcher_dir/install.sh"

  TEST_GIT_BOOTSTRAP_SOURCE="$ROOT" \
    TEST_GIT_BOOTSTRAP_LOG="$git_log" \
    run_with_stubs bash "$launcher_dir/install.sh" --dry-run --json --tools none --skills none "$target" >"$out" 2>&1

  assert_contains "$out" '"action": "dry-run"'
  assert_contains "$git_log" "fetch -q --depth 1 origin v9.8.7"
}

test_readme_one_line_curl_install_command() {
  setup_case readme-one-line-curl
  local out="$CASE_DIR/out.txt"
  local curl_log="$CASE_DIR/curl.log"
  local git_log="$CASE_DIR/git.log"
  local target="$CASE_DIR/vault"

  TEST_CURL_RAW_INSTALL_SOURCE="$ROOT/install.sh" \
    TEST_CURL_LOG="$curl_log" \
    TEST_GIT_BOOTSTRAP_SOURCE="$ROOT" \
    TEST_GIT_BOOTSTRAP_LOG="$git_log" \
    run_with_stubs /bin/bash -c \
      'curl -fsSL https://raw.githubusercontent.com/exhank/llm-wiki-installer/main/install.sh | /bin/bash -s -- --no-interactive "$1"' \
      _ "$target" >"$out" 2>&1

  local canonical_target=""
  canonical_target="$(cd "$target" && pwd -P)"

  assert_file "$target/AGENTS.md"
  assert_file "$target/.agents/skills/ar9av-skill/SKILL.md"
  assert_file "$target/.agents/skills/kepano-skill/SKILL.md"
  assert_contains "$curl_log" "raw.githubusercontent.com/exhank/llm-wiki-installer/main/install.sh"
  assert_contains "$git_log" "fetch -q --depth 1 origin v9.8.7"
  assert_contains "$target/.scripts/postrun.sh" "git --no-pager diff --stat"
  assert_contains "$out" "Generated llm-wiki knowledge vault at: $canonical_target"
}

test_refuses_generator_directory() {
  setup_case generator-directory
  local out="$CASE_DIR/out.txt"
  expect_install_failure "$out" "$ROOT"
  assert_contains "$out" "ERROR: target must not be this generator repository or one of its child paths:"
}

test_refuses_generator_child_directory() {
  setup_case generator-child-directory
  local out="$CASE_DIR/out.txt"
  local target="$ROOT/.tmp-test-vault/security-child"
  rm -rf "$target"
  expect_install_failure "$out" "$target"
  assert_contains "$out" "ERROR: target must not be this generator repository or one of its child paths:"
  [ ! -e "$target" ] || fail_assertion "generator child target should not be created"
}

test_refuses_generator_lookalike() {
  setup_case generator-lookalike
  local out="$CASE_DIR/out.txt"
  local target="$CASE_DIR/lookalike"
  mkdir -p "$target/docs"
  : >"$target/docs/llm-wiki-generation-guide.md"
  : >"$target/docs/technical-design.md"
  expect_install_failure "$out" "$target"
  assert_contains "$out" "ERROR: target looks like the llm-wiki generator repository:"
}

test_default_target_is_current_directory() {
  setup_case default-target
  local out="$CASE_DIR/out.txt"
  local target="$CASE_DIR/vault"
  mkdir -p "$target"

  (cd "$target" && run_with_stubs bash "$ROOT/install.sh") >"$out" 2>&1
  local canonical_target=""
  canonical_target="$(cd "$target" && pwd -P)"

  assert_file "$target/AGENTS.md"
  [ ! -e "$target/.agents/skill-manifest.md" ] || fail_assertion "unexpected skill-manifest.md"
  [ ! -e "$target/.agents/skill-manifest.json" ] || fail_assertion "unexpected skill-manifest.json"
  assert_contains "$out" "Generated llm-wiki knowledge vault at: $canonical_target"
}

test_no_interactive_uses_default_selection() {
  setup_case no-interactive
  local out="$CASE_DIR/out.txt"
  local target="$CASE_DIR/vault"

  run_install "$out" --no-interactive "$target"

  assert_file "$target/.agents/skills/ar9av-skill/SKILL.md"
  assert_file "$target/.agents/skills/kepano-skill/SKILL.md"
  [ ! -e "$target/.agents/skill-manifest.md" ] || fail_assertion "unexpected skill-manifest.md"
  [ ! -e "$target/.agents/skill-manifest.json" ] || fail_assertion "unexpected skill-manifest.json"
}

test_dry_run_writes_nothing() {
  setup_case dry-run
  local out="$CASE_DIR/out.txt"
  local target="$CASE_DIR/vault"

  run_install "$out" --dry-run --tools rg --skills none "$target"

  [ ! -e "$target" ] || fail_assertion "dry run should not create target"
  assert_contains "$out" "Dry run: no files were written"
  assert_contains "$out" "Tools: rg"
  assert_contains "$out" "Upstream Skills: none"
}

test_dry_run_json_outputs_plan() {
  setup_case dry-run-json
  local out="$CASE_DIR/out.txt"
  local target="$CASE_DIR/vault"

  run_install "$out" --dry-run --json --tools none --skills none "$target"

  assert_contains "$out" '"action": "dry-run"'
  assert_contains "$out" '"selectedTools": []'
  assert_contains "$out" '"selectedSkills": []'
}

test_full_install_generates_expected_layout() {
  setup_case full-install
  local out="$CASE_DIR/out.txt"
  local target="$CASE_DIR/vault"
  run_install "$out" "$target"
  local canonical_target=""
  canonical_target="$(cd "$target" && pwd -P)"

  assert_dir "$target/inbox"
  assert_dir "$target/raw"
  assert_dir "$target/attachments"
  assert_dir "$target/wiki/maps"
  assert_dir "$target/outputs"
  assert_dir "$target/archives"
  assert_dir "$target/schema"
  assert_file "$target/AGENTS.md"
  assert_file "$target/README.md"
  assert_file "$target/wiki/index.md"
  assert_file "$target/wiki/tags.md"
  assert_file "$target/wiki/log.jsonl"
  assert_file "$target/schema/log.md"
  assert_file "$target/schema/wiki-page.md"
  assert_file "$target/schema/map.md"
  assert_file "$target/.codex/config.toml"
  assert_file "$target/.codex/hooks.json"
  assert_file "$target/.obsidian/app.json"
  assert_file "$target/.obsidian/community-plugins.json"
  assert_file "$target/.obsidian/plugins/obsidian-git/main.js"
  assert_file "$target/.obsidian/plugins/obsidian-git/manifest.json"
  assert_file "$target/.obsidian/plugins/obsidian-git/styles.css"
  assert_file "$target/.obsidian/themes/Things/theme.css"
  assert_file "$target/.agents/skills/ar9av-skill/SKILL.md"
  assert_file "$target/.agents/skills/kepano-skill/SKILL.md"
  [ ! -e "$target/.agents/skill-manifest.md" ] || fail_assertion "unexpected skill-manifest.md"
  [ ! -e "$target/.agents/skill-manifest.json" ] || fail_assertion "unexpected skill-manifest.json"
  assert_executable "$target/.scripts/postrun.sh"
  assert_executable "$target/.scripts/check-index-log.sh"
  assert_executable "$target/.obsidian/plugins/obsidian-git/obsidian_askpass.sh"
  assert_not_dir "$target/.codex/hooks"
  assert_not_dir "$target/tests"
  assert_not_dir "$target/fixtures"
  assert_not_dir "$target/examples"
  [ ! -e "$target/.obsidian/workspace.json" ] || fail_assertion "unexpected workspace.json"
  [ ! -e "$target/.obsidian/workspaces.json" ] || fail_assertion "unexpected workspaces.json"

  assert_contains "$out" "Generated llm-wiki knowledge vault at: $canonical_target"
}

test_existing_generated_files_are_preserved_unless_force_is_used() {
  setup_case force-overwrite
  local out="$CASE_DIR/out.txt"
  local target="$CASE_DIR/vault"

  run_install "$out" "$target"
  printf 'custom readme\n' >"$target/README.md"

  run_install "$out" "$target"
  assert_contains "$target/README.md" "custom readme"
  assert_contains "$out" "keep existing README.md"

  run_install "$out" --force "$target"
  assert_contains "$target/README.md" "# Knowledge Vault"
  assert_not_contains "$target/README.md" "custom readme"
}

test_upstream_repo_without_skills_fails() {
  setup_case upstream-empty
  local out="$CASE_DIR/out.txt"
  local target="$CASE_DIR/vault"

  if STUB_GIT_EMPTY_REPO=1 run_install "$out" "$target"; then
    sed -n '1,220p' "$out" >&2
    fail_assertion "expected upstream empty repo failure"
  fi
  assert_contains "$out" "has no .skills/ or skills/ directory."
}

test_upstream_repo_without_skill_files_fails() {
  setup_case upstream-no-skill
  local out="$CASE_DIR/out.txt"
  local target="$CASE_DIR/vault"

  if STUB_GIT_NO_SKILL=1 run_install "$out" "$target"; then
    sed -n '1,220p' "$out" >&2
    fail_assertion "expected upstream no SKILL.md failure"
  fi
  assert_contains "$out" "has no discovered SKILL.md files."
}

test_generated_check_index_log_requires_index_and_log() {
  setup_case check-index-log
  local out="$CASE_DIR/out.txt"
  local target="$CASE_DIR/vault"

  run_install "$out" "$target"

  if (cd "$target" && STUB_GIT_DIFF_NAMES="wiki/new-page.md" run_with_stubs bash .scripts/check-index-log.sh) >"$out" 2>&1; then
    sed -n '1,220p' "$out" >&2
    fail_assertion "expected index/log failure"
  fi
  assert_contains "$out" "ERROR: wiki content changed but wiki/index.md was not updated."

  (
    export STUB_GIT_DIFF_NAMES=$'wiki/new-page.md\nwiki/index.md\nwiki/log.jsonl'
    export STUB_GIT_LOG_DIFF=$'+{"schema_version":1,"timestamp":"2026-05-29T00:00:00Z","actor":"agent","type":"ingest","scope":"raw/source -> wiki/new-page.md","reason":"Compiled durable knowledge from raw source.","review":"self-reviewed","impact":{"index_updated":true,"references_checked":true},"files":["raw/source","wiki/new-page.md","wiki/index.md"]}'
    cd "$target"
    run_with_stubs bash .scripts/check-index-log.sh
  ) >"$out" 2>&1
  assert_contains "$out" "Index/log checks OK."
}

test_generated_check_index_log_requires_log_for_raw_changes() {
  setup_case check-index-log-raw
  local out="$CASE_DIR/out.txt"
  local target="$CASE_DIR/vault"

  run_install "$out" "$target"

  if (cd "$target" && STUB_GIT_DIFF_NAMES="raw/source.md" run_with_stubs bash .scripts/check-index-log.sh) >"$out" 2>&1; then
    sed -n '1,220p' "$out" >&2
    fail_assertion "expected raw/log failure"
  fi
  assert_contains "$out" "ERROR: raw/ changed but wiki/log.jsonl was not updated."
}

test_generated_check_index_log_rejects_bad_generated_names() {
  setup_case check-index-log-names
  local out="$CASE_DIR/out.txt"
  local target="$CASE_DIR/vault"

  run_install "$out" "$target"

  if (cd "$target" && STUB_GIT_DIFF_NAMES="outputs/New Note.md" run_with_stubs bash .scripts/check-index-log.sh) >"$out" 2>&1; then
    sed -n '1,220p' "$out" >&2
    fail_assertion "expected bad generated filename failure"
  fi
  assert_contains "$out" "ERROR: Generated wiki/output/script/config-description filenames must use lowercase kebab-case."
}

test_generated_postrun_rejects_unauthorized_skill_file() {
  setup_case postrun-skill
  local out="$CASE_DIR/out.txt"
  local target="$CASE_DIR/vault"

  run_install "$out" "$target"
  printf '# Local Skill\n' >"$target/SKILL.md"

  if (cd "$target" && run_with_stubs bash .scripts/postrun.sh) >"$out" 2>&1; then
    sed -n '1,220p' "$out" >&2
    fail_assertion "expected unauthorized SKILL.md failure"
  fi
  assert_contains "$out" "ERROR: Unauthorized SKILL.md found outside .agents/skills/<skill-name>/."
}

test_generated_postrun_rejects_forbidden_runtime_directories() {
  setup_case postrun-forbidden-dir
  local out="$CASE_DIR/out.txt"
  local target="$CASE_DIR/vault"

  run_install "$out" "$target"
  mkdir -p "$target/.codex/rules"

  if (cd "$target" && run_with_stubs bash .scripts/postrun.sh) >"$out" 2>&1; then
    sed -n '1,220p' "$out" >&2
    fail_assertion "expected forbidden directory failure"
  fi
  assert_contains "$out" "ERROR: .codex/rules/ must not exist."
}

test_generated_postrun_requires_raw_authorization() {
  setup_case postrun-raw
  local out="$CASE_DIR/out.txt"
  local target="$CASE_DIR/vault"

  run_install "$out" "$target"

  if (cd "$target" && STUB_GIT_DIFF_NAMES="raw/source.md" run_with_stubs bash .scripts/postrun.sh) >"$out" 2>&1; then
    sed -n '1,220p' "$out" >&2
    fail_assertion "expected raw authorization failure"
  fi
  assert_contains "$out" "ERROR: raw/ changed. Set ALLOW_RAW_CHANGE=1 only when the user explicitly authorized this raw change."

  (
    export ALLOW_RAW_CHANGE=1
    export STUB_GIT_DIFF_NAMES=$'raw/source.md\nwiki/log.jsonl'
    cd "$target"
    run_with_stubs bash .scripts/postrun.sh
  ) >"$out" 2>&1
  assert_contains "$out" "Post-run OK. Review diff before commit."
}

run_test() {
  local name="$1"
  echo "== $name =="
  if (set -e; "$name"); then
    PASS_COUNT=$((PASS_COUNT + 1))
    echo "ok $name"
  else
    FAIL_COUNT=$((FAIL_COUNT + 1))
    echo "not ok $name" >&2
  fi
}

main() {
  run_test test_help
  run_test test_lib_only_mode_exits_without_bootstrap
  run_test test_streamed_bootstrap_is_quiet_for_json_output
  run_test test_streamed_bootstrap_defaults_to_latest_release_ref
  run_test test_readme_one_line_curl_install_command
  run_test test_refuses_generator_directory
  run_test test_refuses_generator_child_directory
  run_test test_refuses_generator_lookalike
  run_test test_default_target_is_current_directory
  run_test test_no_interactive_uses_default_selection
  run_test test_dry_run_writes_nothing
  run_test test_dry_run_json_outputs_plan
  run_test test_full_install_generates_expected_layout
  run_test test_existing_generated_files_are_preserved_unless_force_is_used
  run_test test_upstream_repo_without_skills_fails
  run_test test_upstream_repo_without_skill_files_fails
  run_test test_generated_check_index_log_requires_index_and_log
  run_test test_generated_check_index_log_requires_log_for_raw_changes
  run_test test_generated_check_index_log_rejects_bad_generated_names
  run_test test_generated_postrun_rejects_unauthorized_skill_file
  run_test test_generated_postrun_rejects_forbidden_runtime_directories
  run_test test_generated_postrun_requires_raw_authorization

  echo
  echo "Passed: $PASS_COUNT"
  echo "Failed: $FAIL_COUNT"

  [ "$FAIL_COUNT" -eq 0 ]
}

main "$@"
