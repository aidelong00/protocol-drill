# Two devices, one Google account: the run in progress and deck progress follow you between them.
import json, subprocess, time, re
from playwright.sync_api import sync_playwright
srv=subprocess.Popen(['python3','-m','http.server','8766','--bind','127.0.0.1'],cwd='/home/claude/web/site',stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(0.8)
FAKE=open('/home/claude/tests/fakefb.js').read(); URL='http://127.0.0.1:8766/'
DB={}
html=open('/home/claude/protocol-drill/index.html').read()
MOA=dict(re.findall(r'\["([^"]+)", "((?:[^"\\]|\\.)*)"\]',html.split('const MOA=')[1].split('];')[0]))
def ok(c,m): print(('PASS ' if c else 'FAIL ')+m)
try:
  with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    def device(name):
        ctx=b.new_context(viewport={'width':390,'height':900})
        ctx.route('**/config.js',lambda r: r.fulfill(body="window.FIREBASE_CONFIG={apiKey:'x'};",content_type='application/javascript'))
        ctx.route('**/firebase.js',lambda r: r.fulfill(body=FAKE,content_type='application/javascript'))
        ctx.expose_function('__srvGet',lambda path: DB.get(path))
        def _set(path,v): DB[path]=v
        ctx.expose_function('__srvSet',_set)
        pg=ctx.new_page(); pg.errs=[]; pg.on('pageerror',lambda e: pg.errs.append(str(e)))
        pg.add_init_script("localStorage.setItem('__fakeauth',JSON.stringify({uid:'U',email:'me@example.com'}))")
        pg.goto(URL); pg.wait_for_timeout(500); return pg
    A=device('A'); B=device('B')
    def run_of(pg,deck='moa'): return pg.evaluate(f"(JSON.parse(localStorage.getItem('pdrill:v1')).runs||{{}})['{deck}']||null")
    def answer(pg):
        d=pg.inner_text('#drug'); a=MOA.get(d.title()) or next(v for k,v in MOA.items() if k.upper()==d.upper())
        pg.fill('#ans',json.loads('"'+a+'"')); pg.keyboard.press('Enter'); pg.wait_for_timeout(200); pg.click('#go'); pg.wait_for_timeout(200)
        return d
    def show(pg): pg.evaluate("document.dispatchEvent(new Event('visibilitychange')); window.dispatchEvent(new Event('focus'))"); pg.wait_for_timeout(500)
    # A: two cards
    A.click('[data-act=start][data-id=moa]'); A.wait_for_timeout(200)
    answer(A); answer(A); curA=A.inner_text('#drug'); A.wait_for_timeout(1500)
    ok(len(json.loads(DB['users/U'])['runs']['moa']['cleared'])==2,'A: run with 2 cleared saved to the account')
    # B: comes back to the app (stale), sees the run
    show(B)
    ok('2/26' in B.inner_text('#app'),'B: home shows the run in progress (2/26) after switching back to it')
    B.click('[data-act=start][data-id=moa]'); B.wait_for_timeout(200)
    ok(B.inner_text('#drug')==curA and '2 of 26' in B.inner_text('#barTxt'),'B: resumes on the same card as A')
    answer(B); curB=B.inner_text('#drug'); B.wait_for_timeout(1500)
    # A is still sitting on the drill screen: switching back catches up
    show(A)
    ok(A.inner_text('#drug')==curB and '3 of 26' in A.inner_text('#barTxt'),'A: drill on screen catches up to B (3 cleared, same card)')
    # typed but not submitted on A shows up on B
    A.fill('#ans','Pancreatic hormone'); A.dispatch_event('#ans','input'); A.wait_for_timeout(1500)
    show(B); ok(B.input_value('#ans')=='Pancreatic hormone','B: half-typed answer from A shows up')
    # progress parts: A toggles a setting, B (stale) finishes a different thing -> both kept
    A.click('[data-act=home]'); A.wait_for_timeout(200); A.click('#auto'); A.wait_for_timeout(1500)
    B.click('[data-act=home]'); B.wait_for_timeout(200)
    B.evaluate("()=>{}")
    B.click('[data-act=start][data-id=class]'); B.wait_for_timeout(200); B.fill('#ans','wrong'); B.keyboard.press('Enter'); B.wait_for_timeout(1600)
    d=json.loads(DB['users/U'])
    ok(d['settings']['auto']==True and 'class' in d['runs'] and d['progress'].get('class',{}).get('strikes',0)>=0 and d['runs']['moa']['cleared'].__len__()==3,'B saving later kept A\'s setting change and the moa run')
    # restart on B ends the moa run; A (on home) sees it gone after switching back
    B.click('[data-act=home]'); B.wait_for_timeout(200); B.click('[data-act=start][data-id=moa]'); B.wait_for_timeout(200)
    B.click('#restartBtn'); B.wait_for_timeout(80); B.click('#restartBtn'); B.wait_for_timeout(1600)
    show(A); ok('3/26' not in A.inner_text('#app'),'A: restarted run on B is not resurrected on A')
    ok(not A.errs and not B.errs,'no errors '+str(A.errs+B.errs))
    b.close()
finally: srv.terminate()
