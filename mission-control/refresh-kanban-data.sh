#!/bin/bash

# Define paths
KANBAN_JSON="/Users/karst/.openclaw/workspace/kanban-board.json"
STORE_DIR="/Users/karst/.openclaw/workspace/mission-control/src/store"
TMP_FILE="/tmp/default-board.txt"

# Extract just the JSON data from kanban-board.json
cat "$KANBAN_JSON" > "$TMP_FILE"

# Replace the default board data in kanbanStore.ts
sed -i.bak "s/const defaultBoard: Board = {.*columns: \[/const defaultBoard: Board = $(cat $TMP_FILE | sed 's/\//\\\//g')/" "$STORE_DIR/kanbanStore.ts"

echo "Updated the default board data in kanbanStore.ts"
echo "Please restart the Mission Control dashboard to see changes"