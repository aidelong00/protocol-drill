import json, re
from playwright.sync_api import sync_playwright
def ok(c,m): print(('PASS ' if c else 'FAIL ')+m)
html=open('/home/claude/protocol-drill/index.html').read()
MOA=dict(re.findall(r'\["([^"]+)", "((?:[^"\\]|\\.)*)"\]',html.split('const MOA=')[1].split('];')[0]))
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':390,'height':1100},device_scale_factor=2); errs=[]; pg.on('pageerror',lambda e: errs.append(str(e)))
    def open_card(name,live):
        pg.goto('file:///home/claude/protocol-drill/index.html'); pg.wait_for_timeout(200)
        pg.evaluate("l=>{ localStorage.clear(); localStorage.setItem('pdrill:v1',JSON.stringify({settings:{mode:'keys',auto:false,v:3,live:l,prot:true},progress:{},custom:[],mnem:{},mnemLast:{},updatedAt:Date.now()})); }",live)
        pg.reload(); pg.wait_for_timeout(200); pg.click('[data-act=start][data-id=moa]'); pg.wait_for_timeout(150)
        for _ in range(60):
            if pg.inner_text('#drug').upper()==name.upper(): return
            d=pg.inner_text('#drug'); a=json.loads('"'+next((v for k,v in MOA.items() if k.upper()==d.upper() or k.upper().startswith(d.upper()+' (')),'x')+'"')
            pg.fill('#ans',a); pg.keyboard.press('Enter'); pg.wait_for_timeout(150)
            if pg.query_selector('#go') and pg.inner_text('#go')!='Check': pg.click('#go'); pg.wait_for_timeout(150)
    # 1) your Magnesium Sulfate answer, then Show answer
    open_card('Magnesium Sulfate',True)
    yours='depresses cns, blocks peripheral neuromuscular transmission, produces anticonvulsant effects, decreases amount of ach released at end plate by motor nerve impulese. Slows conduction of sa'
    pg.click('#ans'); pg.keyboard.type(yours); pg.wait_for_timeout(100)
    print('warning showing:',pg.is_visible('#liveWarn'),'| drug:',pg.inner_text('#drug'),'| fb:',(pg.inner_text('#fb') or '')[:200].replace('\n',' | '),'| phase:',pg.evaluate("JSON.parse(localStorage.getItem('pdrill:v1')).runs.moa.phase"))
    m0=pg.inner_text('#missTxt')
    pg.click('#reveal'); pg.wait_for_timeout(300)
    fb=pg.inner_text('.fb'); print(fb[:400].replace('\n',' | '))
    ok('retype the whole' not in fb.lower() and 'keep going from where you left off' in fb.lower(),'cut off: keep going from where you left off, not retype the whole answer')
    ok(pg.input_value('#ans').strip()==yours.strip(),'your text stays in the box')
    bolds=[e.inner_text() for e in pg.query_selector_all('.fb-ans b.xb')]; print('bold:',bolds)
    ok(not any(w in ' '.join(bolds) for w in ['myocardium','prolongs','time']),'nothing past where you got is marked')
    pg.screenshot(path='/home/claude/tests/cutoff.png',full_page=True)
    # finish it correctly -> correct (counted as a miss once)
    A=json.loads('"'+MOA['Magnesium Sulfate']+'"')
    pg.fill('#ans',A); pg.dispatch_event('#ans','input'); pg.keyboard.press('Enter'); pg.wait_for_timeout(400)
    print('after finishing:',pg.inner_text('.fb-head') if pg.query_selector('.fb-head') else '', '| missed:',pg.inner_text('#missTxt'))
    ok(pg.query_selector('.fb.miss') is None,'finishing it moves on')
    # 2) Check with a warning up, partway -> same cut-off
    open_card('Glucagon',True)
    pg.click('#ans'); pg.keyboard.type('A hormone naturally produced by pancreatic beta cells of the islets of Langerhans. Causes '); pg.wait_for_timeout(100)
    print('warning showing:',pg.is_visible('#liveWarn'))
    pg.click('#go'); pg.wait_for_timeout(300); fb=pg.inner_text('.fb'); print(fb[:250].replace('\n',' | '))
    ok('keep going' in fb.lower() and 'beta' not in [e.inner_text() for e in pg.query_selector_all('.fb-ans b.xb')],'Check with the warning up, partway: cut off, the wrong word in bold')
    # 3) Check with no warning, full answer with one mistake -> normal fix
    open_card('Glucagon',False)
    A=json.loads('"'+MOA['Glucagon']+'"'); pg.fill('#ans',A.replace('alpha','beta')); pg.click('#go'); pg.wait_for_timeout(300)
    ok('fix just this part' in pg.inner_text('.fb-head').lower(),'whole answer with one mistake: fix just that part, as before')
    # 4) stopped by the warning while typing on, then Check before finishing -> keep going, not "retype the whole answer"
    open_card('Magnesium Sulfate',True)
    t='depresses cns, blocks peripheral neuromuscular transmission, produces anticonvulsant effects, decreases amount of ach released at end plate by motor nerve impulese. Slows conduction of sa node impulse formation in myocardium and'
    pg.click('#ans')
    for w in t.split(' '):
        pg.keyboard.type(w+' ')
        if pg.query_selector('.fb-head') and 'STOPPED' in pg.inner_text('.fb-head').upper(): break
    print('stopped at',repr(w),'| box now:',pg.input_value('#ans')[-50:])
    pg.keyboard.type('Slows rate of sinoatrial node'); pg.keyboard.press('Enter'); pg.wait_for_timeout(300)
    fb=pg.inner_text('.fb'); print(fb[:200].replace('\n',' | '))
    ok('retype the whole' not in fb.lower() and 'keep going' in fb.lower(),'after a stop, Check partway: keep going from where you left off, unreached part not counted')
    A=json.loads('"'+MOA['Magnesium Sulfate']+'"'); rest=A[A.index('node')+4:]
    pg.keyboard.type(rest); pg.keyboard.press('Enter'); pg.wait_for_timeout(400)
    ok(pg.query_selector('.fb.miss') is None,'finishing from there moves on ('+(pg.inner_text('.fb-head') if pg.query_selector('.fb-head') else '')+')')
    print('errors:',errs); b.close()
