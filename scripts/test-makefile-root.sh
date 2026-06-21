#!/usr/bin/env sh
set -eu

PATH=/usr/bin:/bin
export PATH
ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && /bin/pwd -P)
TEMP_ROOT=$(mktemp -d "${TMPDIR:-/tmp}/willbeout-make-authority-XXXXXX")
trap 'rm -rf "$TEMP_ROOT"' EXIT HUP INT TERM
unset MAKEFILES MAKEFILE_LIST MAKEFLAGS MFLAGS MAKEOVERRIDES PYTHON ROOT SHELL

CONTROL_DIR="$TEMP_ROOT/control"
CHECKOUT="$TEMP_ROOT/willbeout app's [gate] \"quoted\" \`touch WILLBEOUT_ROOT_MARKER\`"
ATTACKER_ROOT="$TEMP_ROOT/attacker"
AUTHORITY_PATH="$TEMP_ROOT/no-unreviewed-tools"
LOG="$TEMP_ROOT/commands.log"
SHELL_LOG="$TEMP_ROOT/shell.log"
mkdir -p "$CONTROL_DIR" "$CHECKOUT/scripts" "$ATTACKER_ROOT" "$AUTHORITY_PATH"
CONTROL_DIR=$(CDPATH= cd -- "$CONTROL_DIR" && /bin/pwd -P)
CHECKOUT=$(CDPATH= cd -- "$CHECKOUT" && /bin/pwd -P)
MAKEFILE="$CHECKOUT/Makefile"
cp "$ROOT_DIR/Makefile" "$MAKEFILE"

FAKE_PYTHON="$TEMP_ROOT/trusted python's \"quoted\" \`touch WILLBEOUT_PYTHON_MARKER\` \$literal"
cat >"$FAKE_PYTHON" <<'SCRIPT'
#!/bin/sh
printf '%s|%s|%s\n' "$PWD" "$0" "$*" >> "$WILLBEOUT_COMMAND_LOG"
SCRIPT
chmod +x "$FAKE_PYTHON"
for script in check_willbeout_contracts.py dependency_lock_contract.py test_dependency_lock_contract.py test_workflow_contract.py; do
  cp "$FAKE_PYTHON" "$CHECKOUT/scripts/$script"
done
cat >"$CHECKOUT/scripts/test-makefile-root.sh" <<'SCRIPT'
#!/bin/sh
printf '%s|%s|root-test\n' "$PWD" "$0" >> "$WILLBEOUT_COMMAND_LOG"
SCRIPT
chmod +x "$CHECKOUT/scripts/test-makefile-root.sh"

FAKE_SHELL="$TEMP_ROOT/fake-shell"
printf '#!/bin/sh\nprintf invoked >> %s\nexec /bin/sh "$@"\n' "'$SHELL_LOG'" >"$FAKE_SHELL"
chmod +x "$FAKE_SHELL"

run_case() {
  target=$1
  mode=$2
  output="$TEMP_ROOT/case.out"
  rm -f "$LOG" "$SHELL_LOG" "$output"
  : >"$CHECKOUT/probe.pyc"
  : >"$ATTACKER_ROOT/keep.pyc"
  set +e
  case "$mode" in
    default) (cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" WILLBEOUT_COMMAND_LOG="$LOG" /usr/bin/make --no-print-directory -f "$MAKEFILE" "PYTHON=$FAKE_PYTHON" "$target") >"$output" 2>&1 ;;
    command-root) (cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" WILLBEOUT_COMMAND_LOG="$LOG" /usr/bin/make --no-print-directory -f "$MAKEFILE" ROOT="$ATTACKER_ROOT" "PYTHON=$FAKE_PYTHON" "$target") >"$output" 2>&1 ;;
    environment-root) (cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" ROOT="$ATTACKER_ROOT" WILLBEOUT_COMMAND_LOG="$LOG" /usr/bin/make --no-print-directory -f "$MAKEFILE" "PYTHON=$FAKE_PYTHON" "$target") >"$output" 2>&1 ;;
    command-shell) (cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" WILLBEOUT_COMMAND_LOG="$LOG" /usr/bin/make --no-print-directory -f "$MAKEFILE" SHELL="$FAKE_SHELL" "PYTHON=$FAKE_PYTHON" "$target") >"$output" 2>&1 ;;
    environment-shell) (cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" SHELL="$FAKE_SHELL" WILLBEOUT_COMMAND_LOG="$LOG" /usr/bin/make --no-print-directory -f "$MAKEFILE" "PYTHON=$FAKE_PYTHON" "$target") >"$output" 2>&1 ;;
  esac
  status=$?
  set -e
  if [ "$status" -ne 0 ] || [ -e "$SHELL_LOG" ] || [ ! -e "$ATTACKER_ROOT/keep.pyc" ]; then
    printf 'authority case failed: target=%s mode=%s status=%s\n' "$target" "$mode" "$status" >&2
    cat "$output" >&2
    return 1
  fi
  case "$target" in
    clean) [ ! -e "$CHECKOUT/probe.pyc" ] ;;
    build) grep -Fq 'Python application: no separate build artifact.' "$output" ;;
    *) grep -Fq "$CHECKOUT" "$LOG" ;;
  esac
}

executed=0
for target in build check clean contract-test lint root-test test verify; do
  for mode in default command-root environment-root command-shell environment-shell; do
    run_case "$target" "$mode"
    executed=$((executed + 1))
  done
done
[ "$executed" -eq 40 ]

rm -f "$LOG"
(cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" WILLBEOUT_COMMAND_LOG="$LOG" /usr/bin/make --no-print-directory -f "$MAKEFILE" "PYTHON=$FAKE_PYTHON" check) >/dev/null 2>&1
grep -Fq "$FAKE_PYTHON" "$LOG"
[ ! -e "$CONTROL_DIR/WILLBEOUT_ROOT_MARKER" ]
[ ! -e "$CONTROL_DIR/WILLBEOUT_PYTHON_MARKER" ]

for syntax in paren brace; do
  case "$syntax" in
    paren) open='('; close=')' ;;
    brace) open='{'; close='}' ;;
  esac
  python_mark="$TEMP_ROOT/python-$syntax-syntax"
  python_bad="\$${open}shell /usr/bin/touch '$python_mark'$close"
  if (cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" /usr/bin/make --no-print-directory -f "$MAKEFILE" "PYTHON=$python_bad" lint) >"$TEMP_ROOT/python-$syntax.out" 2>&1; then exit 1; fi
  [ ! -e "$python_mark" ]
  python_env_mark="$TEMP_ROOT/python-$syntax-environment-syntax"
  python_env_bad="\$${open}shell /usr/bin/touch '$python_env_mark'$close"
  if (cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" PYTHON="$python_env_bad" /usr/bin/make --environment-overrides --no-print-directory -f "$MAKEFILE" lint) >"$TEMP_ROOT/python-$syntax-environment.out" 2>&1; then exit 1; fi
  [ ! -e "$python_env_mark" ]
  root_mark="$TEMP_ROOT/root-$syntax-syntax"
  root_bad="\$${open}shell /usr/bin/touch '$root_mark'$close"
  (cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" WILLBEOUT_COMMAND_LOG="$LOG" /usr/bin/make --no-print-directory -f "$MAKEFILE" "ROOT=$root_bad" "PYTHON=$FAKE_PYTHON" lint) >/dev/null 2>&1
  [ ! -e "$root_mark" ]
  root_env_mark="$TEMP_ROOT/root-$syntax-environment-syntax"
  root_env_bad="\$${open}shell /usr/bin/touch '$root_env_mark'$close"
  (cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" ROOT="$root_env_bad" WILLBEOUT_COMMAND_LOG="$LOG" /usr/bin/make --environment-overrides --no-print-directory -f "$MAKEFILE" "PYTHON=$FAKE_PYTHON" lint) >/dev/null 2>&1
  [ ! -e "$root_env_mark" ]
done

if (cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" /usr/bin/make --no-print-directory -f "$MAKEFILE" MAKEFILE_LIST=/tmp/untrusted check) >"$TEMP_ROOT/list-command.out" 2>&1; then exit 1; fi
grep -Fq 'MAKEFILE_LIST must not be overridden' "$TEMP_ROOT/list-command.out"
if (cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" MAKEFILE_LIST=/tmp/untrusted /usr/bin/make --environment-overrides --no-print-directory -f "$MAKEFILE" check) >"$TEMP_ROOT/list-environment.out" 2>&1; then exit 1; fi
grep -Fq 'MAKEFILE_LIST must not be overridden' "$TEMP_ROOT/list-environment.out"

PRE="$TEMP_ROOT/pre.mk"; PRE_MARKER="$TEMP_ROOT/pre-ran"; printf '%s\n' "\$(shell /usr/bin/touch '$PRE_MARKER')" >"$PRE"
if (cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" MAKEFILES="$PRE" /usr/bin/make --no-print-directory -f "$MAKEFILE" check) >"$TEMP_ROOT/pre.out" 2>&1; then exit 1; fi
grep -Fq 'MAKEFILES must be empty' "$TEMP_ROOT/pre.out"; [ -e "$PRE_MARKER" ]
EARLY="$TEMP_ROOT/early.mk"; EARLY_MARKER="$TEMP_ROOT/early-ran"; printf '%s\n' "\$(shell /usr/bin/touch '$EARLY_MARKER')" >"$EARLY"
if (cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" /usr/bin/make --no-print-directory -f "$EARLY" -f "$MAKEFILE" check) >"$TEMP_ROOT/early.out" 2>&1; then exit 1; fi
[ -e "$EARLY_MARKER" ]

for target in build check clean contract-test lint root-test test verify; do
  later="$TEMP_ROOT/later-$target.mk"
  printf '%s:\n\t@/usr/bin/touch %s\n' "$target" "$TEMP_ROOT/replaced-$target" >"$later"
  if (cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" /usr/bin/make --no-print-directory -f "$MAKEFILE" -f "$later" "$target" "PYTHON=$FAKE_PYTHON") >"$TEMP_ROOT/later-$target.out" 2>&1; then exit 1; fi
  [ ! -e "$TEMP_ROOT/replaced-$target" ]
done

TARGET_PYTHON="$TEMP_ROOT/target-python"; TARGET_LOG="$TEMP_ROOT/target.log"
cat >"$TARGET_PYTHON" <<'SCRIPT'
#!/bin/sh
printf target >> "$WILLBEOUT_TARGET_LOG"
exit 1
SCRIPT
chmod +x "$TARGET_PYTHON"
LATER_VARS="$TEMP_ROOT/later-vars.mk"
cat >"$LATER_VARS" <<LATER_VARS_EOF
build check clean contract-test lint root-test test verify: MAKEFILE_LIST := $MAKEFILE
build check clean contract-test lint root-test test verify: ROOT := $ATTACKER_ROOT
build check clean contract-test lint root-test test verify: PYTHON := $TARGET_PYTHON
LATER_VARS_EOF
rm -f "$LOG" "$TARGET_LOG"
(cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" WILLBEOUT_COMMAND_LOG="$LOG" WILLBEOUT_TARGET_LOG="$TARGET_LOG" /usr/bin/make --no-print-directory -f "$MAKEFILE" -f "$LATER_VARS" check "PYTHON=$FAKE_PYTHON") >/dev/null 2>&1
grep -Fq "$FAKE_PYTHON" "$LOG"; [ ! -e "$TARGET_LOG" ]

LATER_SHELL="$TEMP_ROOT/later-shell.mk"
cat >"$LATER_SHELL" <<LATER_SHELL_EOF
build check clean contract-test lint root-test test verify: MAKEFILE_LIST := $MAKEFILE
build check clean contract-test lint root-test test verify: SHELL := $FAKE_SHELL
build check clean contract-test lint root-test test verify: .SHELLFLAGS := -c
LATER_SHELL_EOF
rm -f "$LOG" "$SHELL_LOG"
(cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" WILLBEOUT_COMMAND_LOG="$LOG" /usr/bin/make --no-print-directory -f "$MAKEFILE" -f "$LATER_SHELL" check "PYTHON=$FAKE_PYTHON") >/dev/null 2>&1
[ ! -e "$SHELL_LOG" ]; grep -Fq "$CHECKOUT" "$LOG"

PATH_PYTHON="$TEMP_ROOT/python3"; PATH_LOG="$TEMP_ROOT/path-python.log"; cp "$FAKE_PYTHON" "$PATH_PYTHON"
rm -f "$PATH_LOG"
(cd "$CONTROL_DIR" && PATH="$TEMP_ROOT:/usr/bin:/bin" WILLBEOUT_COMMAND_LOG="$PATH_LOG" /usr/bin/make --no-print-directory -f "$MAKEFILE" lint) >/dev/null 2>&1
[ -s "$PATH_LOG" ]

if (cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" /usr/bin/make --no-print-directory -f "$MAKEFILE" MAKEFLAGS=-n check) >"$TEMP_ROOT/flags.out" 2>&1; then exit 1; fi
grep -Fq 'MAKEFLAGS must not be overridden' "$TEMP_ROOT/flags.out"
for flag in -n --just-print --dry-run --recon -t --touch -q --question -i --ignore-errors; do
  if (cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" /usr/bin/make "$flag" --no-print-directory -f "$MAKEFILE" check) >"$TEMP_ROOT/flag.out" 2>&1; then exit 1; fi
  grep -Fq 'non-executing or error-ignoring MAKEFLAGS are not supported' "$TEMP_ROOT/flag.out"
done

printf '%s\n' 'Make authority tests passed: 40 target/authority cases, hostile literal Python path, 8 raw Make-syntax controls, 2 MAKEFILE_LIST rejections, 2 startup-boundary cases, 8 later recipe-replacement rejections, later root/Python and shell protection, PATH-Python boundary control, cleanup containment, caller MAKEFLAGS rejection, and 10 mode rejections'
