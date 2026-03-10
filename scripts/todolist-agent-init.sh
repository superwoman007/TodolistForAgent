#!/bin/bash
#
# todolist-agent-init - Initialize TodolistForAgent runtime configuration
#
# Usage:
#   ./todolist-agent-init.sh --api-url <url> --api-key <key> --agent-id <id> [--cron]
#
# Options:
#   --api-url     TodoList API URL (e.g., https://todo.yourdomain.com)
#   --api-key     Server-issued API key for this agent
#   --agent-id    Agent ID assigned by the server
#   --cron        Create/update cron patrol job (every 30 minutes)
#   --help        Show this help message
#
# The script writes ~/.openclaw/todolist-agent.json and optionally sets up
# an OpenClaw cron job for periodic patrol checks. Safe to run multiple times.
#

set -e

CONFIG_DIR="$HOME/.openclaw"
CONFIG_FILE="$CONFIG_DIR/todolist-agent.json"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

show_help() {
    sed -n '3,25p' "$0"
    exit 0
}

log() {
    echo "[todolist-agent-init] $1"
}

parse_args() {
    API_URL=""
    API_KEY=""
    AGENT_ID=""
    ENABLE_CRON=false

    while [[ $# -gt 0 ]]; do
        case $1 in
            --api-url)
                API_URL="$2"
                shift 2
                ;;
            --api-key)
                API_KEY="$2"
                shift 2
                ;;
            --agent-id)
                AGENT_ID="$2"
                shift 2
                ;;
            --cron)
                ENABLE_CRON=true
                shift
                ;;
            --help)
                show_help
                ;;
            *)
                echo "Unknown option: $1"
                show_help
                ;;
        esac
    done
}

validate_args() {
    if [[ -z "$API_URL" ]]; then
        echo "Error: --api-url is required"
        exit 1
    fi
    if [[ -z "$API_KEY" ]]; then
        echo "Error: --api-key is required"
        exit 1
    fi
    if [[ -z "$AGENT_ID" ]]; then
        echo "Error: --agent-id is required"
        exit 1
    fi
}

create_config_dir() {
    if [[ ! -d "$CONFIG_DIR" ]]; then
        mkdir -p "$CONFIG_DIR"
        log "Created config directory: $CONFIG_DIR"
    fi
}

write_config() {
    local temp_file
    temp_file=$(mktemp)

    cat > "$temp_file" <<EOF
{
  "apiUrl": "$API_URL",
  "apiKey": "$API_KEY",
  "agentId": "$AGENT_ID"
}
EOF

    if [[ -f "$CONFIG_FILE" ]]; then
        if cmp -s "$temp_file" "$CONFIG_FILE"; then
            log "Config unchanged, skipping update"
            rm "$temp_file"
            return 0
        fi
    fi

    mv "$temp_file" "$CONFIG_FILE"
    chmod 600 "$CONFIG_FILE"
    log "Wrote config to $CONFIG_FILE"
}

setup_cron() {
    local job_name="todolist-agent-patrol"
    local message="Use the todolist-agent skill to patrol due tasks now. Run /agent/todos/check, inspect subtasks when present, execute actionable due tasks, mark subtasks done as you finish them, mark parent todos done on success, and mark fail with a useful result if execution fails. Reporting rule: if there are no due tasks, return a very short one-line summary only. If work was performed, return a concise but useful summary including how many tasks were due, which tasks were completed or failed, whether recurring tasks generated next items, and any follow-up risks that need human attention."

    if [[ "$ENABLE_CRON" != "true" ]]; then
        log "Cron job not requested (use --cron to enable)"
        return 0
    fi

    local existing_id
    existing_id=$(openclaw cron list --json 2>/dev/null | python3 - <<'PY'
import json,sys
try:
    data=json.load(sys.stdin)
    for job in data.get('jobs', []):
        if job.get('name') == 'todolist-agent-patrol':
            print(job.get('id',''))
            break
except Exception:
    pass
PY
)

    if [[ -n "$existing_id" ]]; then
        openclaw cron edit "$existing_id" \
          --description "Every 30 minutes: patrol due todos, execute them, and send concise summaries only when useful" \
          --every 30m \
          --session isolated \
          --message "$message" \
          --wake now \
          --expect-final \
          --best-effort-deliver >/dev/null
        log "Updated OpenClaw cron job: every 30 minutes"
    else
        openclaw cron add \
          --name "$job_name" \
          --description "Every 30 minutes: patrol due todos, execute them, and send concise summaries only when useful" \
          --every 30m \
          --session isolated \
          --message "$message" \
          --wake now \
          --expect-final \
          --best-effort-deliver >/dev/null
        log "Installed OpenClaw cron job: every 30 minutes"
    fi
}

main() {
    parse_args "$@"
    validate_args
    create_config_dir
    write_config

    if [[ "$ENABLE_CRON" == "true" ]]; then
        setup_cron
    fi

    log "Initialization complete"
    log "Config: $CONFIG_FILE"
    if [[ "$ENABLE_CRON" == "true" ]]; then
        log "Cron: enabled (every 30 minutes)"
    fi
}

main "$@"
