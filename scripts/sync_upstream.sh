#!/usr/bin/env bash
# Re-vendor gameblocks/ from xt4d/GameBlocks. Usage: scripts/sync_upstream.sh [ref]
# (ref = branch, tag, or SHA; default main). Then run pytest — the coherence tests
# catch a summary.md <-> modules/ drift — and commit vendor/ + UPSTREAM together.
set -euo pipefail
cd "$(dirname "$0")/.."

REF="${1:-main}"
URL="https://github.com/xt4d/GameBlocks"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

git clone --quiet "$URL" "$TMP"
git -C "$TMP" checkout --quiet "$REF"
SHA="$(git -C "$TMP" rev-parse HEAD)"

rsync -a --delete "$TMP/gameblocks/" vendor/gameblocks/
cp "$TMP/LICENSE" vendor/LICENSE

cat > vendor/UPSTREAM <<EOF
source: $URL
ref: $REF
sha: $SHA
synced: $(date +%Y-%m-%d)
license: MIT (see vendor/LICENSE)
# Re-vendor with scripts/sync_upstream.sh — never hand-edit vendor/gameblocks/.
EOF

echo "vendored $URL @ $SHA ($(find vendor/gameblocks/modules -name '*.js' | wc -l | tr -d ' ') modules)"
