import json, re
from playwright.sync_api import sync_playwright
def ok(c,m): print(('PASS ' if c else 'FAIL ')+m)
html=open('/home/claude/protocol-drill/index.html').read()
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':390,'height':1000},device_scale_factor=2); errs=[]; pg.on('pageerror',lambda e: errs.append(str(e)))
    pg.goto('file:///home/claude/protocol-drill/index.html'); pg.wait_for_timeout(300)
    pg.evaluate("()=>{ localStorage.clear(); localStorage.setItem('pdrill:v1',JSON.stringify({settings:{mode:'keys',auto:false,v:3,live:false,prot:true},progress:{},custom:[],mnem:{},mnemLast:{},updatedAt:Date.now()})); }")
    pg.reload(); pg.wait_for_timeout(200)
    # Indications deck: answer with 2 wrong words far apart + wrong protocols
    pg.click('[data-act=start][data-id=ind]'); pg.wait_for_timeout(200)
    for attempt in range(30):
        pg.click('#reveal'); pg.wait_for_timeout(120)
        A=pg.inner_text('.fb-ans'); P=pg.inner_text('.fb-prot').replace('Protocols:','').strip()
        if len(A.split())>=10: break
        pg.fill('#ans',A); pg.fill('#prot',P); pg.keyboard.press('Enter'); pg.wait_for_timeout(500)
    # now this card was revealed (a miss): finish it, then it comes back later... instead use the retype screen as is
    W=A.split(); W[1]='zebra'; W[-2]='giraffe'
    pg.fill('#ans',' '.join(W)); pg.fill('#prot','999'); 
    # we're on the retype (full) screen after reveal; type it right to move on, and find a fresh card
    pg.fill('#ans',A); pg.fill('#prot',P); pg.keyboard.press('Enter'); pg.wait_for_timeout(600)
    for attempt in range(30):
        if pg.query_selector('#go') and pg.inner_text('#go')!='Check': pg.click('#go'); pg.wait_for_timeout(200); continue
        break
    drug=pg.inner_text('#drug')
    m=re.search(r'\["'+re.escape(drug.title())+r'", "((?:[^"\\]|\\.)*)", \[([^\]]*)\]',html.split('const IND=')[1]) or re.search(r'\["([^"]+)", "((?:[^"\\]|\\.)*)", \[([^\]]*)\]',html.split('const IND=')[1])
    names=re.findall(r'\["([^"]+)", "((?:[^"\\]|\\.)*)", \[([^\]]*)\]',html.split('const IND=')[1].split('];')[0])
    row=next(r for r in names if r[0].upper()==drug.upper())
    A=json.loads('"'+row[1]+'"'); P=', '.join(json.loads('['+row[2]+']'))
    W=A.split()
    if len(W)<8: print('short answer, card',drug,A)
    W[1]='zebra'; W[-2]='giraffe'
    pg.fill('#ans',' '.join(W)); pg.fill('#prot','999'); pg.keyboard.press('Enter'); pg.wait_for_timeout(300)
    head=pg.inner_text('.fb-head'); print('card:',drug,'| head:',head)
    ok(' of 2' not in pg.inner_text('.fb').lower(),'no "part 1 of 2" steps')
    ok(pg.locator('.fix').count()==2 and not pg.is_editable('#prot')==False and pg.is_editable('#ans'),'both the text box and the protocol box on one screen, both typeable')
    pg.screenshot(path='/home/claude/tests/onestep.png',full_page=True)
    parts=pg.inner_text('.fix .fix-text'); print('parts box:',parts)
    # type only the parts, wrong protocols -> fails, says what's left
    pg.fill('#ans',parts.replace(' … ',' ')); pg.dispatch_event('#ans','input'); pg.keyboard.press('Enter'); pg.wait_for_timeout(300)
    ok('Still not right' in pg.inner_text('.fb') and pg.query_selector('.fb.miss') is not None,'one Check: text right, protocols wrong -> stays, says what is left')
    pg.fill('#prot',P); pg.dispatch_event('#prot','input'); pg.keyboard.press('Enter'); pg.wait_for_timeout(600)
    ok(pg.query_selector('.fb.miss') is None,'second Check with both right moves on')
    print('errors:',errs); b.close()
