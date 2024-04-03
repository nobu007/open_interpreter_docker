#!/bin/bash
# ログファイルのパス
LOG_FILE="/app/work/all.log"

# ログを出力する関数
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a "$LOG_FILE"
}

# npm install
cd /app/TavernAI

# start-linux.shが起動しているかチェック
if ! pgrep -f "start-linux.sh" >/dev/null; then
    log "start-linux.sh is not running. Starting it now..."
    # open_interpreterを起動
    if bash -c "bash ./start-linux.sh >> $LOG_FILE  2>&1" & then
        log "start-linux.sh started successfully."
        exit 0
    else
        log "Failed to start start-linux.sh."
        exit 1
    fi
else
    log "start-linux.sh is already running."
    exit 0
fi
