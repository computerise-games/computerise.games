#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE="$(realpath "${1:-"$ROOT/video/new-worlds-trailer.mp4"}")"

if [[ ! -f "$SOURCE" ]]; then
  echo "Trailer source not found: $SOURCE" >&2
  exit 1
fi
if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "ffmpeg is required to encode trailer variants." >&2
  exit 1
fi

encode() {
  local output="$1"
  local filter="$2"
  local bitrate="$3"
  local maxrate="$4"
  local bufsize="$5"
  ffmpeg -hide_banner -y -i "$SOURCE" \
    -map 0:v:0 -map 0:a:0 \
    -vf "$filter" -c:v libx264 -preset medium -pix_fmt yuv420p \
    -b:v "$bitrate" -maxrate "$maxrate" -bufsize "$bufsize" \
    -c:a copy -movflags +faststart "$ROOT/video/$output"
}

encode new-worlds-trailer-1080p30.mp4 "fps=30" 1500k 1800k 3000k
encode new-worlds-trailer-720p30.mp4 "fps=30,scale=-2:720:flags=lanczos" 700k 850k 1400k
