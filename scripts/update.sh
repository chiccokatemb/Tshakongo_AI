
#!/usr/bin/env bash
set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
REPO_URL=$(python3 - <<'PY'
import yaml,os
cfg=yaml.safe_load(open(os.path.join("app","config.yaml")))
print(cfg.get("project",{}).get("repo_url",""))
PY
)
if [ ! -d ".git" ]; then
  git init
  if [ -n "$REPO_URL" ]; then git remote add origin "$REPO_URL" || true; fi
fi
git fetch origin || true
git pull origin principal || true
git pull origin main || true
echo "Mise à jour OK."
