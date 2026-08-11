# KeyCast v1

A Mac-only live keystroke overlay for instructors and streamers. It floats a
small always-on-top panel in the bottom-right corner of the screen and shows
the modifier chord you just pressed — with the shortcut's *name*, when it
knows one for the app you're in (e.g. Photoshop's `Cmd+Shift+S` becomes
"Cmd+Shift+S — Save As"). No third-party dependencies: one Swift file, Cocoa
+ ApplicationServices only.

## Quick start

```bash
cd keycast
./run.sh
```

That interprets `KeyCast.swift` directly — no build step. To compile and run
a binary instead (faster, useful for a long-running livestream):

```bash
./run.sh --build
```

This produces `build/keycast` (gitignored) and runs it.

Stop with Ctrl+C in the terminal, or quit the process another way — there's
no menu bar icon in v1.

## Accessibility permission

KeyCast needs to see keystrokes system-wide, which macOS gates behind
Accessibility access for whatever process is running it (usually your
terminal app).

1. Run `./run.sh`. macOS should prompt you to grant access automatically.
2. If it doesn't, or you dismissed the prompt: **System Settings → Privacy &
   Security → Accessibility**, then add your terminal app (Terminal.app,
   iTerm, etc.) and enable the toggle.
3. The overlay itself will say "Grant Accessibility access…" while it's
   waiting. It polls every ~2 seconds and should flip to "Ready…" and start
   working within a couple of seconds of you granting access — no need to
   quit and relaunch.
4. If it still shows nothing after granting access, relaunch `./run.sh` as a
   last resort.

## Display vs. lookup key format

The on-screen label spells out modifier names (`Cmd`, `Shift`, `Opt`,
`Ctrl`) joined with `+` — e.g. `Cmd+Shift+S — Save As` — because the ⌘ ⇧ ⌥ ⌃
symbols are no longer printed on Mac keyboards and students watching a
stream can't map them to a physical key.

Internally, and in every `mappings/*.json` file, shortcuts are still keyed
by the compact symbol form in canonical order (⌘ then ⇧ then ⌥ then ⌃, no
separator — e.g. `⌘⇧S`). Only the display layer translates one to the
other; you never need to write `Cmd+Shift+S` in a mapping file.

Symbol ↔ name legend:

| Symbol | Name  |
|--------|-------|
| ⌘      | Cmd   |
| ⇧      | Shift |
| ⌥      | Opt   |
| ⌃      | Ctrl  |

## Editing or adding shortcut mappings

Mappings live in `keycast/mappings/`:

- `manifest.json` — lists each app's bundle id and its mapping file, plus a
  `globalFile` fallback used when no app-specific entry matches.
- `photoshop.json`, `illustrator.json` — flat `{ "⌘⇧S": "Save As", ... }`
  objects, one per app.
- `global.json` — the same shape, used for any app (or when the frontmost
  app has no dedicated file).

To change a name or shortcut: edit the relevant JSON file and relaunch
KeyCast (mappings are loaded once at startup, not hot-reloaded).

To add a new app: create a new JSON file in `mappings/` in the same flat
`combo -> name` shape, using canonical key order (⌘⇧⌥⌃), then add an entry
to `manifest.json`'s `apps` array with that app's bundle id.

To find an app's bundle id, run this in Terminal with the app installed:

```bash
osascript -e 'id of application "Adobe Photoshop 2025"'
```

## A note on the seed data

The Photoshop and Illustrator entries in this repo were reformatted from
`data/shortcuts/productivity/adobe-creative-suite.json` and from general
knowledge of each app's default shortcuts. They have **not** been verified
against a live install. Adobe changes bindings between versions, and the
bundle ids in `manifest.json` (`com.adobe.Photoshop`, `com.adobe.illustrator`)
are best-known values, not confirmed on this machine — there's no Adobe
install in this dev environment. Verify both against your actual installed
version before relying on this for a live session.

## Troubleshooting

- **Names not showing for an app** — check that the app's bundle id in
  `manifest.json` matches what `osascript -e 'id of application "..."'`
  reports for your installed version. A mismatch fails silently: KeyCast
  just falls back to `global.json` (or shows the bare chord), it won't
  error.
- **Nothing shows at all** — see Accessibility permission above.
- **Validate your mapping files without launching the app**, e.g. after
  editing JSON by hand:

  ```bash
  ./run.sh --check-mappings
  # or, against a compiled binary:
  ./run.sh --build --check-mappings
  ```

  This loads every file referenced by `manifest.json`, prints entry counts,
  and flags decode errors or non-canonical modifier ordering in a mapping
  key. Exits 0 on success, 1 on any decode error — safe to run over SSH,
  since it never touches `NSApplication`.

## Why bare-letter tool shortcuts aren't shown

Adobe apps bind single letters to tools (`V` = Move, `A` = Direct Selection,
`P` = Pen, …). KeyCast v1 intentionally does not show these. A global key
monitor can't tell "pressed P to switch tools" apart from "typed the letter
P into a text layer or a dialog box" — showing every bare letter would spam
the overlay with noise, and risks echoing text you're typing on stream.
Only modifier chords (with ⌘/⌥/⌃, or ⇧ paired with one of those or a special
key like Tab/Space/Return/Delete/Esc) are displayed.
