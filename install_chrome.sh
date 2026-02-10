#!/bin/bash

# Mount the DMG file
echo "Mounting Chrome DMG..."
hdiutil attach /tmp/chrome.dmg -nobrowse

# Copy Chrome to Applications
echo "Installing Chrome to Applications folder..."
cp -r "/Volumes/Google Chrome/Google Chrome.app" /Applications/

# Unmount the DMG
echo "Cleaning up..."
hdiutil detach "/Volumes/Google Chrome" -force

echo "Chrome installation complete!"