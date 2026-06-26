---
title: Message Rendering XSS
date: 2026-06-25
type: implementation-plan
status: completed
---

# Message Rendering XSS

## Problem

The message API returns decoded user content. Both desktop and mobile event
templates concatenated `val.msg` into an HTML string and appended that markup to
the document, allowing stored message content to create executable elements.

## Requirements

- Preserve the existing message API, storage encoding, ordering, styling, and
  owner-only delete controls.
- Build message list elements through DOM APIs in both event templates.
- Assign decoded message and date values through `.text()` rather than HTML
  interpolation.
- Keep profile image URLs on HTTPS and encode the user-id path component.
- Return the message API as non-sniffable JSON for direct navigation.
- Add a static contract that rejects message interpolation into markup.

## Verification

- RED: the new contract failed because `templates/event.html` did not assign
  `val.msg` through a text API; the mobile template contained the same sink.
- GREEN: both templates construct list items and assign messages through
  `.text(val.msg)`; the static suite passes with 29 contracts.
- The message API sets `application/json; charset=UTF-8` and
  `X-Content-Type-Options: nosniff`; hostile decoded script content remains data.
- Full dependency-pinned `make check` passes with 29 static contracts, 38 runtime
  tests, 31 workflow mutations, 23 dependency-lock mutations, lint, and Make
  authority tests.
- Independent desktop and mobile `.html(val.msg)` mutations are rejected.
- Independent review found and verified the direct-navigation MIME hardening;
  final re-review, exact-head Codex review, and hosted CI remain before merge.
