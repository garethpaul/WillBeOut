# WillBeOut HTTPS Template Integrations

## Status: Completed

## Context

The legacy templates loaded active JavaScript, CSS, Facebook, Yelp, and profile
URLs over plain HTTP. Standards namespace and DTD strings are historical markup,
but runtime browser integrations should use HTTPS to avoid mixed content and
request tampering.

## Objectives

- Replace active template-side external HTTP integrations with HTTPS.
- Leave standards namespace, DTD, and vendored license references untouched.
- Add a dependency-free checker contract so active HTTP template integrations
  do not return.

## Work Completed

- Replaced jQuery Mobile, jQuery, Facebook SDK, Facebook profile, WillBeOut
  share, and Yelp JSONP URLs with HTTPS equivalents.
- Verified the jQuery, jQuery Mobile, Facebook SDK, and Yelp HTTPS endpoints
  respond over TLS on June 10, 2026.
- Extended the WillBeOut contract checker to reject those active HTTP template
  integration prefixes.
- Updated README, VISION, SECURITY, and CHANGES with the HTTPS baseline.

## Verification

- `curl -L -I --max-time 15 https://code.jquery.com/jquery-1.7.1.min.js`
- `curl -L -I --max-time 15 https://code.jquery.com/mobile/1.1.1/jquery.mobile-1.1.1.min.css`
- `curl -L -I --max-time 15 https://connect.facebook.net/en_US/all.js`
- `curl -L -I --max-time 15 'https://api.yelp.com/business_review_search?'`
- `make check`
- `git diff --check`

## Follow-Up Candidates

- Replace the retired Yelp v1 JSONP integration with a server-side, credentialed
  API path if this app is revived.
