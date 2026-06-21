# Make Authority Isolation

## Status: Completed

## Context

WillBeOut rooted its file arguments, but GNU Make still accepted caller-
controlled Python expressions, shell state, startup files, unsafe execution
modes, later public recipe replacement, and recursive cleanup authority.

## Implementation

- Froze the literal Python executable, `/bin/sh`, and canonical repository root
  for all eight public verification targets.
- Rejected startup files, replaced Makefile lists, parenthesized and braced
  executable Make syntax, non-executing modes, and later single-colon recipes.
- Added an executable adversarial harness, removed recursive cleanup, and bound
  hosted verification to `/usr/bin/make check`.

## Verification

- Repository-root and external-directory `/usr/bin/make check` pass 28 static
  contracts, 36 runtime tests, 21 workflow mutations, 23 dependency-lock
  mutations, and 40 target/root/shell authority cases in the hash-locked Python
  environment.
- The authority harness also covers cleanup containment, hostile literal paths,
  startup and Makefile-list boundaries, later target variables, PATH selection,
  and ten unsafe Make modes.

## Trust Boundary

GNU Make parses earlier startup files before this Makefile can reject them. A
caller who selects the default `python3` also controls `PATH`; hosted checks
install the hash-verified lock into the reviewed Python runtime before invoking
the fixed system Make executable.

## Scope Boundary

This change does not alter application routes, templates, database behavior,
OAuth/session policy, dependencies, or lockfile bytes. No production secrets or
live Facebook/MySQL services are used during verification.
