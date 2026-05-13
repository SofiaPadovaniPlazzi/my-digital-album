#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
APP_NAME="My Digital Album"
APP_DIR="$ROOT_DIR/mac-app/$APP_NAME.app"
CONTENTS_DIR="$APP_DIR/Contents"
MACOS_DIR="$CONTENTS_DIR/MacOS"
RESOURCES_DIR="$CONTENTS_DIR/Resources"
ICON_SOURCE="$ROOT_DIR/mac-app/resources/app-icon-transparent.png"
ICONSET_DIR="$ROOT_DIR/mac-app/AppIcon.iconset"

rm -rf "$APP_DIR"
mkdir -p "$MACOS_DIR" "$RESOURCES_DIR"

python3 - "$ROOT_DIR" "$RESOURCES_DIR/index.html" <<'PY'
from pathlib import Path
import sys

root = Path(sys.argv[1])
target = Path(sys.argv[2])
sys.path.insert(0, str(root))

from my_digital_album import APP_HTML

target.write_text(APP_HTML, encoding="utf-8")
PY

cp "$ROOT_DIR/mac-app/resources/Info.plist" "$CONTENTS_DIR/Info.plist"

if [[ -f "$ICON_SOURCE" ]]; then
  rm -rf "$ICONSET_DIR"
  mkdir -p "$ICONSET_DIR"
  sips -z 16 16 "$ICON_SOURCE" --out "$ICONSET_DIR/icon_16x16.png" >/dev/null
  sips -z 32 32 "$ICON_SOURCE" --out "$ICONSET_DIR/icon_16x16@2x.png" >/dev/null
  sips -z 32 32 "$ICON_SOURCE" --out "$ICONSET_DIR/icon_32x32.png" >/dev/null
  sips -z 64 64 "$ICON_SOURCE" --out "$ICONSET_DIR/icon_32x32@2x.png" >/dev/null
  sips -z 128 128 "$ICON_SOURCE" --out "$ICONSET_DIR/icon_128x128.png" >/dev/null
  sips -z 256 256 "$ICON_SOURCE" --out "$ICONSET_DIR/icon_128x128@2x.png" >/dev/null
  sips -z 256 256 "$ICON_SOURCE" --out "$ICONSET_DIR/icon_256x256.png" >/dev/null
  sips -z 512 512 "$ICON_SOURCE" --out "$ICONSET_DIR/icon_256x256@2x.png" >/dev/null
  sips -z 512 512 "$ICON_SOURCE" --out "$ICONSET_DIR/icon_512x512.png" >/dev/null
  sips -z 1024 1024 "$ICON_SOURCE" --out "$ICONSET_DIR/icon_512x512@2x.png" >/dev/null
  python3 - "$ICONSET_DIR" "$RESOURCES_DIR/AppIcon.icns" <<'PY'
from pathlib import Path
import struct
import sys

iconset = Path(sys.argv[1])
target = Path(sys.argv[2])
chunks = [
    ("icp4", "icon_16x16.png"),
    ("icp5", "icon_32x32.png"),
    ("icp6", "icon_32x32@2x.png"),
    ("ic07", "icon_128x128.png"),
    ("ic08", "icon_256x256.png"),
    ("ic09", "icon_512x512.png"),
    ("ic10", "icon_512x512@2x.png"),
]
body = bytearray()
for chunk_type, filename in chunks:
    data = (iconset / filename).read_bytes()
    body.extend(chunk_type.encode("ascii"))
    body.extend(struct.pack(">I", len(data) + 8))
    body.extend(data)
target.write_bytes(b"icns" + struct.pack(">I", len(body) + 8) + body)
PY
  rm -rf "$ICONSET_DIR"
fi

clang \
  -fobjc-arc \
  "$ROOT_DIR/mac-app/src/main.m" \
  -o "$MACOS_DIR/MyDigitalAlbum" \
  -framework Cocoa \
  -framework WebKit \
  -framework UniformTypeIdentifiers

chmod +x "$MACOS_DIR/MyDigitalAlbum"

echo "Built $APP_DIR"
echo "Local album data will be saved in ~/Library/Application Support/My Digital Album/library.json"
