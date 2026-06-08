# Issue 3: Enable XSRF Protection

## Context

GitHub issue: `garethpaul/WillBeOut#3`

The Tornado application disables XSRF cookies while authenticated handlers mutate events, votes, attendees, calendar data, suggestions, messages, and session state. Some mutations are exposed through GET links, which bypass Tornado's unsafe-method XSRF checks.

## Plan

1. Enable Tornado XSRF cookies in the application settings.
2. Convert vote, attendance, message deletion, and logout mutations from GET handlers to POST handlers.
3. Replace mutating GET links with POST forms carrying `_xsrf` tokens.
4. Include `_xsrf` in AJAX POSTs from desktop and mobile event flows.
5. Add a source-level verification script that checks the XSRF setting, handler methods, token propagation, and absence of mutating GET links.

## Verification

- Run `bash scripts/check-baseline.sh`.
- Compile the changed Python files.
- Run `git diff --check`.
