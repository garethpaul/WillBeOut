#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

ROOT="$ROOT" python3 - <<'PY'
import os
import re
import sys
from pathlib import Path

ROOT = Path(os.environ["ROOT"])


def text(path):
    return (ROOT / path).read_text()


def fail(message):
    print("FAIL: {}".format(message))
    sys.exit(1)


def require(pattern, path, message, flags=0):
    if not re.search(pattern, text(path), flags):
        fail(message)


def reject(pattern, path, message, flags=0):
    if re.search(pattern, text(path), flags):
        fail(message)


def class_block(path, class_name):
    source = text(path)
    match = re.search(r"^class {}\b.*?(?=^class \w|\Z)".format(class_name),
                      source, re.M | re.S)
    if not match:
        fail("{} missing class {}".format(path, class_name))
    return match.group(0)


def require_post_only(path, class_name):
    block = class_block(path, class_name)
    if "def post(self):" not in block:
        fail("{} must define POST for {}".format(path, class_name))
    if "def get(self):" in block:
        fail("{} must not define mutating GET for {}".format(path, class_name))


require(r"xsrf_cookies=True", "facebook.py", "Tornado XSRF cookies must be enabled")
reject(r"xsrf_cookies=False", "facebook.py", "Tornado XSRF cookies must not be disabled")

for path, class_name in [
    ("auth.py", "AuthLogoutHandler"),
    ("attendees.py", "Attend"),
    ("attendees.py", "AttendNo"),
    ("votes.py", "VoteHandler"),
    ("votes.py", "ChangeVoteHandler"),
    ("messages.py", "DMHandler"),
]:
    require_post_only(path, class_name)

require(r"action='/vote' method='post'", "templates/event.html",
        "Vote action must be a POST form")
require(r"action='/change/vote' method='post'", "templates/event.html",
        "Change vote action must be a POST form")
require(r"attendForm\('/attend/no'", "templates/event.html",
        "Attend removal must use the POST form helper")
require(r"attendForm\('/attend',", "templates/event.html",
        "Attend creation must use the POST form helper")
require(r'action="/delete/message" method="post"', "templates/event.html",
        "Message deletion must be a POST form")
require(r'action="/auth/logout" method="post"', "templates/base.html",
        "Navbar logout must be a POST form")
require(r'action="/auth/logout" method="post"', "templates/stream.html",
        "Stream logout must be a POST form")
require(r"_xsrf", "static/js/events.js",
        "Calendar AJAX POST must include an XSRF token")
require(r"_xsrf", "templates/mobile_event.html",
        "Mobile AJAX POSTs must include an XSRF token")
require(r"xsrf_form_html\(\)", "mobile.py",
        "Mobile event rendering must materialize an XSRF token")

mutating_link = re.compile(
    r"""href=['"][^'"]*/(?:attend(?:/no)?|vote|change/vote|delete/message|auth/logout)\b"""
)
for path in [
    "templates/base.html",
    "templates/event.html",
    "templates/mobile_event.html",
    "templates/events.html",
    "templates/stream.html",
]:
    if mutating_link.search(text(path)):
        fail("{} contains a mutating GET link".format(path))

print("Baseline checks passed")
PY
