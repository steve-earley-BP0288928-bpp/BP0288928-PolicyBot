#!/bin/bash

# Get current date for log file
LOG_DATE=$(date +"%Y-%m-%d")

# Bounds for the windows
# These fixed values are for iMac in default display configuration
# BACKEND_BOUNDS="{1280, 0, 2560, 500}" # Top Right with some separation
# FRONTEND_BOUNDS="{1280, 540, 2560, 700}" # Middle Right with some separation
# LOGTAIL_BOUNDS="{1280, 720, 2560, 1440}" # Bottom Right
# SAFARI_BOUNDS="{0, 0, 1280, 1440}" # Left

RESOLUTION=$( osascript -e 'tell application "Finder" to get bounds of window of desktop' )
WIDTH=$(echo "$RESOLUTION" | awk -F', ' '{print $3}')
HEIGHT=$(echo "$RESOLUTION" | awk -F', ' '{print $4}')

BACKEND_BOUNDS="{$((WIDTH/2)), 0, ${WIDTH}, $((HEIGHT*35/100))}"
FRONTEND_BOUNDS="{$((WIDTH/2)), $((HEIGHT*38/100)), ${WIDTH}, $((HEIGHT*49/100))}"
LOGTAIL_BOUNDS="{$((WIDTH/2)), $((HEIGHT/2)), ${WIDTH}, ${HEIGHT}}"
SAFARI_BOUNDS="{0, 0, $((WIDTH/2)), ${HEIGHT}}"

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

    tell newWindow1
        set bounds to $BACKEND_BOUNDS
    end tell

    tell current session of newWindow1
        write text "PATH=/opt/anaconda3/bin:/opt/anaconda3/condabin:$PATH"
        write text "conda activate chat-lse"
        write text "cd /Users/steve/chat-lse"
        write text "sh scripts/start_backend.sh"
    end tell

    -- Start the frontend
    set newWindow2 to (create window with default profile)

    tell newWindow2
        set bounds to $FRONTEND_BOUNDS
    end tell

    tell current session of newWindow2
        write text "PATH=/opt/anaconda3/bin:/opt/anaconda3/condabin:$PATH"
        write text "conda activate chat-lse"
        write text "cd /Users/steve/chat-lse"
        write text "sh scripts/start_frontend.sh"
    end tell
    
end tell
EOF

# Wait for the backend process to fully start
sleep 12

# AppleScript to tail the log file
osascript <<EOF
tell application "iTerm"
    activate
    
    -- Tail the log
    set newWindow3 to (create window with default profile)

    tell newWindow3
        set bounds to $LOGTAIL_BOUNDS
    end tell

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

    tell front window
        set bounds to $SAFARI_BOUNDS
    end tell

    set URL of current tab of front window to "http://localhost:5173"
end tell
EOF