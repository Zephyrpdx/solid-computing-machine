#!/usr/bin/env bash

# cleanup-port.sh
# Stops the process listening on a given port (default: 8000).

set -euo pipefail

PORT=${1:-8000}

if command -v lsof >/dev/null 2>&1; then
  PIDS=$(lsof -t -iTCP:"${PORT}" -sTCP:LISTEN -Pn || true)
else
  PIDS=$(ss -ltnp 2>/dev/null | awk -v port=":${PORT}" '$4 ~ port { gsub(/.*pid=|,/, "", $6); print $6 }' | sort -u)
fi

if [[ -z "$PIDS" ]]; then
  echo "No process found listening on port ${PORT}."
  exit 0
fi

echo "Stopping process(es) on port ${PORT}: $PIDS"
kill $PIDS

echo "Port ${PORT} is now free."
