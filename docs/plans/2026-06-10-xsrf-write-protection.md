# XSRF Write Protection

Status: Completed

## Goal

Prevent third-party sites, speculative navigation, and crawlers from changing
an authenticated user's event data or session state.

## Scope

- Enable Tornado's signed XSRF cookie enforcement.
- Convert attendance, vote, vote removal, message deletion, and logout handlers
  from GET to POST.
- Replace mutation links with POST forms or token-bearing AJAX calls.
- Include Tornado XSRF fields in desktop, mobile, and logout forms.
- Include the `_xsrf` cookie value in calendar, suggestion, attendance,
  message-deletion, and mobile-message AJAX requests.
- Add portable contracts for handler methods, application settings, templates,
  and JavaScript clients.

## Verification

- `make check`
- Mutation check: disabling `xsrf_cookies` causes the contract checker to fail.
- Mutation check: changing an attendance mutation back to GET causes the
  contract checker to fail.

## Outcome

Authenticated writes now require an intentional POST carrying a Tornado XSRF
token. Read-only data routes remain GET endpoints, while unsafe navigation can
no longer add attendance, alter votes, delete messages, or clear a session.
