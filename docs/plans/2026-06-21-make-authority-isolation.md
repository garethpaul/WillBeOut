# Make Authority Isolation

## Status: Completed

## Context

The repository rooted its file arguments, but GNU Make still accepted caller-
controlled Python expressions, shell state, startup files, unsafe modes, and
later public recipe replacement. Those inputs could redirect cleanup or make a
verification run execute different commands than the checked-in gate.
Startup makefiles can run parse-time Make functions before the repository Makefile rejects them.

## Implementation

- Froze the literal Python executable, `/bin/sh`, and canonical repository root
  for every public verification target.
- Rejected startup files, replaced Makefile lists, executable Make syntax,
  non-executing or error-ignoring modes, and later single-colon recipes.
- Recorded caller-supplied later makefiles, later override directives, and
  double-colon public recipe appends as outside the local Make trust boundary.
- Added an adversarial authority harness and bound hosted verification to
  `/usr/bin/make check`.

## Verification

- Repository-root and external-directory `make check` run 28 static contracts,
  36 no-network runtime tests, 21 workflow mutations, 23 dependency-lock
  mutations, cleanup, and the authority harness.
- The authority harness covers 40 target/root/shell combinations, a hostile
  literal Python path, eight raw Make-syntax controls, two startup parse-time
  boundary reproductions, Makefile-list boundaries, eight later single-colon
  replacements, eight later double-colon append reproductions, a later override
  fake-shell boundary reproduction, cleanup containment, and ten unsupported
  execution modes.

## Trust Boundary

GNU Make parses an earlier startup file before this Makefile can reject it, and
an explicit later `override` directive remains caller authority. A caller who
chooses the default `python3` still controls `PATH`; hosted verification installs
the reviewed Python runtime before invoking the fixed system Make executable.
Caller-supplied later makefiles, including double-colon public recipes and later override directives, are outside the local Make trust boundary.

## Scope Boundary

This change does not alter application code, templates, JavaScript, database
behavior, dependencies, deployment configuration, credentials, or public APIs.
Live Meta OAuth and MySQL behavior remain credentialed integration boundaries.
