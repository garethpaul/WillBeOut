# Calendar JSON Response Design

## Evidence

- `CalHandler.get` returns authenticated, user-scoped calendar rows as a JSON
  array through `json.dumps`, but leaves Tornado's default HTML content type.
- Direct navigation can therefore expose a sensitive JSON response under an
  ambiguous media type and without `X-Content-Type-Options: nosniff`.
- `MessageHandler.get` already establishes the repository precedent:
  `application/json; charset=UTF-8` plus `X-Content-Type-Options: nosniff` while
  preserving the existing array payload.
- `static/js/events.js` consumes the current array shape, so wrapping or
  versioning the response would create unnecessary compatibility risk.

## Options

1. **Preserve the array and add exact response headers (recommended).** Small,
   compatible, and consistent with the message API.
2. Wrap the array in an object. This would provide a stronger JSON-hijacking
   shape but break the existing browser consumer.
3. Replace the endpoint with a new API. This is disproportionate for a
   historical app and creates duplicate behavior.

## Decision

Set the JSON media type and `nosniff` before querying calendar rows. Preserve
authentication, user scoping, SQL parameters, field names, ordering, and the
top-level array.

## Validation

- Add an authenticated runtime test that exercises `/calendar/get` and asserts
  the exact headers and unchanged decoded payload.
- Add a static source contract so future refactors cannot silently remove the
  headers.
- Run the full dependency-pinned baseline, workflow/lock mutations, dependency
  audit, diff hygiene, and secret scans.
