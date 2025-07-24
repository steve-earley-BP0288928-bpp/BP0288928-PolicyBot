#!/bin/bash

WEBPAGE_URL="http://localhost:5173"

# Function to check if iTerm is running
check_iterm() {
    if ! pgrep -f "iTerm" > /dev/null; then
        echo "Starting iTerm..."
        open -a iTerm
        sleep 2
    fi
}

# Start iTerm if not running
check_iterm

# && bash 'scripts/start_backend.sh'"
# && bash 'scripts/start_backend.sh'

# Create AppleScript to manage iTerm sessions
osascript <<EOF
tell application "iTerm"
    activate
    
    -- Start backend in one iTerm window
    set newWindow1 to (create window with default profile)
    tell current session of newWindow1
        write text "cd /Users/steve/chat-lse && conda activate chat-lse"
    end tell
    
    -- Start frontend in another iTerm window
    set newWindow2 to (create window with default profile)
    tell current session of newWindow2
        write text "cd /Users/steve/chat-lse && conda activate chat-lse && bash 'scripts/start_frontend.sh'"
    end tell
    
    -- Tail the log a third iTerm window
    set newWindow3 to (create window with default profile)
    tell current session of newWindow3
        write text "cd /Users/steve/chat-lse && tail -f 'app_log_2025-07-23.log'"
    end tell
    
end tell
EOF

# Wait a moment for iTerm to settle
sleep 5

# Open Safari with the specified webpage
echo "Opening Safari with webpage..."
osascript <<EOF
tell application "Safari"
    activate
    if (count of windows) = 0 then
        make new document at end of documents
    end if
    set URL of current tab of front window to "$WEBPAGE_URL"
end tell
EOF

echo "Setup complete!"
echo "- Script 1 running in iTerm window 1"
echo "- Script 2 running in iTerm window 2" 
echo "- Log file being tailed in iTerm window 3"
echo "- Safari opened with specified webpage"