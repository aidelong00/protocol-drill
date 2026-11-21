#!/usr/bin/env bash
# Runs every test against /home/claude/protocol-drill/index.html (and the built site for web*.py).
# Usage: bash tools/run-tests.sh        (all)    |   bash tools/run-tests.sh node   (grading only, ~3 min)
cd /home/claude/tests || exit 1
FILTER='agent-proxy|^- |Allowed|For details'
echo "== Grading suites (node)"
for f in v8 dup andor2 cls v7 v6 v5 v4 abbr v3 grade2 andor fix mnorder skip numw andopt smalltypo; do
  printf "%-10s " "$f"; timeout 600 node $f.test.js 2>&1 | tail -1
done
[ "$1" = "node" ] && exit 0
echo "== App flows (Playwright, Chrome)"
for f in flow5 flow7 flow8 flow9 flow10 flow11 flow12 flow13 flow16 flow17 flow18 flow19 flow20 flow21 flow22 flow23 flow25 flow26 flow27 flow28 flow29 flow30 art2dev migrate; do
  n=$(timeout 300 python3 $f.py 2>&1 | grep -Ev "$FILTER" | grep -c "FAIL\|Traceback")
  printf "%-10s %s\n" "$f" "$([ "$n" = 0 ] && echo ok || echo "$n FAIL (rerun once: some flows pick random cards)")"
done
echo "== Website (build first: python3 /home/claude/web/build-web.py)"
for f in web1 web3; do
  printf "%-10s " "$f"; timeout 300 python3 $f.py 2>&1 | grep -Ev "$FILTER" | grep -c "^PASS" | sed 's/$/ checks passed/'
done
