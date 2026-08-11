# KeyCast

A live keyboard-shortcut overlay for macOS, made for instructors who stream or record
software lessons. Every shortcut you press appears in the corner of the screen **with its
name**, so students see exactly what your hands just did — tuned for Adobe Photoshop and
Illustrator out of the box.

```
your screen ──────────────────────────────────┐
│                                             │
│         (Photoshop, Illustrator, …)         │
│                                             │
│                     ┌─────────────────────┐ │
│                     │ Cmd+Shift+S—Save As │ │
│                     └─────────────────────┘ │
└─────────────────────────────────────────────┘
```

No install, no dependencies — one Swift file that runs on any modern Mac.

## Run it

```bash
cd keycast
./run.sh
```

For stream days (compiled, faster startup):

```bash
cd keycast
./run.sh --build
```

Quit with **Ctrl+C** in the terminal. Drag the overlay anywhere with the mouse.

## First run — allow it to see the keyboard (one time)

```
./run.sh
   │
   ▼
macOS asks for permission
   │
   ▼
System Settings ▸ Privacy & Security ▸ Accessibility ▸ turn ON “Terminal”
   │
   ▼
overlay switches to “Ready…” by itself within ~2 seconds — no relaunch needed
```

## How it names your shortcuts

```
you press Cmd+J
   │
   ▼
which app is in front?
   ├── Photoshop    ──▶ mappings/photoshop.json    ──▶  “Duplicate Layer”
   ├── Illustrator  ──▶ mappings/illustrator.json  ──▶  (Illustrator’s names)
   └── anything else ─▶ mappings/global.json       ──▶  “Copy”, “Paste”, …
                              │
                              └── no match? shows just the keys:  Cmd+J
```

## Make it yours

The names live in plain-text JSON at [keycast/mappings/](keycast/mappings) — edit, relaunch, done.
Add another app with one new JSON file plus one line in `manifest.json`
(find an app's id with `osascript -e 'id of application "Adobe Photoshop 2025"'`).
Check your edits any time:

```bash
cd keycast
./run.sh --check-mappings
```

Heads-up: single letters like V/A/P (tool switching) are intentionally not shown — from
outside an app they're indistinguishable from typing, and you don't want typed text echoed
on stream.

## More

- [keycast/README.md](keycast/README.md) — full details and troubleshooting
- [keycast/DECISIONS.md](keycast/DECISIONS.md) & [keycast/SKILL-SEED.md](keycast/SKILL-SEED.md) — why it's built this way (the teaching trail)
- The earlier prototypes this grew out of are preserved on the `legacy-prototypes` branch as a teaching example.
