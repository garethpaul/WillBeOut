#!/usr/bin/env sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
FACEBOOK_PY="$ROOT_DIR/facebook.py"
README="$ROOT_DIR/README"

if grep -Fq '12oETzKXQAGaYdkG5gEmGeJJFuYh7EQnp2XdTP1o/Vo=' "$FACEBOOK_PY"; then
  printf '%s\n' "facebook.py must not ship the old public cookie_secret." >&2
  exit 1
fi

if ! grep -Fq "os.environ.get('COOKIE_SECRET', '')" "$FACEBOOK_PY"; then
  printf '%s\n' "facebook.py must read COOKIE_SECRET from the environment." >&2
  exit 1
fi

if ! grep -Fq 'def configured_cookie_secret()' "$FACEBOOK_PY"; then
  printf '%s\n' "facebook.py must validate cookie secret configuration." >&2
  exit 1
fi

if ! grep -Fq 'cookie_secret=configured_cookie_secret()' "$FACEBOOK_PY"; then
  printf '%s\n' "Application settings must use the validated cookie secret." >&2
  exit 1
fi

if ! grep -Fq 'COOKIE_SECRET' "$README"; then
  printf '%s\n' "README must document COOKIE_SECRET setup." >&2
  exit 1
fi

printf '%s\n' "WillBeOut cookie secret checks passed."
