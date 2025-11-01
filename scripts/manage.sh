
#!/usr/bin/env bash
set -e
CMD="${1:-help}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
case "$CMD" in
  setup)
    python3 -m venv "$ROOT/tsk"
    source "$ROOT/tsk/bin/activate"
    pip install --upgrade pip
    pip install -r "$ROOT/requirements.txt"
    echo "OK: env prêt."
    ;;
  run)
    source "$ROOT/tsk/bin/activate"
    python3 "$ROOT/app/app.py"
    ;;
  update)
    bash "$ROOT/scripts/update.sh"
    ;;
  *)
    echo "Usage: scripts/manage.sh {setup|run|update}"
    ;;
esac
