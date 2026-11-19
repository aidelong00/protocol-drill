import json, subprocess, time
from playwright.sync_api import sync_playwright
srv=subprocess.Popen(['python3','-m','http.server','8765','--bind','127.0.0.1'],cwd='/home/claude/web/site',stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(0.8)
FAKE=open('/home/claude/tests/fakefb.js').read()
URL='http://127.0.0.1:8765/'
def ok(c,m): print(('PASS ' if c else 'FAIL ')+m)
try:
  with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    # 1) no config: device-only
    ctx=b.new_context(viewport={'width':390,'height':900}); pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e: errs.append(str(e)))
    pg.goto(URL); pg.wait_for_timeout(400)
    ok(pg.locator('.acct').count()==0,'no config: no account row')
    ok('saved on this device' in pg.inner_text('#syncNote'),'no config: device note')
    pg.click('[data-act=start][data-id=moa]'); pg.wait_for_timeout(150); pg.type('#ans','Pancreatic'); pg.click('[data-act=home]'); pg.reload(); pg.wait_for_timeout(300)
    pg.click('[data-act=start][data-id=moa]'); pg.wait_for_timeout(200); ok(pg.input_value('#ans')=='Pancreatic','no config: typed text kept across reload')
    ok(not errs,'no config: no errors '+str(errs)); ctx.close()
    # 2) fake Firebase
    ctx=b.new_context(viewport={'width':390,'height':900}); errs=[]
    ctx.route('**/config.js',lambda r: r.fulfill(body="window.FIREBASE_CONFIG={apiKey:'x',authDomain:'x',projectId:'x'};",content_type='application/javascript'))
    ctx.route('**/firebase.js',lambda r: r.fulfill(body=FAKE,content_type='application/javascript'))
    pg=ctx.new_page(); pg.on('pageerror',lambda e: errs.append(str(e)))
    pg.goto(URL); pg.wait_for_timeout(300)
    ok(pg.locator('[data-act=signin]').count()==1,'signed out: Sign in button')
    pg.click('#auto'); pg.wait_for_timeout(100)   # anonymous change
    st=lambda: pg.evaluate("JSON.parse(localStorage.getItem('pdrill:v1'))")
    db=lambda: pg.evaluate("JSON.parse(localStorage.getItem('__fakedb')||'{}')")
    ok(st()['settings']['auto']==True,'anonymous change saved on device')
    pg.click('[data-act=signin]'); pg.wait_for_timeout(400)
    ok('a@example.com' in pg.inner_text('.acct'),'signed in as A shown')
    ok(db().get('users/A',{}).get('settings',{}).get('auto')==True,'first sign-in: device progress moved into A')
    ok('Google account' in pg.inner_text('#syncNote'),'synced note')
    pg.click('#auto'); pg.wait_for_timeout(1600)
    ok(db()['users/A']['settings']['auto']==False,'A change autosaves to account')
    pg.reload(); pg.wait_for_timeout(400)
    ok('a@example.com' in pg.inner_text('.acct') and st()['settings']['auto']==False,'reload: still signed in, progress kept')
    # start a run, then sign out: device cleared
    pg.click('[data-act=start][data-id=moa]'); pg.wait_for_timeout(150); pg.type('#ans','Pancreatic'); pg.click('[data-act=home]'); pg.wait_for_timeout(100)
    pg.click('[data-act=signout]'); pg.wait_for_timeout(300)
    ok(pg.locator('[data-act=signin]').count()==1 and st()['settings']['auto']==False and not st().get('uid'),'signed out: device reset')
    ok(pg.evaluate("Object.keys(localStorage).filter(k=>k.startsWith('pdrill:run:')).length")==0,'signed out: runs cleared')
    # B signs in: empty account, gets fresh store, not A's
    pg.evaluate("window.__nextUser={uid:'B',email:'b@example.com'}"); pg.click('[data-act=signin]'); pg.wait_for_timeout(400)
    ok('b@example.com' in pg.inner_text('.acct') and 'users/B' in db(),'B signed in, own doc created')
    pg.click('#auto'); pg.wait_for_timeout(1600); ok(db()['users/B']['settings']['auto']==True and db()['users/A']['settings']['auto']==False,'B change saved to B only')
    pg.click('[data-act=signout]'); pg.wait_for_timeout(200)
    pg.evaluate("window.__nextUser={uid:'A',email:'a@example.com'}"); pg.click('[data-act=signin]'); pg.wait_for_timeout(400)
    ok(st()['settings']['auto']==False and st().get('uid')=='A','A back: A progress restored')
    # account newer than device (other device saved): device takes account
    pg.evaluate("()=>{const d=JSON.parse(localStorage.getItem('__fakedb'));d['users/A'].settings.live=true;d['users/A'].updatedAt=Date.now()+5000;localStorage.setItem('__fakedb',JSON.stringify(d));}")
    pg.reload(); pg.wait_for_timeout(400); ok(st()['settings']['live']==True,'newer account copy wins on load')
    # device newer than account (offline edits): device pushed
    pg.evaluate("()=>{const s=JSON.parse(localStorage.getItem('pdrill:v1'));s.settings.mode='exact';s.updatedAt=Date.now()+99999;localStorage.setItem('pdrill:v1',JSON.stringify(s));}")
    pg.reload(); pg.wait_for_timeout(1700); ok(db()['users/A']['settings']['mode']=='exact','newer device copy pushed')
    # account unreachable: message, account not overwritten
    pg.add_init_script("window.__dbDown=true")
    before=db()['users/A']['updatedAt']; pg.reload(); pg.wait_for_timeout(500)
    ok('Couldn' in pg.inner_text('#syncNote'),'offline: message shown')
    pg.click('#auto'); pg.wait_for_timeout(1600); ok(db()['users/A']['updatedAt']==before,'offline: account not overwritten')
    pg.screenshot(path='/home/claude/tests/web_home.png',full_page=False)
    ok(not errs,'no errors '+str(errs)); b.close()
finally:
  srv.terminate()
