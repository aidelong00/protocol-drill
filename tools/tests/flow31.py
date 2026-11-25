import json, re
from playwright.sync_api import sync_playwright
def ok(c,m): print(('PASS ' if c else 'FAIL ')+m)
html=open('/home/claude/protocol-drill/index.html').read()
MOA=dict(re.findall(r'\["([^"]+)", "((?:[^"\\]|\\.)*)"\]',html.split('const MOA=')[1].split('];')[0]))
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':390,'height':1000},device_scale_factor=2); errs=[]; pg.on('pageerror',lambda e: errs.append(str(e)))
    pg.goto('file:///home/claude/protocol-drill/index.html'); pg.wait_for_timeout(200)
    pg.evaluate("()=>{ localStorage.clear(); localStorage.setItem('pdrill:v1',JSON.stringify({settings:{mode:'keys',auto:false,v:3,live:false,prot:true},progress:{},custom:[],mnem:{},mnemLast:{},updatedAt:Date.now()})); }")
    pg.reload(); pg.wait_for_timeout(200)
    run=lambda k='moa': pg.evaluate(f"JSON.parse(localStorage.getItem('pdrill:v1')).runs['{k}']")
    pg.click('[data-act=start][data-id=moa]'); pg.wait_for_timeout(150)
    ok(pg.is_visible('#skipBtn'),'Skip for now shows on a fresh card')
    first=pg.inner_text('#drug'); r0=run(); 
    pg.fill('#ans','half typed'); pg.click('#skipBtn'); pg.wait_for_timeout(200)
    r1=run(); print('skipped',first,'-> now',pg.inner_text('#drug'),'| queue end:',r1['queue'][-1]==r0['cur'],'| misses',r1['misses'])
    ok(pg.inner_text('#drug')!=first and r1['queue'][-1]==r0['cur'] and r1['misses']==0 and pg.input_value('#ans')=='','skip: next card, skipped one at the end of the line, not a miss, box cleared')
    pg.screenshot(path='/home/claude/tests/skip.png',clip={'x':0,'y':300,'width':390,'height':700})
    # skip after using next word: counts as a miss
    if pg.is_visible('#nwBtn'):
        second=pg.inner_text('#drug'); pg.click('#nwBtn'); pg.wait_for_timeout(100); pg.click('#skipBtn'); pg.wait_for_timeout(200)
        ok(run()['misses']==1,'skipping after Show next word still counts that hint as a miss')
    # drug card: skip a section
    pg.click('[data-act=home]'); pg.wait_for_timeout(100); pg.click('[data-act=cards]'); pg.fill('#cardSearch','glucagon'); pg.wait_for_timeout(80); pg.click('#cardList [data-act=start]'); pg.wait_for_timeout(200)
    sec=pg.inner_text('#ask'); pg.click('#skipBtn'); pg.wait_for_timeout(200)
    rc=run('card:Glucagon'); print('drug card:',sec,'->',pg.inner_text('#ask'))
    ok('2 OF' in pg.inner_text('#ask').upper() or 'MECHANISM' in pg.inner_text('#ask').upper(),'drug card: skipping goes to the next section')
    ok(rc['queue'][-1]==0 or rc['queue'][-1]==rc['ids'][0],'drug card: skipped section comes back after the others')
    # last card left: no skip
    pg.evaluate("()=>{ const s=JSON.parse(localStorage.getItem('pdrill:v1')); const r=s.runs['card:Glucagon']; r.queue=[]; r.t=Date.now(); localStorage.setItem('pdrill:v1',JSON.stringify(s)); }")
    pg.reload(); pg.wait_for_timeout(200)
    pg.click('[data-act=cards]'); pg.wait_for_timeout(100); pg.fill('#cardSearch','glucagon'); pg.wait_for_timeout(80); pg.click('#cardList [data-act=start]'); pg.wait_for_timeout(200)
    ok(not pg.is_visible('#skipBtn'),'no Skip on the last card left')
    print('errors:',errs); b.close()
