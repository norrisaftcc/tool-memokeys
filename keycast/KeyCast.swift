#!/usr/bin/swift

import Cocoa
import ApplicationServices

// MARK: - ChordFormatter

/// The ONLY place chord combos are formatted. Two renderings share one
/// ordered-modifier list so they can never drift apart:
///   - `comboKey`      -> canonical, symbol-based, no separator ("⌘⇧S"). Used as
///                        the JSON lookup key and stored in mappings/*.json.
///   - `displayString` -> spelled-out, "+"-joined ("Cmd+Shift+S"). Used only for
///                        the on-screen label (students don't recognize ⌘⇧⌥⌃).
enum ChordFormatter {

    /// Canonical order: ⌘ ⇧ ⌥ ⌃, then the key.
    private static let modifierOrder: [(flag: NSEvent.ModifierFlags, symbol: String, name: String)] = [
        (.command, "⌘", "Cmd"),
        (.shift, "⇧", "Shift"),
        (.option, "⌥", "Opt"),
        (.control, "⌃", "Ctrl")
    ]

    private static func activeModifiers(_ modifiers: NSEvent.ModifierFlags) -> [(symbol: String, name: String)] {
        return modifierOrder.filter { modifiers.contains($0.flag) }.map { ($0.symbol, $0.name) }
    }

    /// Canonical, symbol-based combo string used for mapping lookups (e.g. "⌘⇧S").
    static func comboKey(modifiers: NSEvent.ModifierFlags, key: String) -> String {
        let symbols = activeModifiers(modifiers).map { $0.symbol }
        return symbols.joined() + key
    }

    /// Spelled-out combo string for on-screen display (e.g. "Cmd+Shift+S").
    static func displayString(modifiers: NSEvent.ModifierFlags, key: String) -> String {
        let names = activeModifiers(modifiers).map { $0.name }
        return (names + [key]).joined(separator: "+")
    }

    /// Spelled-out preview of only the held modifiers, no key (e.g. "Cmd+Shift").
    static func modifierPreview(modifiers: NSEvent.ModifierFlags) -> String {
        return activeModifiers(modifiers).map { $0.name }.joined(separator: "+")
    }

    /// Maps raw characters from `charactersIgnoringModifiers` to a display name.
    /// Special keys get names (SPACE/TAB/RETURN/ESC/DELETE/arrows); letters are
    /// uppercased; everything else passes through uppercased.
    static func keyDisplayName(_ key: String) -> String {
        switch key {
        case " ": return "SPACE"
        case "\t": return "TAB"
        case "\r", "\n": return "RETURN"
        case String(UnicodeScalar(UInt8(27))): return "ESC"
        case String(UnicodeScalar(UInt8(127))): return "DELETE"
        case String(UnicodeScalar(0xF700)!): return "↑"
        case String(UnicodeScalar(0xF701)!): return "↓"
        case String(UnicodeScalar(0xF702)!): return "←"
        case String(UnicodeScalar(0xF703)!): return "→"
        default: return key.uppercased()
        }
    }

    /// True if modifiers are meaningful enough to show a combo: needs a primary
    /// modifier (⌘/⌥/⌃), or ⇧ paired with a primary modifier or a special key
    /// (SPACE/TAB/RETURN/DELETE/ESC).
    static func hasValidModifiers(modifiers: NSEvent.ModifierFlags, key: String) -> Bool {
        let hasPrimaryModifier = modifiers.contains(.command) ||
                                  modifiers.contains(.option) ||
                                  modifiers.contains(.control)
        let hasMeaningfulShift = modifiers.contains(.shift) &&
                                  (hasPrimaryModifier || isSpecialShiftKey(key))
        return hasPrimaryModifier || hasMeaningfulShift
    }

    /// True if any primary modifier (⌘/⌥/⌃) is held — used to gate the transient
    /// "held modifier" preview shown on `.flagsChanged`. Bare ⇧ alone is not
    /// meaningful on its own.
    static func hasAnyMeaningfulModifier(modifiers: NSEvent.ModifierFlags) -> Bool {
        return modifiers.contains(.command) ||
               modifiers.contains(.option) ||
               modifiers.contains(.control)
    }

    private static func isSpecialShiftKey(_ key: String) -> Bool {
        let specialKeys = ["TAB", "SPACE", "RETURN", "DELETE", "ESC"]
        return specialKeys.contains(key)
    }

    /// Re-orders any combo of ⌘⇧⌥⌃ symbols (in whatever order they appear) plus a
    /// trailing key into canonical order. Used only to validate stored mapping
    /// keys — never to build a combo from a live event.
    static func normalizeComboOrder(_ combo: String) -> String {
        let symbolSet = Set(modifierOrder.map { $0.symbol })
        var present = Set<Character>()
        var rest = ""
        for ch in combo {
            if symbolSet.contains(String(ch)) {
                present.insert(ch)
            } else {
                rest.append(ch)
            }
        }
        var result = ""
        for m in modifierOrder where present.contains(Character(m.symbol)) {
            result += m.symbol
        }
        result += rest
        return result
    }
}

// MARK: - MappingStore

/// Loads mappings/manifest.json plus every referenced per-app file and the
/// global fallback file, once, into memory.
final class MappingStore {

    private struct ManifestApp: Decodable {
        let bundleId: String
        let file: String
    }

    private struct Manifest: Decodable {
        let apps: [ManifestApp]
        let globalFile: String
    }

    private var perApp: [String: [String: String]] = [:]
    private var global: [String: String] = [:]
    private var reportLines: [String] = []
    private(set) var hasErrors: Bool = false

    init(mappingsDir: URL) throws {
        let manifestURL = mappingsDir.appendingPathComponent("manifest.json")
        let manifestData = try Data(contentsOf: manifestURL)
        let manifest = try JSONDecoder().decode(Manifest.self, from: manifestData)

        for app in manifest.apps {
            let fileURL = mappingsDir.appendingPathComponent(app.file)
            let dict = load(fileURL: fileURL, label: "\(app.bundleId) -> \(app.file)")
            if let dict = dict {
                perApp[app.bundleId] = dict
            }
        }

        let globalURL = mappingsDir.appendingPathComponent(manifest.globalFile)
        if let dict = load(fileURL: globalURL, label: "global -> \(manifest.globalFile)") {
            global = dict
        }
    }

    /// Loads one flat combo->name JSON file, appending a report line. Decode
    /// failures are captured (not thrown) so one bad file doesn't sink the rest;
    /// `hasErrors` is set so callers can still fail the process appropriately.
    private func load(fileURL: URL, label: String) -> [String: String]? {
        do {
            let data = try Data(contentsOf: fileURL)
            let dict = try JSONDecoder().decode([String: String].self, from: data)
            reportLines.append("\(fileURL.path): \(dict.count) entries, 0 decode errors")
            for key in dict.keys.sorted() {
                let canonical = ChordFormatter.normalizeComboOrder(key)
                if canonical != key {
                    reportLines.append("  WARNING: non-canonical modifier order '\(key)' (expected '\(canonical)') in \(fileURL.path)")
                }
            }
            return dict
        } catch {
            hasErrors = true
            reportLines.append("\(fileURL.path): FAILED to load/decode - \(error)")
            return nil
        }
    }

    /// Per-app dict first, then global, else nil.
    func name(bundleId: String?, combo: String) -> String? {
        if let bundleId = bundleId, let dict = perApp[bundleId], let match = dict[combo] {
            return match
        }
        return global[combo]
    }

    func validationReport() -> String {
        return reportLines.joined(separator: "\n")
    }
}

// MARK: - Mappings dir resolution

/// Resolves the mappings directory, in order:
///   1. KEYCAST_MAPPINGS_DIR env var, if it exists on disk.
///   2. "mappings" next to CommandLine.arguments[0], resolving arg0 relative to
///      cwd and resolving symlinks (works for `swift KeyCast.swift`, where arg0
///      is the script path, and for a compiled binary).
///   3. "./mappings" relative to cwd.
func resolveMappingsDir() -> URL {
    let fm = FileManager.default

    if let envDir = ProcessInfo.processInfo.environment["KEYCAST_MAPPINGS_DIR"] {
        let url = URL(fileURLWithPath: envDir)
        if fm.fileExists(atPath: url.path) {
            return url
        }
    }

    let cwd = fm.currentDirectoryPath
    let arg0 = CommandLine.arguments.first ?? ""
    let arg0URL: URL
    if arg0.hasPrefix("/") {
        arg0URL = URL(fileURLWithPath: arg0)
    } else {
        arg0URL = URL(fileURLWithPath: cwd).appendingPathComponent(arg0)
    }
    let resolvedArg0 = arg0URL.resolvingSymlinksInPath()
    let candidate = resolvedArg0.deletingLastPathComponent().appendingPathComponent("mappings")
    if fm.fileExists(atPath: candidate.path) {
        return candidate
    }

    return URL(fileURLWithPath: "mappings", relativeTo: URL(fileURLWithPath: cwd, isDirectory: true)).standardizedFileURL
}

// MARK: - AccessibilityPermission

enum AccessibilityPermission {
    static func isTrusted(prompt: Bool) -> Bool {
        let options = [kAXTrustedCheckOptionPrompt.takeUnretainedValue() as String: prompt] as CFDictionary
        return AXIsProcessTrustedWithOptions(options)
    }
}

// MARK: - OverlayWindow

/// Borderless, floating, click-through-draggable overlay window pinned to the
/// bottom-right corner of the main screen.
class OverlayWindow: NSWindow {
    init() {
        super.init(
            contentRect: NSRect(x: 0, y: 0, width: 260, height: 80),
            styleMask: [.borderless, .nonactivatingPanel],
            backing: .buffered,
            defer: false
        )

        self.level = .floating
        self.collectionBehavior = [.canJoinAllSpaces, .stationary]
        self.backgroundColor = NSColor.black.withAlphaComponent(0.8)
        self.isOpaque = false
        self.hasShadow = true
        self.isMovableByWindowBackground = true

        if let screen = NSScreen.main {
            let screenFrame = screen.visibleFrame
            self.setFrameOrigin(NSPoint(
                x: screenFrame.maxX - self.frame.width - 20,
                y: screenFrame.minY + 20
            ))
        }
    }
}

// MARK: - HotkeyView

class HotkeyView: NSView {
    let label = NSTextField()

    override init(frame: NSRect) {
        super.init(frame: frame)

        label.isEditable = false
        label.isBordered = false
        label.backgroundColor = .clear
        label.textColor = .white
        label.alignment = .center
        label.font = NSFont.systemFont(ofSize: 14, weight: .medium)
        label.stringValue = "Ready…"
        label.lineBreakMode = .byWordWrapping
        label.maximumNumberOfLines = 2

        self.addSubview(label)
        label.translatesAutoresizingMaskIntoConstraints = false
        NSLayoutConstraint.activate([
            label.centerXAnchor.constraint(equalTo: self.centerXAnchor),
            label.centerYAnchor.constraint(equalTo: self.centerYAnchor),
            label.widthAnchor.constraint(equalTo: self.widthAnchor, constant: -20)
        ])
    }

    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }

    func updateHotkey(_ text: String) {
        DispatchQueue.main.async {
            self.label.stringValue = text
        }
    }
}

// MARK: - HotkeyMonitor

final class HotkeyMonitor {
    private let view: HotkeyView
    private let mappingStore: MappingStore
    private var eventMonitor: Any?
    private var hideTimer: Timer?
    private var trustPollTimer: Timer?
    private var isTrusted: Bool

    init(view: HotkeyView, mappingStore: MappingStore) {
        self.view = view
        self.mappingStore = mappingStore
        self.isTrusted = AccessibilityPermission.isTrusted(prompt: false)

        addMonitor()
        if !isTrusted {
            view.updateHotkey("Grant Accessibility access…")
        }
        startTrustPolling()
    }

    deinit {
        if let m = eventMonitor {
            NSEvent.removeMonitor(m)
        }
        hideTimer?.invalidate()
        trustPollTimer?.invalidate()
    }

    private func addMonitor() {
        eventMonitor = NSEvent.addGlobalMonitorForEvents(
            matching: [.keyDown, .flagsChanged],
            handler: { [weak self] event in
                self?.handleEvent(event)
            }
        )
    }

    /// A global monitor created while the process is untrusted can stay
    /// silently dead even after the user grants Accessibility access — macOS
    /// only re-evaluates trust for a monitor at creation time. So on the
    /// untrusted -> trusted flip we tear down and recreate the monitor object
    /// (not just re-check the flag).
    private func startTrustPolling() {
        trustPollTimer = Timer.scheduledTimer(withTimeInterval: 2.0, repeats: true) { [weak self] _ in
            self?.repollTrust()
        }
    }

    private func repollTrust() {
        guard !isTrusted else { return }
        guard AccessibilityPermission.isTrusted(prompt: false) else { return }

        if let m = eventMonitor {
            NSEvent.removeMonitor(m)
        }
        addMonitor()
        isTrusted = true
        view.updateHotkey("Ready…")
    }

    func handleEvent(_ event: NSEvent) {
        hideTimer?.invalidate()
        let modifiers = event.modifierFlags

        if event.type == .keyDown {
            if let rawChars = event.charactersIgnoringModifiers {
                let keyName = ChordFormatter.keyDisplayName(rawChars)
                if ChordFormatter.hasValidModifiers(modifiers: modifiers, key: keyName) {
                    let lookupCombo = ChordFormatter.comboKey(modifiers: modifiers, key: keyName)
                    let display = ChordFormatter.displayString(modifiers: modifiers, key: keyName)
                    let bundleId = NSWorkspace.shared.frontmostApplication?.bundleIdentifier
                    if let name = mappingStore.name(bundleId: bundleId, combo: lookupCombo) {
                        view.updateHotkey("\(display) — \(name)")
                    } else {
                        view.updateHotkey(display)
                    }
                }
            }
        } else if event.type == .flagsChanged {
            if ChordFormatter.hasAnyMeaningfulModifier(modifiers: modifiers) {
                let preview = ChordFormatter.modifierPreview(modifiers: modifiers)
                view.updateHotkey(preview + "…")
            }
        }

        hideTimer = Timer.scheduledTimer(withTimeInterval: 2.0, repeats: false) { [weak self] _ in
            self?.view.updateHotkey("")
        }
    }
}

// MARK: - AppDelegate

final class AppDelegate: NSObject, NSApplicationDelegate {
    private let mappingStore: MappingStore
    private var window: OverlayWindow!
    private var hotkeyView: HotkeyView!
    private var monitor: HotkeyMonitor!

    init(mappingStore: MappingStore) {
        self.mappingStore = mappingStore
    }

    func applicationDidFinishLaunching(_ notification: Notification) {
        window = OverlayWindow()
        hotkeyView = HotkeyView(frame: window.contentView!.bounds)
        window.contentView = hotkeyView
        window.orderFront(nil)

        monitor = HotkeyMonitor(view: hotkeyView, mappingStore: mappingStore)

        print("KeyCast is running. The overlay floats in the bottom-right corner.")
        print("If nothing appears when you press a chord, grant Accessibility access")
        print("to your terminal in System Settings > Privacy & Security > Accessibility.")
    }
}

// MARK: - main

let arguments = CommandLine.arguments

if arguments.contains("--check-mappings") {
    // Headless path: must never touch NSApplication so it can run over SSH.
    let mappingsDir = resolveMappingsDir()
    do {
        let store = try MappingStore(mappingsDir: mappingsDir)
        print("Mappings dir: \(mappingsDir.path)")
        print(store.validationReport())
        if store.hasErrors {
            print("FAILED: one or more mapping files had decode errors.")
            exit(1)
        } else {
            print("OK: all mapping files loaded cleanly.")
            exit(0)
        }
    } catch {
        print("FAILED: could not load manifest at \(mappingsDir.path): \(error)")
        exit(1)
    }
} else {
    let mappingsDir = resolveMappingsDir()
    let mappingStore: MappingStore
    do {
        mappingStore = try MappingStore(mappingsDir: mappingsDir)
    } catch {
        FileHandle.standardError.write("KeyCast: failed to load mappings from \(mappingsDir.path): \(error)\n".data(using: .utf8)!)
        exit(1)
    }

    let app = NSApplication.shared
    _ = AccessibilityPermission.isTrusted(prompt: true)

    let delegate = AppDelegate(mappingStore: mappingStore)
    app.delegate = delegate
    app.run()
}
