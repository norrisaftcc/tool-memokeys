#!/bin/bash

# Quick launcher for the hotkey overlay

echo "🚀 Starting Hotkey Overlay..."
echo ""
echo "⚠️  IMPORTANT: You'll need to grant Accessibility permissions"
echo "   System Preferences > Security & Privacy > Privacy > Accessibility"
echo "   Add Terminal (or your terminal app) to the list"
echo ""
echo "Press Ctrl+C to stop the overlay"
echo "-----------------------------------"
echo ""

# Make the script executable and run it
chmod +x hotkey-overlay.swift
./hotkey-overlay.swift
