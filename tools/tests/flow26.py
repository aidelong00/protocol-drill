import json, re
from playwright.sync_api import sync_playwright
def ok(c,m): print(('PASS ' if c else 'FAIL ')+m)
html=open('/home/claude/protocol-drill/index.html').read()
MOA=dict(re.findall(r'\["([^"]+)", "((?:[^"\\]|\\.)*)"\]',html.split('const MOA=')[1].split('];')[0]))
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':390,'height':1000},device_scale_factor=2); errs=[]; pg.on('pageerror',lambda e: errs.append(str(e)+' '+str(e.stack)[:600]))
    pg.goto('file:///home/claude/protocol-drill/index.html'); pg.wait_for_timeout(300)
    pg.evaluate("()=>{ localStorage.clear(); localStorage.setItem('pdrill:v1',JSON.stringify({settings:{mode:'keys',auto:false,v:3,live:false,prot:true},progress:{},custom:[],mnem:{},mnemLast:{},updatedAt:Date.now()})); }")
    pg.reload(); pg.wait_for_timeout(200); pg.click('[data-act=start][data-id=moa]'); pg.wait_for_timeout(200)
    for attempt in range(30):
        d=pg.inner_text('#drug'); A=json.loads('"'+next(v for k,v in MOA.items() if k.upper()==d.upper())+'"')
        W=A.split(); idx=[i for i,w in enumerate(W) if re.fullmatch(r'[A-Za-z]{6,}',w)]
        if len(W)>=18 and len(idx)>=2 and idx[-1]-idx[0]>10: break
        pg.fill('#ans',A); pg.keyboard.press('Enter'); pg.wait_for_timeout(200); pg.click('#go'); pg.wait_for_timeout(200)
    W[idx[0]]='zebra'; W[idx[-1]]='giraffe'
    print('attempts',attempt,'phase',pg.evaluate("JSON.parse(localStorage.getItem('pdrill:v1')).runs.moa.phase"),'go:',pg.inner_text('#go'))
    pg.fill('#ans',' '.join(W)); pg.click('#go'); pg.wait_for_timeout(300)
    print('fb:',pg.inner_text('#fb')[:200] if pg.query_selector('#fb') else None, '| typed:', pg.input_value('#ans')[:80], '| phase:', pg.evaluate("JSON.parse(localStorage.getItem('pdrill:v1')).runs.moa.phase"), '| card', d, '| errs', errs)
    head=pg.inner_text('.fb-head'); box=pg.inner_text('.fix .fix-text') if pg.query_selector('.fix .fix-text') else ''
    print('card:',d,'| head:',head,'| box:',box)
    ok('these parts' in head.lower() and '…' in box and pg.locator('.fix').count()==1,'two parts in one box, one step')
    pg.screenshot(path='/home/claude/tests/twoparts.png',full_page=True)
    pg.fill('#ans',box.replace('…',' ')); pg.dispatch_event('#ans','input'); pg.keyboard.press('Enter'); pg.wait_for_timeout(600)
    ok(pg.query_selector('.fb.miss') is None,'one Check with both parts moves on')
    print('errors:',errs); b.close()
