#!/bin/bash

# Get current date for log file
LOG_DATE=$(date +"%Y-%m-%d")

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

# AppleScript to open separate iTerm sessions for the backend and frontend processes
osascript <<EOF
tell application "iTerm"
    activate
    
    -- Start the backend
    set newWindow1 to (create window with default profile)
    tell current session of newWindow1
        write text "PATH=/opt/anaconda3/bin:/opt/anaconda3/condabin:$PATH"
        write text "conda activate chat-lse"
        write text "cd /Users/steve/chat-lse"
        write text "sh scripts/start_backend.sh"
    end tell
    
    -- Start the frontend
    set newWindow2 to (create window with default profile)
    tell current session of newWindow2
        write text "PATH=/opt/anaconda3/bin:/opt/anaconda3/condabin:$PATH"
        write text "conda activate chat-lse"
        write text "cd /Users/steve/chat-lse"
        write text "sh scripts/start_frontend.sh"
    end tell
    
end tell
EOF

# Wait for the backend process to fully start
sleep 10

# AppleScript to tail the log file
osascript <<EOF
tell application "iTerm"
    activate
    
    -- Tail the log
    set newWindow3 to (create window with default profile)
    tell current session of newWindow3
        write text "cd /Users/steve/chat-lse/logs"
        write text "tail -f app_log_$LOG_DATE.log"
    end tell
end tell
EOF

# AppleScript to open Safari with the chat-lse interface
osascript <<EOF
tell application "Safari"
    activate
    if (count of windows) = 0 then
        make new document at end of documents
    end if
    set URL of current tab of front window to "http://localhost:5173"
end tell
EOF