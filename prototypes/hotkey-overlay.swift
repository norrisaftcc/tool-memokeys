#!/usr/bin/swift

import Cocoa
import Carbon

// Simple floating overlay window
class OverlayWindow: NSWindow {
    init() {
        super.init(
            contentRect: NSRect(x: 0, y: 0, width: 200, height: 80),
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
        
        // Position in bottom-right corner
        if let screen = NSScreen.main {
            let screenFrame = screen.visibleFrame
            self.setFrameOrigin(NSPoint(
                x: screenFrame.maxX - self.frame.width - 20,
                y: screenFrame.minY + 20
            ))
        }
    }
}

// Label for displaying hotkeys
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
        label.stringValue = "Ready..."
        
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

// Monitor for global hotkeys
class HotkeyMonitor {
    let view: HotkeyView
    var eventMonitor: Any?
    var currentModifiers: String = ""
    var hideTimer: Timer?
    
    init(view: HotkeyView) {
        self.view = view
        startMonitoring()
    }
    
    func startMonitoring() {
        // Monitor both key down and flags changed events
        eventMonitor = NSEvent.addGlobalMonitorForEvents(
            matching: [.keyDown, .flagsChanged],
            handler: { [weak self] event in
                self?.handleEvent(event)
            }
        )
    }
    
    func handleEvent(_ event: NSEvent) {
        hideTimer?.invalidate()
        
        let modifiers = event.modifierFlags
        var keys: [String] = []
        
        // Check modifiers
        if modifiers.contains(.command) { keys.append("⌘") }
        if modifiers.contains(.shift) { keys.append("⇧") }
        if modifiers.contains(.option) { keys.append("⌥") }
        if modifiers.contains(.control) { keys.append("⌃") }
        
        // For keyDown events, add the actual key
        if event.type == .keyDown {
            if let chars = event.charactersIgnoringModifiers?.uppercased() {
                keys.append(chars)
                
                // Add description for common actions
                let description = getActionDescription(modifiers: keys, key: chars)
                let display = keys.joined(separator: " + ") + "\n" + description
                view.updateHotkey(display)
            }
        } else if !keys.isEmpty {
            // Just show modifiers being held
            currentModifiers = keys.joined(separator: " + ")
            view.updateHotkey(currentModifiers + "\n...")
        }
        
        // Hide after 2 seconds of no activity
        hideTimer = Timer.scheduledTimer(withTimeInterval: 2.0, repeats: false) { _ in
            self.view.updateHotkey("")
        }
    }
    
    func getActionDescription(modifiers: [String], key: String) -> String {
        let combo = modifiers.joined() + key
        
        // Common macOS shortcuts
        switch combo {
        case "⌘C": return "Copy"
        case "⌘V": return "Paste"
        case "⌘X": return "Cut"
        case "⌘Z": return "Undo"
        case "⌘⇧Z": return "Redo"
        case "⌘S": return "Save"
        case "⌘⇧S": return "Save As"
        case "⌘O": return "Open"
        case "⌘N": return "New"
        case "⌘W": return "Close"
        case "⌘Q": return "Quit"
        case "⌘A": return "Select All"
        case "⌘F": return "Find"
        case "⌘G": return "Find Next"
        case "⌘⇧G": return "Find Previous"
        case "⌘P": return "Print"
        case "⌘,": return "Preferences"
        case "⌘TAB": return "Switch App"
        case "⌘`": return "Switch Window"
        case "⌘SPACE": return "Spotlight"
        case "⌘⌥D": return "Show/Hide Dock"
        case "⌘⌥ESC": return "Force Quit"
        case "⌘⇧3": return "Screenshot"
        case "⌘⇧4": return "Screenshot Selection"
        case "⌘⇧5": return "Screenshot/Recording"
        default: return ""
        }
    }
}

// App delegate
class AppDelegate: NSObject, NSApplicationDelegate {
    var window: OverlayWindow!
    var hotkeyView: HotkeyView!
    var monitor: HotkeyMonitor!
    
    func applicationDidFinishLaunching(_ notification: Notification) {
        window = OverlayWindow()
        hotkeyView = HotkeyView(frame: window.contentView!.bounds)
        window.contentView = hotkeyView
        window.orderFront(nil)
        
        monitor = HotkeyMonitor(view: hotkeyView)
        
        print("Hotkey overlay is running! Press Ctrl+C in terminal to quit.")
        print("The overlay will show in the bottom-right corner of your screen.")
        print("NOTE: You'll need to grant Accessibility permissions when prompted.")
    }
}

// Main
let app = NSApplication.shared
let delegate = AppDelegate()
app.delegate = delegate
app.run()
