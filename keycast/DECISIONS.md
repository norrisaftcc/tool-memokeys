# KeyCast — Decision Log

Each entry records a real decision, the alternatives we rejected, and — because this project doubles as teaching material — a **Teaching note**: the transferable lesson, stated so it survives outside this repo.

---

## D1. Rebuild from spec; salvage one file, not the codebase

**Decision.** Start `keycast/` fresh, seeding only from `prototypes/hotkey-overlay.swift`. Ignore the other two prototypes (`mvp/*.py`, `static/keycast.html`) and the legacy test suite.

**Why.** A scout survey found three divergent, unfinished implementations of the same idea, none consolidated after a "Refactor v2" that moved code into `archive/` and broke every KeyCast test import (`ModuleNotFoundError: hotkey_panel_proto`). The Swift prototype was the only artifact whose *architecture* matched the goal: global event monitor + native floating window, zero dependencies.

**Teaching note.** When assessing a messy repo, grade artifacts on architecture, not completeness. A 235-line untested script with the right skeleton beats a larger, tested codebase pointed at the wrong problem. And a commit message claiming "comprehensive test suite" is a claim, not evidence — run the tests before you inherit them.

## D2. Why Swift (native), not Python/PyObjC, Electron, or a web page

**Decision.** One Swift file, Cocoa APIs, no third-party dependencies, runnable as a script (`swift KeyCast.swift`) or compiled (`swiftc`).

**Why.** The hardest requirement — *see every keystroke system-wide and float above every app* — lives at the OS layer. Swift reaches `NSEvent`, `NSWindow`, and `NSWorkspace` first-class. Python needs `pynput` + `pyobjc` (install/packaging burden for a non-technical user, and the repo's own Python attempts collected real bugs). Electron drags a ~200MB runtime to render one label. The repo's web prototype (`static/keycast.html`) proved the dead end empirically: a browser page can only hear keys while its own tab is focused — architecturally incapable of the job, no matter how polished.

**Teaching note.** Choose your stack by asking where the *hardest* requirement lives, and build in the layer that owns it. Every abstraction between you and that layer is a tax paid forever.

## D3. `NSEvent.addGlobalMonitorForEvents`, not `CGEventTap`

**Decision.** Observe keystrokes with the high-level global monitor.

**Why.** We only *read* events — we never modify, consume, or block them. `CGEventTap` is the heavier tool for intercepting/rewriting events and brings run-loop plumbing and a tap that macOS can disable under load. Both require Accessibility trust, so the tap buys nothing here.

**Teaching note.** Prefer the least-privileged API that satisfies the requirement. "Might need the powerful one later" is how prototypes accrete complexity they never use.

## D4. Chord logic driven by `keyDown` only — no press/release state machine

**Decision.** Build the displayed chord entirely from each `keyDown` event, whose `modifierFlags` snapshot is atomic. `flagsChanged` drives only the cosmetic "⌘⇧…" held-modifier preview.

**Why.** The repo's `mvp/minimal.py` demonstrates the failure mode: it tracked pressed keys in a list and cleared the *whole list* on any release — so releasing ⌘ before V (the common human timing) wiped the display. Modifier state machines invite exactly this class of ordering bug; the OS already hands us the resolved answer on every keypress.

**Teaching note.** If the platform delivers derived state atomically, consume it — don't re-derive it from an event stream you'll inevitably reorder in your head. Bugs live in the gaps between events.

## D5. One canonical chord formatter, used everywhere

**Decision.** A single `ChordFormatter` produces combo strings in fixed modifier order — ⌘ ⇧ ⌥ ⌃, then the key, no separators (`⌘⇧S`) — and it is the only code path that builds either the JSON lookup key or the on-screen label. `--check-mappings` warns on any JSON key that isn't in canonical form.

**Why.** The lookup joins two worlds: strings typed by a human into JSON and strings synthesized from live events. If they format independently, `⇧⌘S` vs `⌘⇧S` never match and the failure is *silent* — the overlay still works, just namelessly.

**Teaching note.** When a string is a join key across a data boundary, centralize its construction and validate stored keys against the same normalizer. Silent lookup misses are the worst bug class: nothing errors, value just quietly leaks away.

## D6. Data-driven per-app mappings via `manifest.json`

**Decision.** Resolve the frontmost app with `NSWorkspace.shared.frontmostApplication?.bundleIdentifier`, then look up bundle id → mapping file in `mappings/manifest.json`; fall back to `global.json`. Supporting a new app (InDesign, Figma…) is a pure data change — new JSON file plus one manifest line, no recompile.

**Why.** Per-app *names* are the product's whole educational edge over KeyCastr, and the instructor — not a developer — is the person who knows her tools' shortcuts. The editing surface has to be hers.

**Teaching note.** Put the knowledge that domain experts own in data, and the mechanics in code. The seam between them (here: the manifest) is what makes the tool extensible by its actual user.

## D7. Bundle IDs are asserted, not verified — and the failure is soft

**Decision.** Ship `com.adobe.Photoshop` (capital P) and `com.adobe.illustrator` (lowercase i) as best-known values, with a documented verify step: `osascript -e 'id of application "Adobe Photoshop 2025"'` on the instructor's machine.

**Why.** No Adobe install exists in the dev environment. A wrong bundle id doesn't crash — lookups just fall through to `global.json`, so the symptom is "app names missing," which the README's troubleshooting section points straight at the manifest.

**Teaching note.** When you can't verify an external identifier, (1) make the failure degrade gracefully, (2) write the exact one-line check the end user can run, and (3) say out loud which values are unverified. Confidence labeling is part of the deliverable.

## D8. Permissions: prompt proactively, and re-create the dead monitor

**Decision.** Call `AXIsProcessTrustedWithOptions` with the prompt option at launch, show the untrusted state *in the overlay itself*, and run a ~2s repoll that — on the untrusted→trusted flip — tears down and re-creates the `NSEvent` global monitor.

**Why.** The old prototype just printed instructions to a terminal the user may never read. Worse gotcha: a global monitor created while the process is untrusted can stay *silently dead* even after the user grants permission — macOS historically re-evaluates trust for monitors only at creation. Recreating the monitor on the trust flip removes an entire class of "I granted it and nothing happens" support questions — the kind that would otherwise strike mid-livestream.

**Teaching note.** Permission UX is part of the feature, not an install note. And when an OS caches a capability check at object-creation time, "poll the flag" isn't enough — you must recreate the object.

## D9. Bare-letter tool shortcuts (V, A, P, …) are a non-goal, not an oversight

**Decision.** v1 shows only modifier chords. Adobe's single-letter tool switches are deliberately excluded.

**Why.** From a global monitor there is no reliable way to distinguish "pressed P to select the Pen tool" from "typed the letter P into a text layer or dialog." Showing every letter would spray the overlay with noise (and potentially echo sensitive typed text on stream).

**Teaching note.** Scope cuts should be *written down as decisions with reasons*, or they read as bugs to the next person. "Excluded because indistinguishable at this observation layer" is an answer; silence is a defect report waiting to be filed.

## D10. Headless verification designed in: `--check-mappings`

**Decision.** A flag, parsed before any `NSApplication` call, that loads and validates every mapping file, prints per-file counts and errors, and exits.

**Why.** The overlay's core loop needs a screen, an Accessibility grant, and a human eyeballing it — none automatable here. But the *data* pipeline (manifest resolution, JSON decoding, canonical-key validation) is the part the instructor will touch and break, and it can be tested over SSH in one second.

**Teaching note.** When a program's essence is un-automatable (GUI, hardware, permissions), carve out the largest testable subsystem and give it a headless entry point. "Some verification now" beats "full verification never" — and be explicit about what the passing check does *not* prove.

## D11. Display spelled-out modifier names, not Mac symbols (client amendment)

**Decision.** The overlay renders "Cmd+Shift+S — Save As", never "⌘⇧S". Internal JSON lookup keys keep the compact symbol form; only the display layer translates (⌘→Cmd, ⇧→Shift, ⌥→Opt, ⌃→Ctrl). Both renderings come from the same ordered-modifier logic in `ChordFormatter`, so D5's one-formatter invariant still holds.

**Why.** Direct feedback from the instructor: the symbols are no longer printed on Apple keyboards, so students watching the stream can't map ⌥ to a physical key. The overlay exists to teach; notation the audience can't decode is a failed lesson. Splitting display format from storage format let us take the amendment mid-build as a display-only change — zero churn in the mapping files.

**Teaching note.** Two lessons. Product: notation must match the audience's keyboard, not the platform's typographic tradition — test copy against the least-expert viewer. Engineering: separating a value's canonical/storage form from its presentation form is what makes late-arriving presentation requirements cheap; if we'd stored "Cmd+Shift+S" as the JSON key, this amendment would have rewritten every mapping file.

## D12. Hand-off hygiene: preserve the mess on a branch, ship a minimal main

**Decision.** Before handing the repo to the instructor, `main` was stripped to KeyCast plus a diagram-first top-level README; every prior artifact (quiz app, three prototypes, broken tests, planning docs) moved intact to the `legacy-prototypes` branch.

**Why.** The recipient is a non-developer: everything she sees on first clone should be either runnable or readable by her. But the mess has real value *as a teaching example* — it's the corpus this project's decision log keeps citing (D1, D2, D4). Git branches let both be true at once: a clean face and a preserved fossil record, with zero data loss and a one-command path back (`git switch legacy-prototypes`).

**Teaching note.** "Clean up the repo" almost never means "delete history" — it means curate the *default view*. Branches are free; use one as the museum so `main` can be the storefront. And write the pointer down (README, this entry), because an unadvertised museum might as well not exist.

---

*Follow-ups for later passes: hot-reload of mappings, menu-bar packaging, per-version Adobe shortcut audit with the instructor.*
