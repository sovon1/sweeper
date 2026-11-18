#!/usr/bin/env bash
# 🧹 SWEEPER macOS & Linux Instant One-Liner
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/sovon1/sweeper/main/run.sh | bash

set -e

printf "\033[38;2;56;189;248m\033[1m"
cat << "EOF"
   ____                                   
  / ___|_      _____  ___ _ __   ___ _ __ 
  \___ \ \ /\ / / _ \/ _ \ '_ \ / _ \ '__|
   ___) \ V  V /  __/  __/ |_) |  __/ |   
  |____/ \_/\_/ \___|\___| .__/ \___|_|   
                         |_|   v1.0.0 ✨
EOF
printf "\033[0m\033[38;2;156;163;175m  The intelligent, zero-dependency folder organizer\033[0m\n\n"

INSTALL_DIR="${HOME}/.local/bin"
mkdir -p "$INSTALL_DIR"

if command -v python3 >/dev/null 2>&1; then
    printf "\033[38;2;52;211;153m⚡ Python 3 detected. Launching sweeper...\033[0m\n"
    SCRIPT_PATH="${INSTALL_DIR}/sweeper.py"
    curl -fsSL "https://raw.githubusercontent.com/sovon1/sweeper/main/sweeper.py" -o "$SCRIPT_PATH"
    chmod +x "$SCRIPT_PATH"
    python3 "$SCRIPT_PATH" "$@"
else
    printf "\033[38;2;56;189;248m⚡ Standalone binary mode. Fetching binary for $(uname -s)...\033[0m\n"
    OS=$(uname -s | tr '[:upper:]' '[:lower:]')
    ARCH=$(uname -m)
    
    if [ "$OS" = "darwin" ]; then
        BINARY="sweeper-darwin-universal"
    else
        BINARY="sweeper-linux-amd64"
    fi
    
    URL="https://github.com/sovon1/sweeper/releases/latest/download/${BINARY}"
    TARGET="${INSTALL_DIR}/sweeper"
    curl -fsSL "$URL" -o "$TARGET"
    chmod +x "$TARGET"
    "$TARGET" "$@"
fi
