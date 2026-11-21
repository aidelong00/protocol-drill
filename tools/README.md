# Working on Protocol Drill

Start with **HANDOFF.md** at the repo root: it is the full guide (where everything lives, the rules agreed with
the user, how to change, test and publish).

Quick start in a new session:

```bash
git clone --depth 1 https://github.com/aidelong00/protocol-drill /home/claude/gh-site   # not /home/claude/protocol-drill
bash /home/claude/gh-site/tools/setup.sh      # recreates /home/claude/{protocol-drill,web,tests,packet}
bash /home/claude/gh-site/tools/run-tests.sh  # all tests (or: run-tests.sh node)
```

- `src/index.html` — the app source, identical to the Claude artifact. Edit the working copy at
  `/home/claude/protocol-drill/index.html`, then publish it to the artifact and copy it back here.
- `build-web.py` — builds the website (`/home/claude/web/site/index.html`) from the source: swaps Claude saving
  for Google sign-in (Firebase) and adds the account row, icons and manifest. Copy the result to the repo root.
- `fb-entry.js` — what's bundled into `firebase.js`
  (`npm i firebase esbuild && npx esbuild fb-entry.js --bundle --minify --format=iife --target=es2019 --outfile=site/firebase.js`).
- `tests/` — grading suites (`*.test.js`, node), app flows (`flow*.py`, Playwright + /usr/bin/google-chrome),
  website tests (`web1.py` one device, `web3.py` two devices, against a stand-in for Firebase in `fakefb.js`),
  `art2dev.py` (Claude version, two devices), `migrate.py` (old saved runs).
