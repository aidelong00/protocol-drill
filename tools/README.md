# Updating the site

The app itself is the Protocol Drill artifact's `index.html` (Claude version). This site is built from it:

1. Put the artifact's current `index.html` at `/home/claude/protocol-drill/index.html`.
2. `python3 tools/build-web.py` swaps the Claude saving for Google sign-in (Firebase) and writes `index.html`
   (edit the OUT path in the script to this repo's root).
3. `firebase.js` is a bundle of the Firebase SDK: `npm install firebase esbuild`, then
   `npx esbuild tools/fb-entry.js --bundle --minify --format=iife --target=es2019 --outfile=firebase.js`.
4. `tools/web1.py` tests sign-in, autosave and account switching against a stand-in for Firebase (`tools/fakefb.js`).

Each person's progress is the Firestore document `users/<uid>`; the Firestore rules only let that user read or write it.
