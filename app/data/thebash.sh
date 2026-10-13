

#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────────────
# agent.sh – PC2 (agent)
#
# Purpose:
#   Auto‑detects its FQDN, primary IP, and a sandbox directory, then dials out
#   to the controller (PC1). It accepts three commands (ls, cd, cat) from the
#   controller, executes them inside the sandbox without any shell
#   interpolation, and returns output terminated by <<<END>>>.
#
# Usage (one command):
#   Direct / LAN:
#     $ bash agent.sh <CONTROLLER_IP> [PORT] [SANDBOX]
#   Through a Cloudflare tunnel (requires cloudflared on PC2):
#     $ bash agent.sh https://<random>.trycloudflare.com [PORT] [SANDBOX]
#   - PORT defaults to 5050 (in tunnel mode it is the local forwarder port).
#   - SANDBOX defaults to /srv/labshare.
#   - Any address that looks like a URL or a *.trycloudflare.com host is
#     treated as a tunnel: the script starts `cloudflared access tcp` in the
#     background, connects through it, and stops it again on exit.
#
# Wire protocol matches controller.py – each reply ends with <<<END>>> on its
# own line. Paths are confined to the sandbox using realpath; attempts to escape
# are rejected. No command writes to disk, and the script refuses to run as root.
# ──────────────────────────────────────────────────────────────────────────────

set -u  # error on unset variables

# ---------- Configuration defaults ----------
DEFAULT_PORT=5050
DEFAULT_SANDBOX="/srv/labshare"
MAX_INPUT=4096               # bytes
MAX_CAT_SIZE=$((1024*1024))   # 1 MiB
CONNECT_TRIES=20             # seconds to wait for the controller / tunnel
# Optional hard‑coded controller address (edit if you want the script to use a fixed IP/FQDN)
# Leave empty to require a command‑line argument.
DEFAULT_CONTROLLER_IP="https://helping-attach-boundaries-women.trycloudflare.com"

# ---------- Argument handling ----------
# Use the first argument if supplied; otherwise fall back to the hard‑coded default.
CONTROLLER_IP="${1:-${DEFAULT_CONTROLLER_IP}}"
if [[ -z "$CONTROLLER_IP" ]]; then
    echo "[!] No controller IP/FQDN supplied and DEFAULT_CONTROLLER_IP is empty. Provide it as an argument or edit the script to set DEFAULT_CONTROLLER_IP." >&2
    exit 1
fi
PORT="${2:-$DEFAULT_PORT}"
SANDBOX="${3:-$DEFAULT_SANDBOX}"

# ---------- Privilege check ----------
if [[ "$(id -u)" -eq 0 ]]; then
    echo "[!] Refusing to run as root."
    exit 1
fi

# ---------- Auto‑detection ----------
# FQDN
if fqdn=$(hostname -f 2>/dev/null); then
    :
elif fqdn=$(hostname 2>/dev/null); then
    :
else
    fqdn="unknown"
fi

# Primary IP
if ip_addr=$(hostname -I 2>/dev/null | awk '{print $1}') && [[ -n "$ip_addr" ]]; then
    :
elif ip_addr=$(ip route get 1.1.1.1 2>/dev/null | awk '/src/ {for(i=1;i<=NF;i++) if($i=="src") print $(i+1)}') && [[ -n "$ip_addr" ]]; then
    :
else
    ip_addr="unknown"
fi

# Sandbox setup
if ! mkdir -p "$SANDBOX" 2>/dev/null; then
    echo "[!] Could not create sandbox directory '$SANDBOX'."
    exit 1
fi
if ! SANDBOX=$(realpath -m "$SANDBOX"); then
    echo "[!] Could not resolve sandbox path."
    exit 1
fi

# ---------- Tunnel (cloudflared) ----------
TUNNEL_PID=""
TUNNEL_LOG=""
cleanup() {
    if [[ -n "$TUNNEL_PID" ]]; then
        kill "$TUNNEL_PID" 2>/dev/null
        wait "$TUNNEL_PID" 2>/dev/null
    fi
    [[ -n "$TUNNEL_LOG" ]] && rm -f "$TUNNEL_LOG"
}
trap cleanup EXIT
trap 'exit 130' INT TERM

# Strip scheme and trailing slash/path so a pasted URL works as-is.
host="${CONTROLLER_IP#*://}"
host="${host%%/*}"
if [[ "$CONTROLLER_IP" == *://* || "$host" == *.trycloudflare.com ]]; then
    if ! command -v cloudflared >/dev/null 2>&1; then
        echo "[!] Tunnel address given but cloudflared is not installed on this machine." >&2
        echo "    Install it: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/" >&2
        exit 1
    fi
    TUNNEL_LOG=$(mktemp)
    echo "[*] Starting cloudflared forwarder 127.0.0.1:$PORT -> $host" >&2
    cloudflared access tcp --hostname "$host" --url "127.0.0.1:$PORT" >"$TUNNEL_LOG" 2>&1 &
    TUNNEL_PID=$!
    CONNECT_HOST="127.0.0.1"
else
    CONNECT_HOST="$CONTROLLER_IP"
fi

# ---------- Connection ----------
# Retry instead of probing: the controller accepts exactly one client, so a
# throw-away test connection would use up its only slot.
connected=0
for ((i = 0; i < CONNECT_TRIES; i++)); do
    if exec 3<>/dev/tcp/"$CONNECT_HOST"/"$PORT" 2>/dev/null; then
        connected=1
        break
    fi
    if [[ -n "$TUNNEL_PID" ]] && ! kill -0 "$TUNNEL_PID" 2>/dev/null; then
        echo "[!] cloudflared exited early:" >&2
        cat "$TUNNEL_LOG" >&2
        exit 1
    fi
    sleep 1
done
if (( ! connected )); then
    echo "[!] Unable to connect to $CONNECT_HOST:$PORT – is the controller running?" >&2
    [[ -n "$TUNNEL_LOG" ]] && cat "$TUNNEL_LOG" >&2
    exit 1
fi

# ---------- Greeting ----------
# controller.py waits for this greeting (terminated by <<<END>>>) before it
# sends any command, so it must go over the socket; echo it locally too.
greeting=$(printf "Agent starting.\n  fqdn    = %s\n  ip      = %s\n  sandbox = %s\n  allowed = ls, cd, cat" "$fqdn" "$ip_addr" "$SANDBOX")
printf "%s\n<<<END>>>\n" "$greeting" >&3
printf "[+] Connected to %s:%s\n%s\n" "$CONNECT_HOST" "$PORT" "$greeting" >&2

# ---------- Session state ----------
CWD="$SANDBOX"

# ---------- Helper functions ----------
# True if $1 is the sandbox itself or inside it (a plain prefix match would
# also accept siblings such as /srv/labshare2).
in_sandbox() {
    [[ "$1" == "$SANDBOX" || "$1" == "$SANDBOX"/* ]]
}

send_reply() {
    local cwd_display="${CWD#$SANDBOX}"
    if [[ -z "$cwd_display" ]]; then
        cwd_display="~"
    else
        cwd_display="~${cwd_display}"
    fi
    {
        printf "cwd=%s\n" "$cwd_display"
        printf "%s\n" "$1"
        printf "<<<END>>>\n"
    } >&3
}

error_reply() {
    send_reply "$1"
}

# ---------- Main loop ----------
while IFS= read -r line <&3; do
    # Strip possible CR (defensive)
    line=${line%$'\r'}

    # Skip empty lines
    [[ -z "$line" ]] && continue

    # Enforce length limit
    if (( ${#line} > MAX_INPUT )); then
        error_reply "Error: input line exceeds ${MAX_INPUT} bytes."
        continue
    fi

    # Tokenise without evaluation
    read -r -a parts <<< "$line"
    cmd="${parts[0]}"
    args=("${parts[@]:1}")

    case "$cmd" in
        exit|quit)
            printf "bye\n" >&3
            break
            ;;
        cd)
            if (( ${#args[@]} == 0 )); then
                target="$SANDBOX"
            else
                target="${args[0]}"
            fi
            resolved=$(realpath -m "$CWD/$target")
            if ! in_sandbox "$resolved"; then
                error_reply "Error: path '$target' is outside the sandbox."
                continue
            fi
            if [[ ! -d "$resolved" ]]; then
                error_reply "Error: '$target' is not a directory."
                continue
            fi
            CWD="$resolved"
            send_reply ""
            ;;
        ls)
            if (( ${#args[@]} == 0 )); then
                target_path="$CWD"
            else
                target_path=$(realpath -m "$CWD/${args[0]}")
            fi
            if ! in_sandbox "$target_path"; then
                error_reply "Error: path '${args[0]:-.}' is outside the sandbox."
                continue
            fi
            output=$(ls -la -- "$target_path" 2>&1)
            send_reply "$output"
            ;;
        cat)
            if (( ${#args[@]} != 1 )); then
                error_reply "Error: cat requires exactly one argument."
                continue
            fi
            target_path=$(realpath -m "$CWD/${args[0]}")
            if ! in_sandbox "$target_path"; then
                error_reply "Error: path '${args[0]}' is outside the sandbox."
                continue
            fi
            if [[ ! -f "$target_path" ]]; then
                error_reply "Error: file does not exist."
                continue
            fi
            size=$(stat -c%s "$target_path" 2>/dev/null || echo 0)
            if (( size > MAX_CAT_SIZE )); then
                error_reply "Error: file size exceeds 1 MiB limit."
                continue
            fi
            output=$(cat -- "$target_path" 2>&1)
            send_reply "$output"
            ;;
        *)
            error_reply "Denied: '$cmd' is not allowed (allowed: ls, cd, cat)."
            ;;
    esac
done

# ---------- Cleanup ----------
exec 3<&-
exec 3>&-
printf "[*] disconnected from controller. agent stopped.\n" >&2
