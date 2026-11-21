# Protocol Drill — handoff script for the next session

Follow this to keep building Protocol Drill exactly where the last session left off (handoff: 2026-11-21).
Sections 0–3 are the procedure; 4–5 are the reference you'll need while changing things; 6–8 are tests, open threads, history.

---

## 0. Who this is for and how to work with them

- **The user:** a paramedic student studying San Diego County EMS (LEMSIS) protocols. Protocol Drill is their
  typing drill for memorizing the **County of San Diego EMS P-115 Medication List (7/1/2026)** word for word.
  They use it mostly on their phone (Claude mobile app / phone browser), sometimes on a PC.
- **Standing preferences (always apply):**
  - Double-check yourself before giving any dosing, protocol or medication-indication answer.
  - Protocol study material must be the **full verbatim P-115 text**: never condense, shorten or reword the card data.
- **How they work:**
  - Requests arrive in small batches, often several in a row while you're still working. Handle them all.
  - They hate guessing. When a request changes behavior and could reasonably go two ways, ask **one** short
    question first (AskUserQuestion, 2–3 options, previews for layouts). Past examples where asking was right:
    the progress-bar rules, "warn vs. stop" for skipped words, one box per drug vs. names pre-typed in the box.
  - **Going live:** if they say "do not go live yet", make and test the change, report, and wait for "push it" /
    "go live". Otherwise, fixes and requested changes were published right away. When in doubt, ask.
  - Every change goes to **both** versions (Claude artifact and website).
  - Report briefly in plain language (they read on a phone): what changed, in their terms; anything that still
    behaves differently than they might expect; at most one offer. No internals or jargon.
  - Screenshots from them are photos of a screen: read the "You wrote" line and the card name, reproduce the exact
    input in a test, then fix.

## 1. Where everything lives

| Thing | Where |
|---|---|
| Claude version (artifact) | slug `b4eff82c-d9f9-4038-a0e1-5061c9accc87`, https://claude.ai/artifact/PLtae1h23avPqFDEyhwaHL, title "Protocol Drill", shared **public** (publishing needs `shared_live:'public'` and `artifact_title:'Protocol Drill'`). Live version at handoff: `1795125432-151f`. |
| Artifact capabilities | `db` rules `[{path:"",read:"admin",write:"admin"},{path:"data/users/{self}",read:"interact",write:"interact"}]`, plus `user`. Each person's progress is the doc `data/users/<id>/state`. **Platform rule:** link viewers are "Viewers" and can never write the db, whatever the rules say (the tool also refuses to loosen rules on a public artifact). That's why the website exists. |
| Website | https://aidelong00.github.io/protocol-drill/ (GitHub Pages, branch `main`, root). Repo **aidelong00/protocol-drill** (public). The Claude GitHub App is installed on the account, so `add_repo` with `access:"push"` works. |
| Repo layout | `index.html` (built site), `config.js` (Firebase web config, public by design), `firebase.js` (bundled Firebase SDK: app, auth, firestore/lite), `manifest.webmanifest`, icons, `.nojekyll`, **`src/index.html` (the app source, same file as the artifact)**, `tools/` (build-web.py, fb-entry.js, setup.sh, run-tests.sh, tests/), this file. |
| Firebase | Project `protocol-drill-7743c` on the user's Google account. Google sign-in on. Authorized domain `aidelong00.github.io`. Firestore rules: `match /users/{uid} { allow read, write: if request.auth != null && request.auth.uid == uid; }`. Website progress = Firestore doc `users/<uid>`; signed out = this device only. You can't reach Firebase from the sandbox: the user changes the console. |

The Claude version and the website are separate apps with separate progress (Claude account vs. Google account).

## 2. Start-of-session setup

1. `add_repo` owner `aidelong00`, repo `protocol-drill`, access `push`. Clone to **`/home/claude/gh-site`**
   (not `/home/claude/protocol-drill`: that path is the working copy of the source):
   `git clone --depth 1 https://github.com/aidelong00/protocol-drill /home/claude/gh-site`
2. `bash /home/claude/gh-site/tools/setup.sh`. This recreates `/home/claude/protocol-drill/index.html` (source),
   `/home/claude/web/` (build script and site files), `/home/claude/tests/` and `/home/claude/packet/cards.json`
   (test fixture). The tests and build script use these absolute paths.
3. Check that the source is current: `get_artifact` on the slug. If the live version isn't `1795125432-151f`, or
   isn't the one noted in the latest commit message, `read_artifact` it and save that HTML as the source
   (`/home/claude/protocol-drill/index.html` and `src/index.html`).
4. Baseline: `bash /home/claude/gh-site/tools/run-tests.sh` (`node` argument = grading suites only, a few minutes;
   the flows take about 10 more).
5. Rebuild `firebase.js` only if `fb-entry.js` changes:
   `cd /home/claude/web && npm init -y && npm i firebase esbuild && npx esbuild fb-entry.js --bundle --minify --format=iife --target=es2019 --outfile=site/firebase.js`

## 3. Change → test → publish loop

1. Back up first: `cp /home/claude/protocol-drill/index.html /home/claude/protocol-drill/index.vNN.html`.
2. Edit the source with small Python patch scripts that **assert each search string matches exactly once**
   before replacing. Gotchas: use literal characters for curly quotes and `•`; in Python string literals `\u{...}`
   is a syntax error, so put emoji in literally; JS regex backslashes need doubling inside normal Python strings.
3. Add a test for the new rule or flow. Grading rules get a node test (copy the header of any `*.test.js`: it
   evals the CORE and DATA blocks). UI behavior gets a `flowNN.py` (copy `flow30.py`: settings are seeded via
   localStorage, cards are found by name).
4. Run the tests. Re-run any flow that fails once before debugging: flows 20/25/28/29 pick random cards.
5. "Don't go live yet": stop here and report.
6. **Publish the Claude version:** `get_artifact` (for the live version), then `publish_files` with
   `{slug, base_version:<live version>, shared_live:'public', artifact_title:'Protocol Drill',
   files:[{as:'index.html', path:'/home/claude/protocol-drill/index.html'}], label:'<short change note>'}`.
7. **Publish the website:**
   ```bash
   python3 /home/claude/web/build-web.py            # fails loudly if a source string it patches has changed
   cd /home/claude/gh-site
   cp /home/claude/web/site/index.html index.html
   cp /home/claude/protocol-drill/index.html src/index.html
   cp /home/claude/web/build-web.py tools/          # if you changed it
   git add -A && git -c user.name=aidelong00 -c user.email=aidelong00@users.noreply.github.com commit -m "<what changed>

   <attribution lines from this session's system reminder>"
   git -c push.negotiate=true push
   ```
   Then wait about 50 s and run `gh api repos/aidelong00/protocol-drill/actions/runs --jq '.workflow_runs[:1][]|{status,conclusion,sha:.head_sha[0:7]}'`
   to confirm the deploy. Run `web1.py`/`web3.py` after building. A long chained command once came back as
   "did not run", so check `git log -1` before assuming it pushed.
8. Tell the user it's live and to refresh.

**What `build-web.py` does to the source:** adds manifest/icon/theme tags, loads `config.js` + `firebase.js`;
adds CSS for the account row; keeps `store.uid`; replaces the whole block from `/* Account sync:` through
`function updateSync(){…}` with the Firebase version (sign-in popup with redirect fallback, `users/<uid>` doc,
merge/pull logic, sign-out clears the device, account-switch safety); puts `${acctHTML()}` above `${dayRow()}`
on the home screen; adds `signin`/`signout` actions; replaces the Claude hot-reload line with `start({})`. If you
rename anything it searches for, update the script.

## 4. App architecture (one file, about 2,500 lines)

- **Layout:** CSS → HTML shell → one script. Inside the script, `/*CORE-START*/ … /*CORE-END*/` is the grading
  engine (pure functions; node tests eval this block), and `/*DATA-START*/ … /*DATA-END*/` is the P-115 data and
  the decks. After those come the store and sync, then the UI.
- **Data:** `MOA [drug, text]`, `CLASS`, `IND [drug, text, protocols]`, `CONTRA [drug, text, none?]`, `PEDS`,
  `DOSE`, `ADV [drug, text, mnemonic]`, `NOTES`; `CLASS_ALT`, `MOA_ALT` (allowed phrase swaps).
  `BUILTIN` decks and item flags:
  - `moa`: `nw, eff, andok, alt`
  - `class`: `any, phr, alt`
  - `ind`: `nw, p` (protocols)
  - `contra`: `nw, none`
  - `dose`
  - `peds`: `na`
  - `adv`: `mn, any, lenient`
  - `notes`: `nw, any`

  Drug cards: `cardDeck(name)`, id `'card:'+name`, sections in `CARD_ORDER` (class, moa, ind, contra, dose, peds,
  adv, notes). The Albuterol / Levalbuterol card has a separate MOA item for each drug. Custom decks use
  `question :: answer` with `[key words]` (see `EXAMPLE`).
- **Grading core:**
  - `norm` lowercases, then runs `spellNumbers` (number words and ordinals to digits), then hyphen/range rules, then `SYN`.
  - `ABBR` with `canonRef`/`canonUser`, plus `LONGS`/`badExpansions` (a spelled-out term must be right if it's given).
  - `tokEq`: OSA fuzzy matching with length tolerance and a 3-letter plural rule, `EQUIV`, the `OPPOSITE` guard.
  - `LEEWAY.keys`/`LEEWAY.exact` and `CRIT`.
  - `refOf` (cached).
  - `userToks`: `smallTypo`, doubled-word `dedupe`, `EFF` effects→activity, `SAME_WORDS`, leeway filter.
  - `gradePlain`: LCS plus displaced words (`ORDER_SLACK=2`, `ORDER_MAX=2`), critical extras, slash-"and",
    "or"-for-"and", mistake clusters.
  - `anyMatch` (any-order lists and phrase groups), `gradeKeys`, `gradeProt`, `gradeItem`.
  - `fixTargets` (mistakes become clause ranges, which are merged).
  - `liveCheck` (warn/stop, plus marks for the stop screen).
  - `nextWord` / `nearLast` (alignment that prefers nearby matches, `NEAR_GAP=0.3`).
  - `partialInfo` (grade only the typed part).
- **State:** `store` in localStorage `pdrill:v1`:
  - `settings {mode:'keys'|'exact', auto, live, prot, warnMiss, mnemView, v:3}`
  - `progress {deckId: {streak, learned, mastered, strikes, lastPct, lastMisses, lastAt…}}`
  - `custom`, `mnem`, `mnemLast`
  - `streak {days[], today{d,k[]}}`
  - `runs {deckId: run | {gone:t}}`
  - `stamp {part: time}`, `updatedAt` (plus `uid` on the web)

  Sync works through `mergeStores` (part by part, newest wins; streak days are unioned; runs compared by `t`),
  `adoptStore` (a drill on screen jumps to the newer run), read-before-write, and a pull on focus, on visibility
  and every 30 s.
- **Run object:** `ids, queue, cleared, missed, missCount, phase ('answer'|'retype'|'correct'), fix {targets,i}, pres
  (per-showing flags: missed, hinted, assisted, redo, fail, nw), last, draft, t`. `normFix` merges every fix target
  into **one** step (`part` with `texts`/`n`, or `full`, plus `prot:true`; or `memory` after a stop or cut-off).
- **Screens:** home, cards, drill, results, study, edit, about.

## 5. Behavior rules agreed with the user (don't regress these)

### Grading
- Typos are forgiven. Words that change treatment must match: **and/or, numbers, units, routes, not/no,
  comparison signs** (type `>=`/`<=` for ≥/≤).
- "Word for word" switch off (`keys`) makes the small words optional (the `LEEWAY.keys` list). On (`exact`), only
  a/an/the/but are optional.
- **Typos of small words** count as those words ("te"/"teh"/"hte" = the, "fo" = of, "ot" = to), unless the typed
  thing is a real word anywhere in the cards ("iv", "im") or a word start ("non", "anti", "pre"…).
- **Doubled words** are ignored ("and and", "heart heart rate") unless the card itself repeats the word. Doubled
  numbers, "not" and "no" still count.
- **Same meaning:**
  - within = in, onto = to
  - effects = activity (on cards that use "activity")
  - NSAID = nonsteroidal anti-inflammatory drug (either one or both; any hyphenation)
  - ASA = aspirin, "sodium bicarb" = sodium bicarbonate, "not given" = withheld
  - 5-HT3 is one token
  - hr = heart rate = hour where it fits
  - **numbers written out** = digits ("beta two" = beta-2, "three times" = 3 times, "twenty-four" = 24)
  - **ordinals** ("second-degree" = 2nd = 2), but "6-second" stays a length of time
- Abbreviation or spelled-out term are both fine. If both are given, the spelled-out part must be right
  ("supraventricular bradycardia (SVT)" fails).
- Opposites are never typos: hyper/hypo, brady/tachy, incr/decr, inter/intra, and so on.
- **Order:** up to 2 words out of place, each within 2 positions, passes with an order note. More than that fails.
- **"and/or" is word for word:** "and" or "or" alone fails, "or/and" fails, a doubled "and and/or" passes.
  "and or" without the slash passes (punctuation is never graded).
- An extra "and"/"or" joining a list is fine, except "IV and IO" for "IV/IO".
- **Mechanisms only:** a joining "and" can be left out ("glucose, inhibits…"). Writing "or" in its place fails.
  "and/or" stays word for word. Show next word still shows the "and".
- Aspirin mechanism: "antipyretic and analgesic" may be swapped.
- **Class cards:** comma phrases in any order. Flipping words inside a phrase passes with an order note (not a
  fail). Phrases must stay under their drug label. Bup-Nal: "partial opioid agonist" = "opioid partial agonist".
- Adverse effects: any order, lenient. Mnemonic views (book / A–Z / custom). Show answer lists them in the view
  last used for that drug.
- Notes: bullets in any order. Contraindications "None" and peds "NA" accept variants (`NONE_OK`/`NA_OK`).
- Indications: protocol numbers when "Ask for protocol numbers" is on. Numbers only is fine; extra numbers are flagged.
- "Count my answer as correct (the grader missed a synonym)": when used on the run's only miss, it undoes the run's fail.

### Screens and flow
- **Home:** header (tag, About button, title), then on the website the account row (just the email + Sign out, or
  "Sign in with Google"), then a centered row with the date (e.g. "November 21, 2026") and "🔥 N day streak",
  then one settings card of switches: Word for word / Mistake warning / Warning counts as a miss / Ask for
  protocol numbers / Skip ahead after a correct answer. Then deck lists and Drug cards. Explanations live on the
  About page. No color stripes or drug-class labels (they gave answers away).
- **Deck progress bar:** shows "x% learned" (share of first-try answers in the last full run; starts at 0%).
- **Learned:** a perfect full run (no misses, no go-backs) makes the deck Learned, and the mastery bar starts at
  10%. Each further perfect run adds 10%.
- **Mastered:** 10 perfect runs in a row.
- **Failed runs:** a run fails at its first miss. A failed run puts the mastery bar back to 0%. Two failed runs in a
  row: Mastered drops to Learned, and Learned drops to 0. A perfect run clears the strike. Drill-missed (subset)
  runs don't count. The results screen warns about a failed run.
- **Decay:** 169 h without finishing a full run resets the deck to 0. A red h:mm:ss countdown shows top-right of
  the deck row for the last 24 h.
- **Streak:** a day counts after **3 different things answered with no mistakes** (cards in any deck, or drug-card
  sections). Repeats count once. Missed-then-retyped doesn't count; "I was right" does. Days follow the phone's
  calendar. The streak shows the count through yesterday until today counts. The fire stays grey until today counts
  (Claude's addition, offered to change). Streak days merge across devices.
- **Drill header and buttons:**
  - Back button: an outlined pill ("‹ All decks" / "‹ Drug cards").
  - Drug-card header: the section is the big title, with the drug small and grey above. In regular decks, the deck
    name is small and the drug big.
  - Buttons: **Check**, **Show answer** beside it, **Show next word** full width under them (greys out after use;
    using it counts as a miss).
  - Switches under the box: Mistake warning and Warning counts as a miss.
- **Typing is saved with the run** and comes back when you return, on any device. A revealed next word still fits it.
- **Show next word:** uses the alignment that stays near your position. Words you typed out of order count as
  done. A wrong word at the end counts as your try at that spot. A half-typed word (no space yet) keeps showing that word.
- **Mistake warning:**
  - "Something's off…" shows 2 words after a slip. A stop comes 5 words after.
  - **Skipped words** warn as soon as the 2 words after the gap match, and stop 2 words later.
  - A stop cuts the box back to the start of that sentence. The stop screen shows the full answer with the problem
    in **bold** ("+word" where a stray word went) and "You wrote: …" with your wrong word in bold.
  - A warning counts as a miss unless that switch is off. A stop is always a miss.
- **After a miss:**
  - "N mistakes: fix just this part / fix these parts / retype the whole answer" (3 or more mistakes means retype
    the whole answer).
  - When you retype a part, the full answer on top shows mistakes in **bold** and only the dashed retype box is
    highlighted.
  - **Everything is one step with one Check:** two parts go in one box with "…" between them, and the protocols box
    sits on the same screen. A failed Check adds a "Still not right: …" line. Overlapping parts are merged, so
    nothing appears twice.
  - Drug cards ask for the section once more from memory afterwards.
- **Show answer:** with nothing typed, it shows the answer and you retype the whole thing. Typed and right: counts
  as correct. Typed to the end with mistakes: the normal fix. Typed partway: a **cut-off**.
- **Cut-off** happens on Show answer partway, Check after a stop, or Check while the warning is showing. Only what
  you typed is graded; the part you haven't reached isn't a mistake. Your text stays in the box. The screen says
  "Fix the bold part, then keep going from where you left off", and it counts as one miss. Pressing Check on an
  unfinished answer with no warning or stop still grades the whole answer (offered to change).
- **Two-drug cards:** the Bup-Nal class card shows one box per drug with fixed "Buprenorphine:" / "Naloxone:"
  labels. Enter moves to the next box, and in the last box it checks. The boxes are written into the hidden main
  box as "• Name: …" lines. The Albuterol / Levalbuterol mechanism sections show "Albuterol:" or "Levalbuterol:"
  above the box.

### Saving and sync
- The run in progress, deck progress, streak and settings follow the account across devices, merging part by part
  so two devices never overwrite each other. A device catches up when you come back to it, and a drill that's open
  jumps to the newer spot. Restarting or finishing a deck on one device doesn't bring the old run back on another.
- Website: signing out clears the device. A device's copy is never pushed into a different account.
- Updates never touch anyone's saved progress. Only a half-finished run whose deck wording changed starts over.

## 6. Tests (`tools/tests`, run with `tools/run-tests.sh`)

- **Grading (node):**
  - `v3`–`v8`, `grade2`: core grading and live check.
  - `abbr`: abbreviations. `andor`, `andor2`: and/or rules. `cls`: class phrases. `fix`: fix parts.
  - `mnorder`: mnemonic order. `dup`: doubled words on every card. `skip`: skipped-word warnings vs. flips.
  - `numw`: number words. `andopt`: optional "and" in mechanisms. `smalltypo`: small-word typos.
  - `grade.test.js` was retired: it predates the verbatim cards.
- **Next-word accuracy:** `nwacc.js` compares the source with a saved baseline. Before a change that touches next
  word, run `cp /home/claude/protocol-drill/index.html /home/claude/protocol-drill/index.base.html`, then run it
  after the change.
- **Flows (Playwright):**
  - 5/7/8: core drill, search, results. 9/17/18: progress bar and mastery. 10/11: assisted cards, stops, warnings.
  - 12: class and redo. 13: mnemonic views. 16: next word "ions".
  - 19: drafts. 20/21: retype fixes and protocols. 22: skip warn/stop. 23: streak and back button.
  - 25/26: one-step fix. 27: drug boxes. 28: warning switch. 29: Show answer. 30: cut-off (replays the user's
    Magnesium Sulfate typing).
- **Sync:** `web1` (one device), `web3` (two devices), `art2dev` (Claude version, two devices), `migrate`
  (old run keys). `web2` takes screenshots.
- `livecal.js` replays the Calcium Chloride skipped-words case.

## 7. Open threads (offered to the user, not decided)

1. Check on an unfinished answer with no warning or stop grades the whole answer. Offered: treat it as a cut-off too.
2. The streak fire is grey until today counts. Offered: always lit.
3. "and or" without the slash passes. Offered: require the slash.
4. The stop screen shows the whole answer. Offered: show only the sentence with the mistake.
5. Next-word trade-off: an extra word typed at the very end now skips one word ahead (94% vs. 98% before).
6. 3 of 211 skipped-word cases (in the last couple of words of an answer) aren't caught live; Check catches them.
7. The website saves on every typing pause (a read and a write each time). That's fine on Firebase's free tier for
   a few users. If many classmates use it, lengthen the save delay.
8. Old `ABBR` entries for "1st"/"first" are dead code now (ordinals become digits first). Harmless.

## 8. History (what was built, in order)

Verbatim P-115 cards and decks, then: typo-tolerant grading with critical words; mistake warning; Show next word;
drug cards; progress bar with Learned/Mastery and 169 h decay; one settings card plus an About page; color
stripes removed; "within" = "in"; drafts saved; bold-vs-highlight on misses; doubled words; errors marked in the
text; "or/and" fails; Claude-account limits found, then the **website** (GitHub Pages + Firebase Google sign-in,
autosave, two-device sync tests); Mistake warning renamed; skipped words warn, then stop; stop screen shows the
answer with bold; daily streak and date row; clearer back button; runs synced across devices with part-by-part
merging; next word prefers nearby matches (Ipratropium "acetylcholine" case); number words; one-step fixing; box
per drug; onto = to; optional joining "and" in mechanisms; warning-counts-as-miss switch (home and card screen);
Show answer checks typed text; fix parts never doubled; small-word typos ("te" for "the", Glucagon case); cut-off
grading of only the typed part (Magnesium Sulfate case).

`nwacc.js` last results: verbatim 100%, swapped words 98.5%, wrong word 86.8%, word from later 83.3%, inserted
word 93.9%.
