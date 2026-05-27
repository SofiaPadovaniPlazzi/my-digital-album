#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TARGET="$ROOT_DIR/ipad-app/MyDigitalAlbum/Resources/index.html"

python3 - "$ROOT_DIR" "$TARGET" <<'PY'
from pathlib import Path
import sys

root = Path(sys.argv[1])
target = Path(sys.argv[2])
sys.path.insert(0, str(root))

from my_digital_album import APP_HTML

target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(APP_HTML, encoding="utf-8")
PY

echo "Synced $TARGET"
