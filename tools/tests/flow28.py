import json, re
from playwright.sync_api import sync_playwright
def ok(c,m): print(('PASS ' if c else 'FAIL ')+m)
html=open('/home/claude/protocol-drill/index.html').read()
MOA=dict(re.findall(r'\["([^"]+)", "((?:[^"\\]|\\.)*)"\]',html.split('const MOA=')[1].split('];')[0]))
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':390,'height':1000},device_scale_factor=2); errs=[]; pg.on('pageerror',lambda e: errs.append(str(e)))
    def trial(warnMiss):
        pg.goto('file:///home/claude/protocol-drill/index.html'); pg.wait_for_timeout(200)
        pg.evaluate("w=>{ localStorage.clear(); localStorage.setItem('pdrill:v1',JSON.stringify({settings:{mode:'keys',auto:false,v:3,live:true,prot:true,warnMiss:w},progress:{},custom:[],mnem:{},mnemLast:{},updatedAt:Date.now()})); }",warnMiss)
        pg.reload(); pg.wait_for_timeout(200)
        lab=pg.inner_text('.set-card'); 
        pg.click('[data-act=start][data-id=moa]'); pg.wait_for_timeout(200)
        for _ in range(20):
            d=pg.inner_text('#drug'); hit=[v for k,v in MOA.items() if k.upper()==d.upper()]
            if hit: break
            pg.click('#reveal'); pg.wait_for_timeout(100); pg.fill('#ans',pg.inner_text('.fb-ans')); pg.keyboard.press('Enter'); pg.wait_for_timeout(500)
        A=json.loads('"'+hit[0]+'"'); W=A.split(); m0=int(pg.inner_text('#missTxt').split()[0])
        bad=' '.join(W[:3]+['zebra','giraffe']+W[3:6])+' '
        pg.click('#ans'); pg.keyboard.type(bad); pg.wait_for_timeout(100)
        warned=pg.is_visible('#liveWarn')
        pg.fill('#ans',A); pg.dispatch_event('#ans','input'); pg.keyboard.press('Enter'); pg.wait_for_timeout(300)
        head=pg.inner_text('.fb-head'); miss=str(int(pg.inner_text('#missTxt').split()[0])-m0); cost='on' if pg.is_checked('#warnMissSwitch') else 'off'
        return lab,warned,head,miss,cost
    lab,warned,head,miss,cost=trial(False)
    print('off:',warned,head,miss,cost); ok('Warning counts as a miss' in lab,'home has the new switch')
    ok(warned and head.upper()=='CORRECT' and miss.startswith('0'),'switch off: warning shown, fixed answer counts as correct')
    ok(cost=='off','drill switch shows it off')
    lab,warned,head,miss,cost=trial(True)
    print('on:',warned,head,miss,cost)
    ok(warned and miss.startswith('1') and cost=='on','switch on: warning makes it a miss; drill switch shows on')
    # flip it from the drill screen
    pg.click('label:has(#warnMissSwitch)'); pg.wait_for_timeout(100)
    ok(pg.evaluate("JSON.parse(localStorage.getItem('pdrill:v1')).settings.warnMiss")==False,'drill switch turns it off')
    pg.click('[data-act=home]'); pg.wait_for_timeout(150); ok(not pg.is_checked('#warnMissHome'),'home switch matches')
    print('errors:',errs); b.close()
