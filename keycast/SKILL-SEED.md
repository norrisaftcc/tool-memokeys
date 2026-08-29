# SKILL-SEED — raw material for a future reusable skill

This file is the "lambda version of what we did that was useful today": the session's transferable method, captured in proto-skill format so it can be lifted into a real skill (`SKILL.md` + frontmatter) with minimal rework. It is deliberately about the *method*, not KeyCast — KeyCast is the worked example.

---

## Draft frontmatter

```yaml
name: prototype-triage-and-native-rebuild
description: >
  Use when a repo holds one or more abandoned/divergent prototypes of a tool
  and you must decide whether to salvage or rebuild — then execute a minimal
  native rebuild with a pedagogical decision log. Especially suited to small
  macOS utilities needing OS-level access (global input, overlays, permissions).
```

## When to use

- A repo "sort of already does this" but has multiple competing prototypes, a refactor that was never finished, or tests that don't run.
- The target tool is small and its hardest requirement is OS-level (global key capture, always-on-top windows, privileged permissions).
- The work must leave behind teaching-quality documentation, not just code.

## Workflow

1. **Scout cheaply before touching anything.** Dispatch one read-only subagent (a cheaper model is fine) with a tight brief: layout, state of each prototype, does the claimed capability actually exist in code, do the tests run, verdict-with-justification. Demand file paths, forbid file dumps.
2. **Grade artifacts on architecture, not completeness.** Salvage the artifact whose *skeleton* matches the goal (right API, right process boundary), even if untested; discard polished code aimed at the wrong problem. Verify test-suite claims by running them — commit messages lie. (KeyCast: 235-line Swift script won over two larger Python apps and a web page that architecturally couldn't do the job.)
3. **Choose the stack by where the hardest requirement lives.** Identify the single hardest requirement; build in the layer that owns it natively; treat every intermediate dependency as a permanent tax. Write this rationale down (see D2).
4. **Design out the known bug classes before coding.** Mine the failed prototypes for their bugs and convert each into a design rule: atomic-state-over-state-machines (D4), one-formatter-for-join-keys (D5), soft-fail unverified identifiers (D7), recreate-capability-gated-objects-on-permission-flip (D8).
5. **Put expert-owned knowledge in data, mechanics in code.** If the end user is a non-developer who owns the domain knowledge, give them an editable data seam (manifest + JSON) so extension never requires a rebuild (D6).
6. **Carve out a headless verification path.** GUI/permission-gated cores can't be auto-tested; give the data/logic subsystem its own flag or entry point that runs over SSH, and state explicitly what a pass does not prove (D10).
7. **Keep the decision log as you go, not after.** ADR-style entries, each ending in a one-sentence transferable Teaching note. Scope cuts get logged as decisions with reasons, or they read as bugs later (D9).
8. **Delegate mechanical build-out to cheaper subagents; keep judgment in the main loop.** The spec, the verdict, and the docs are main-loop work; typing 400 lines against a fixed spec is not. Verify the delegate's output yourself (compile it, run the headless check, spot-read the invariants).

## Gotchas bank (macOS-flavored, from this session)

- Browser pages cannot observe system-wide keystrokes; a web prototype of a global overlay is a dead end by construction.
- `NSEvent.addGlobalMonitorForEvents` suffices for read-only observation; `CGEventTap` is only for intercepting/modifying. Both need Accessibility trust.
- A global monitor created while the process is *untrusted* can stay silently dead after permission is granted — recreate the monitor object on the trust flip; don't just poll the flag.
- `keyDown` events carry `modifierFlags` atomically — never rebuild chord state from press/release sequences (release-order bugs are near-guaranteed).
- Join-key strings (JSON key ↔ synthesized event string) need one canonical formatter plus a validator over stored data; mismatches fail silently.
- "Swift is built into macOS" is half-true: the *runtime* ships with the OS, but `swift`/`swiftc` require Xcode Command Line Tools (internet-gated install). For offline/air-gapped targets, ship a compiled binary — built `lipo`-universal (arm64 + x86_64) so the target's CPU doesn't matter — and remember gitignored `build/` output doesn't travel via clone.
- Adobe bundle-id casing is inconsistent (`com.adobe.Photoshop` vs `com.adobe.illustrator`); verify on the target machine with `osascript -e 'id of application "…"'`.
- Normalize raw key characters into display names *before* running validity rules on them — the old prototype compared raw `"\t"` against the string `"TAB"`, so its Shift+Tab/Space handling could never fire (latent bug found only on rebuild).
- Arrow keys arrive from `charactersIgnoringModifiers` as private-use Unicode scalars `0xF700`–`0xF703`, not printable characters — map them explicitly.
- Single-letter shortcuts are indistinguishable from typing at the global-monitor layer — excluding them is a decision to document, and also avoids echoing typed text on a livestream.

## Session shape (orchestration pattern)

One cheap probe agent per phase; the main loop keeps custody of the spec and the gaps between phases:

```
scout probe (read-only, sync) ─▶ verdict
        main loop: user stories
plan probe (sync) ─▶ design
        main loop: plan file ─▶ user approval
build probe (background) ◀─ SendMessage: mid-flight scoped amendment
        main loop (parallel): decision log + skill seed
        main loop: re-verify build output
```

Why it works: agents are disposable, conclusions persist; the plan↔build lacuna stays in the main loop, so late-arriving requirements get judged for blast radius there and injected into the running builder as a scoped delta instead of a restart; docs are written in parallel with the build because they depend on decisions (main-loop property), not on build output; every phase deposits into the decision log as it happens, making skill material a byproduct rather than a chore.

## Session log

*Append one entry per working session; this is the raw feed the skill gets distilled from.*

- **2026-08-11** — Scouted tool-memokeys (verdict: rebuild, seed from `prototypes/hotkey-overlay.swift`); wrote user stories (live chord overlay, per-app names for Photoshop/Illustrator, stream-friendly window, permission UX); planned and built KeyCast v1 (single Swift file + JSON mapping seam + `--check-mappings`); started DECISIONS.md D1–D10. Useful today: the scout-before-touching pattern, architecture-over-completeness salvage rule, and converting each legacy prototype's bug into a design rule. Mid-build client amendment (spell out modifier names on screen — students can't read ⌘⇧⌥ symbols) absorbed as a display-only change because storage keys and presentation were already separate layers (D11) — evidence for the storage/presentation split as a default posture. Post-build: verified independently (compile + `--check-mappings` + invariant spot-read); repo curated for hand-off — legacy mess preserved on `legacy-prototypes` branch as the teaching corpus, `main` reduced to KeyCast + a diagram-first README (D12). User feedback captured: shape-of-the-work diagrams are high-value — produce them proactively.
- **2026-08-29** — First real-corpus test of the distilled skill: a fresh Sonnet, blinded (skill's worked-example line stripped, worktree pinned to `legacy-prototypes` so `keycast/` didn't exist), triaged the fossil corpus against the original brief. Result: reproduced the rebuild verdict, seed file, web-veto, broken-test discovery, and all four skill-carried design moves (data seam, headless flag, monitor-recreate, simplest-v1) — and exceeded the original session twice (spotted that the "17/17 passing" suite tests a Python *reimplementation* of the Swift logic, and found a real failing data test). One miss: graded the seed file's filter block "correct" without catching the latent `"\t"` vs `"TAB"` bug sitting in it. REFACTOR applied to the skill: (1) audit the *salvaged* file against the gotchas table, not just the dead ones; (2) grade artifacts against the client's brief, not the repo's own PRD ambitions; (3) engineering theater (generated test reports, simulated reviews) is a claim, not evidence. Lesson: a blind rep on the real corpus grades the skill *and* re-audits the original session for free.
- **2026-08-11 (later)** — Distilled this seed into a real personal skill: `~/.claude/skills/triaging-and-rebuilding-prototypes/SKILL.md`, via skill-TDD (one Sonnet rep per phase). RED finding worth keeping: the no-skill baseline already handled the *judgment* half well (architecture-over-completeness, distrust of test claims, web-veto) — so the skill was written lean, carrying only what the baseline actually missed: the silently-dead-monitor permission trap, the headless verification entry point, the expert-owned data seam, and the simplest-runnable-v1 bias, plus the full gotchas table as reference. GREEN rep with the skill closed all four gaps (it even invented a manual test for the monitor-recreation path). Lesson: distill to the *delta* over baseline competence, not the whole method.
