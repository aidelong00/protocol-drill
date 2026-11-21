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
    pg.reload(); pg.wait_for_timeout(200); pg.click('[data-act=start][data-id=moa]'); pg.wait_for_timeout(200)
    ans_of=lambda: json.loads('"'+next(v for k,v in MOA.items() if k.upper()==pg.inner_text('#drug').upper())+'"')
    # 1) full right answer, then Show answer -> counts as correct
    A=ans_of(); pg.fill('#ans',A); pg.click('#reveal'); pg.wait_for_timeout(300)
    ok(pg.inner_text('.fb-head').upper()=='CORRECT' and pg.inner_text('#missTxt').startswith('0'),'right answer + Show answer = correct')
    pg.click('#go'); pg.wait_for_timeout(200)
    # 2) first half typed, Show answer -> only the rest to type
    A=ans_of(); W=A.split(); half=' '.join(W[:len(W)//2])
    pg.fill('#ans',half); pg.click('#reveal'); pg.wait_for_timeout(300)
    head=pg.inner_text('.fb-head'); box=pg.inner_text('.fix .fix-text') if pg.query_selector('.fix .fix-text') else ''
    print('half typed ->',head,'| retype:',box[:120])
    ok('keep going' in pg.inner_text('.fb').lower() and pg.input_value('#ans').strip()==half.strip(),'half typed + Show answer: keep going from where you left off, text kept')
    # 3) nothing typed, Show answer -> answer shown, retype whole
    pg.keyboard.type(' '+' '.join(W[len(W)//2:])); pg.keyboard.press('Enter'); pg.wait_for_timeout(500)
    if pg.query_selector('#go') and pg.inner_text('#go')!='Check': pg.click('#go'); pg.wait_for_timeout(200)
    pg.fill('#ans',''); pg.click('#reveal'); pg.wait_for_timeout(300)
    ok('whole answer' in pg.inner_text('.fb').lower() or pg.inner_text('.fb-head').upper()=='ANSWER','nothing typed + Show answer: shows the answer as before')
    print('errors:',errs); b.close()
