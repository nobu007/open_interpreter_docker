#!/bin/bash
# ログファイルのパス
LOG_FILE="/app/work/all.log"

# ログを出力する関数
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a "$LOG_FILE"
}

cd /app
if ! pgrep -f "/app/server.py" >/dev/null; then
  # 同期で起動（終了しない）
  bash --login -c "eval $(pyenv init -) && python /app/server.py"
  # TODO: エラー時に終了しないように無限ループ
else
  exit 0
fi

# helthcheck用に非同期で起動
# TODO: IS_BACKGROUNDオプション追加
# /app/server.pyが起動しているかチェック
if ! pgrep -f "/app/server.py" >/dev/null; then
    # sudo rm -f $LOG_FILE
    log "/app/server.py is not running. Starting it now..."
    # open_interpreterを起動
    if bash --login -c "eval $(pyenv init -) && python /app/server.py >> $LOG_FILE  2>&1" & then
        log "/app/server.py started successfully."
        exit 0
    else
        log "Failed to start /app/server.py."
        exit 1
    fi
else
    log "/app/server.py is already running."
    exit 0
fi
