---
status: completed
---

# Retire Client-Side Yelp JSONP

## Problem

The desktop and mobile event templates still exposed Yelp's retired v1
`business_review_search` endpoint through JSONP. The browser embedded a legacy
provider credential, executed the remote response as JavaScript, and assembled
untrusted provider fields into HTML. Yelp's current Places API uses private API
keys in bearer authorization and documents that those keys must remain secret,
so the integration cannot be safely modernized in client-side templates.

## Decision

- Remove the desktop place-search modal and mobile place-search page, including
  their launch controls, legacy credential, JSONP requests, and provider-built
  result markup.
- Preserve the rendering and voting behavior for suggestions already stored in
  the application.
- Revalidate stored suggestion URLs before rendering because legacy rows predate
  the current write-time HTTP(S) URL validation. Unsafe URLs render as plain
  suggestion names instead of links.
- Leave the authenticated `/suggest` storage endpoint in place for compatibility
  and a future reviewed server-mediated integration.
- Require any future provider search to keep credentials server-side, validate
  provider responses, and render returned data without HTML-string assembly.

## Verification

- Dependency-free contracts reject Yelp API URLs, the retired endpoint, the legacy
  credential, JSONP response execution, and restoration of the removed controls.
- Contracts require existing desktop suggestions, mobile places, and mobile
  messaging to remain rendered.
- A runtime test proves that an unsafe legacy suggestion URL is absent from the
  rendered event page while its suggestion name remains visible.
- `make check`
- `git diff --check`

## References

- https://docs.developer.yelp.com/docs/fusion-authentication
- https://docs.developer.yelp.com/docs/fusion-intro
