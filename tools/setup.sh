#!/usr/bin/env bash
# Recreates the working layout that build-web.py and the tests expect (they use absolute paths).
# Run from anywhere:  bash <repo>/tools/setup.sh
set -e
R=$(cd "$(dirname "$0")/.." && pwd)
mkdir -p /home/claude/protocol-drill /home/claude/web/site /home/claude/tests /home/claude/packet

# The app source (the same file as the Claude artifact). Edit THIS copy, then publish and build from it.
cp "$R/src/index.html" /home/claude/protocol-drill/index.html

# Website build: script + Firebase bundle entry, and the site's other files (config, Firebase bundle, icons).
cp "$R/tools/build-web.py" "$R/tools/fb-entry.js" /home/claude/web/
cp "$R/config.js" "$R/firebase.js" "$R/manifest.webmanifest" "$R/.nojekyll" "$R"/*.png /home/claude/web/site/

# Tests and their fixture.
cp -r "$R"/tools/tests/. /home/claude/tests/
cp "$R/tools/tests/fixtures/cards.json" /home/claude/packet/cards.json

# Browser tests need Playwright; Chrome is at /usr/bin/google-chrome.
python3 -c "import playwright" 2>/dev/null || pip install playwright --break-system-packages -q
echo "Setup done. Source: /home/claude/protocol-drill/index.html  Tests: /home/claude/tests  (bash $R/tools/run-tests.sh)"
