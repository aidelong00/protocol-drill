#!/usr/bin/env python3
"""Builds the website version of Protocol Drill from the artifact's index.html.

The artifact saves through Claude; the website saves through Google sign-in (Firebase Auth +
Firestore lite). Everything else (cards, grading, screens) is the same file, so updates are made
once in /home/claude/protocol-drill/index.html and this script is re-run.
"""
import re, sys, pathlib

SRC = pathlib.Path('/home/claude/protocol-drill/index.html')
OUT = pathlib.Path('/home/claude/web/site/index.html')
s = SRC.read_text()

def rep(a, b, count=1):
    global s
    n = s.count(a)
    if n != count:
        sys.exit(f'build-web: expected {count} match(es), found {n}: {a[:70]!r}')
    s = s.replace(a, b)

# ---- <head>: app-like on phones, and load the config + Firebase before the app script
rep('<title>Protocol Drill</title>', '''<title>Protocol Drill</title>
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="icon-192.png">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Protocol Drill">
<meta name="theme-color" content="#E3E6EA" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0E1116" media="(prefers-color-scheme: dark)">''')
m = re.search(r'\n<script>\n', s)
if not m:
    sys.exit('build-web: main <script> not found')
s = s[:m.start()] + '\n<script src="config.js"></script>\n<script src="firebase.js"></script>' + s[m.start():]

# ---- CSS for the account row
rep('.set-card{', '''.acct{background:var(--card);border:1px solid var(--rule);border-radius:14px;display:flex;align-items:center;justify-content:space-between;gap:12px;padding:12px 16px}
.acct-txt{font-size:14px;color:var(--muted);min-width:0;overflow-wrap:anywhere}
.acct-txt b{color:var(--ink);font-weight:700}
.acct-btn{flex:none;border:1.5px solid var(--ink);background:transparent;color:var(--ink);font:700 14px/1 var(--font-body);padding:9px 14px;border-radius:999px;cursor:pointer}
.acct-btn.primary{background:var(--ink);color:var(--card)}
.acct-err{margin:-6px 2px 0;font-size:13px;color:var(--accent)}
.set-card{''')

# ---- store remembers whose progress it is
rep("  f.updatedAt=+s.updatedAt||0; return f;", "  f.uid=typeof s.uid==='string'?s.uid:'';\n  f.updatedAt=+s.updatedAt||0; return f;")

# ---- replace the Claude sync layer with Google sign-in
start = s.index('/* Account sync:')
end = s.index('function updateSync(){')
end = s.index('\n', end) + 1
WEB_SYNC = r'''/* Account sync: Google sign-in (Firebase). Each person's progress is one private document, users/<uid>,
   that only they can read or write. Without signing in, progress stays on this device. */
let remote=null, fbAuth=null, fdb=null, fbUser=null, authReady=false, signErr='', syncErr='';
let saveTimer=null, saving=false, again=false, retryTimer=null;
const FBL=()=>window.FBLIB, FBC=()=>window.FIREBASE_CONFIG;
const fbOn=()=>!!(FBL()&&FBC()&&FBC().apiKey);
function clearRuns(){ try{ Object.keys(localStorage).filter(k=>k.startsWith('pdrill:run:')).forEach(k=>localStorage.removeItem(k)); }catch(e){} }
function scheduleRemote(){ if(!remote) return; clearTimeout(saveTimer); saveTimer=setTimeout(flushRemote,1200); }
async function flushRemote(){
  clearTimeout(saveTimer); saveTimer=null;
  if(!remote) return; if(saving){again=true;return;}
  saving=true; const ref=remote;
  try{ await FBL().setDoc(ref,JSON.parse(JSON.stringify(store))); if(syncErr){ syncErr=''; updateSync(); } }
  catch(e){
    syncErr='Couldn’t reach your account just now. Your progress is kept on this device and will be saved when you’re back online.';
    updateSync(); clearTimeout(retryTimer); retryTimer=setTimeout(scheduleRemote,20000);
  }
  saving=false; if(again){again=false; flushRemote();}
}
document.addEventListener('visibilitychange',()=>{ if(document.visibilityState==='hidden'&&remote&&saveTimer) flushRemote(); });
window.addEventListener('online',()=>{ if(remote&&syncErr) scheduleRemote(); else if(fbUser&&!remote) onUser(fbUser); });
function initRemote(){
  if(!fbOn()){ updateSync(); return; }
  try{
    const L=FBL(), app=L.initializeApp(FBC());
    fbAuth=L.getAuth(app); fdb=L.getFirestore(app);
    L.getRedirectResult(fbAuth).catch(e=>{ signErr=signInMsg(e); if(ui.screen==='home') render(); });
    L.onAuthStateChanged(fbAuth,u=>{ authReady=true; onUser(u); });
  }catch(e){ authReady=true; updateSync(); }
}
async function onUser(u){
  fbUser=u||null; remote=null; clearTimeout(retryTimer);
  if(!u){ updateSync(); if(ui.screen==='home') render(); return; }
  signErr='';
  const L=FBL(), ref=L.doc(fdb,'users',u.uid);
  try{
    const snap=await Promise.race([L.getDoc(ref),new Promise((_,rej)=>setTimeout(()=>rej({code:'timeout'}),12000))]);
    if(fbUser!==u) return;
    const mine=store.uid===u.uid;
    if(snap.exists()){
      const d=cleanStore(JSON.parse(JSON.stringify(snap.data()||{})));
      if(mine&&store.updatedAt>d.updatedAt){ mergeStreak(store,d); remote=ref; scheduleRemote(); }
      else if(!mine||d.updatedAt>store.updatedAt){
        if(store.uid&&!mine) clearRuns();
        if(mine) mergeStreak(d,store);
        store=d; store.uid=u.uid; persistLocal(); remote=ref;
      } else remote=ref;
    } else {
      // First sign-in for this account: keep what's on this device unless it belongs to someone else.
      if(store.uid&&!mine){ store=freshStore(); clearRuns(); }
      store.uid=u.uid; if(!store.updatedAt) store.updatedAt=Date.now(); persistLocal();
      remote=ref; flushRemote();
    }
    syncErr='';
  }catch(e){
    // Can't tell what's in the account yet, so don't overwrite it; try again shortly.
    syncErr='Couldn’t reach your account just now. Your progress is kept on this device and will be saved when you’re back online.';
    retryTimer=setTimeout(()=>{ if(fbUser===u) onUser(u); },20000);
  }
  updateSync(); if(ui.screen==='home') render();
}
function signInMsg(e){
  const c=e&&e.code||'';
  if(!c||c==='auth/popup-closed-by-user'||c==='auth/cancelled-popup-request'||c==='auth/user-cancelled') return '';
  if(c==='auth/unauthorized-domain') return 'Sign-in isn’t set up for this web address yet.';
  if(c==='auth/network-request-failed') return 'No connection. Try again when you’re online.';
  return 'Couldn’t sign in ('+c.replace('auth/','')+'). Try again.';
}
async function doSignIn(){
  if(!fbAuth) return;
  const L=FBL(), p=new L.GoogleAuthProvider(); p.setCustomParameters({prompt:'select_account'});
  signErr='';
  try{ await L.signInWithPopup(fbAuth,p); }
  catch(e){
    const c=e&&e.code||'';
    if(c==='auth/popup-blocked'||c==='auth/operation-not-supported-in-this-environment'){
      try{ await L.signInWithRedirect(fbAuth,p); return; }catch(e2){ signErr=signInMsg(e2); }
    } else signErr=signInMsg(e);
    if(ui.screen==='home') render();
  }
}
async function doSignOut(){
  if(!fbAuth) return;
  if(remote) await flushRemote();
  remote=null;
  try{ await FBL().signOut(fbAuth); }catch(e){}
  store=freshStore(); persistLocal(); clearRuns(); run=null; result=null;
  ui.screen='home'; render();
}
function acctHTML(){
  if(!fbOn()) return '';
  if(!authReady) return '<section class="acct"><span class="acct-txt">Checking sign-in…</span></section>';
  if(fbUser) return `<section class="acct"><span class="acct-txt"><b>${esc(fbUser.email||fbUser.displayName||'Signed in')}</b></span><button class="acct-btn" data-act="signout">Sign out</button></section>`;
  return `<section class="acct"><span class="acct-txt">Sign in to save your progress to your Google account</span><button class="acct-btn primary" data-act="signin">Sign in with Google</button></section>${signErr?`<p class="acct-err">${esc(signErr)}</p>`:''}`;
}
function updateSync(){
  const el=document.getElementById('syncNote'); if(!el) return;
  el.textContent=syncErr?syncErr:(remote&&fbUser)?'Your progress saves automatically to your Google account.':'Your progress is saved on this device. Sign in to keep it on any device.';
}
'''
s = s[:start] + WEB_SYNC + s[end:]

# ---- account row on the home screen, and the two buttons
rep('  ${dayRow()}\n  <section class="set-card" aria-label="Settings">', '  ${acctHTML()}\n  ${dayRow()}\n  <section class="set-card" aria-label="Settings">')
rep("    case 'about': ui.screen='about'; render(); window.scrollTo({top:0}); break;",
    "    case 'about': ui.screen='about'; render(); window.scrollTo({top:0}); break;\n    case 'signin': doSignIn(); break;\n    case 'signout': doSignOut(); break;")

# ---- no Claude hot-reload on the website
rep("try{ window.claude?.hot?.snapshot?.(()=>({ui:{screen:ui.screen,deckId:ui.deckId,editId:ui.editId,q:ui.q},run,result})); }catch(e){}\nif(window.claude?.hot?.ready) window.claude.hot.ready(start); else start(window.claude?.hot?.data??{});",
    "start({});")

if 'window.claude' in s:
    sys.exit('build-web: a window.claude reference is left')
OUT.write_text(s)
print('built', OUT, len(s), 'bytes')
