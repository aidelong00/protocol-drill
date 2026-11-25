# Claude version: two devices, same Claude account (fake window.claude db) - the run follows you.
import json, re
from playwright.sync_api import sync_playwright
DB={}
html=open('/home/claude/protocol-drill/index.html').read()
MOA=dict(re.findall(r'\["([^"]+)", "((?:[^"\\]|\\.)*)"\]',html.split('const MOA=')[1].split('];')[0]))
FAKE="""window.claude={use:async n=>{
  if(n==='user') return {id:async()=>'U1'};
  if(n==='db') return {doc:p=>({get:async()=>{ const j=await window.__srvGet(p); return {exists:!!j,data:()=>j?JSON.parse(j):null}; }, set:async v=>{ await window.__srvSet(p,JSON.stringify(v)); }})};
  return null; }};"""
def ok(c,m): print(('PASS ' if c else 'FAIL ')+m)
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    def device():
        ctx=b.new_context(viewport={'width':390,'height':900})
        ctx.expose_function('__srvGet',lambda path: DB.get(path))
        def _set(path,v): DB[path]=v
        ctx.expose_function('__srvSet',_set)
        ctx.add_init_script(FAKE)
        pg=ctx.new_page(); pg.errs=[]; pg.on('pageerror',lambda e: pg.errs.append(str(e)))
        pg.goto('file:///home/claude/protocol-drill/index.html'); pg.wait_for_timeout(500); return pg
    A=device(); B=device()
    def answer(pg):
        d=pg.inner_text('#drug'); a=next(v for k,v in MOA.items() if k.upper()==d.upper() or k.upper().startswith(d.upper()+' ('))
        pg.fill('#ans',json.loads('"'+a+'"')); pg.keyboard.press('Enter'); pg.wait_for_timeout(200); pg.click('#go'); pg.wait_for_timeout(200)
    def show(pg): pg.evaluate("document.dispatchEvent(new Event('visibilitychange')); window.dispatchEvent(new Event('focus'))"); pg.wait_for_timeout(500)
    ok('Claude account' in A.inner_text('#syncNote'),'A: synced to (fake) Claude account')
    A.click('[data-act=start][data-id=moa]'); A.wait_for_timeout(200); answer(A); answer(A); cur=A.inner_text('#drug'); A.wait_for_timeout(1500)
    show(B); ok('2/26' in B.inner_text('#app'),'B: sees the run in progress')
    B.click('[data-act=start][data-id=moa]'); B.wait_for_timeout(200); ok(B.inner_text('#drug')==cur,'B: resumes on the same card')
    answer(B); B.wait_for_timeout(1500); show(A); ok('3 of 26' in A.inner_text('#barTxt'),'A: catches up')
    ok(not A.errs and not B.errs,'no errors '+str(A.errs+B.errs)); b.close()
