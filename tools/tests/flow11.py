import json
from playwright.sync_api import sync_playwright
C=json.load(open('/home/claude/packet/cards.json'))
MOA={c[0].split(' (')[0].upper():c[1] for c in C['moa']}
def typeit(pg,text):
    t=''
    for w in text.split(' '):
        t+=w+' '; pg.fill('#ans',t); pg.dispatch_event('#ans','input'); pg.wait_for_timeout(10)
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':390,'height':1000}); errs=[]; pg.on('pageerror',lambda e: errs.append(str(e)))
    pg.goto('file:///home/claude/protocol-drill/index.html'); pg.wait_for_timeout(300)
    pg.evaluate("()=>{ localStorage.clear(); }"); pg.reload(); pg.wait_for_timeout(300)
    pg.click('[data-act=start][data-id=moa]'); pg.wait_for_timeout(120)
    pg.click('label.switch-row:has(#liveSwitch)'); pg.wait_for_timeout(60)
    print('switch label:', pg.inner_text('label.switch-row:has(#liveSwitch)'))
    # 1) clean answer, switch on
    d=pg.inner_text('#drug'); typeit(pg,MOA[d]); warned=pg.is_visible('#liveWarn'); pg.click('#go'); pg.wait_for_timeout(100)
    print('clean:', d, '| warning shown:', warned, '|', pg.inner_text('.fb-head'), '|', pg.inner_text('#missTxt'))
    pg.click('#go'); pg.wait_for_timeout(100)
    # 2) trigger the warning with three wrong words, then fix it
    d=pg.inner_text('#drug'); words=MOA[d].split(' ')
    typeit(pg,' '.join(words[:3]+['zebra','giraffe','walrus'])); print('warning visible:', pg.is_visible('#liveWarn'), repr(pg.inner_text('#liveWarn')))
    pg.fill('#ans',''); typeit(pg,MOA[d]); print('warning after fixing:', pg.is_visible('#liveWarn'))
    pg.click('#go'); pg.wait_for_timeout(100)
    print('warned:', d, '|', pg.inner_text('.fb-head'), '|', pg.locator('.fb-small').last.inner_text(), '|', pg.inner_text('#missTxt'))
    # reload keeps the assisted flag mid-card
    pg.click('#go'); pg.wait_for_timeout(100)
    d=pg.inner_text('#drug'); words=MOA[d].split(' ')
    typeit(pg,' '.join(words[:3]+['zebra','giraffe','walrus'])); pg.reload(); pg.wait_for_timeout(300)
    pg.click('[data-act=start][data-id=moa]'); pg.wait_for_timeout(150)
    pg.fill('#ans',MOA[pg.inner_text('#drug')]); pg.click('#go'); pg.wait_for_timeout(100)
    print('warned, reloaded:', pg.inner_text('#drug'), '|', pg.inner_text('.fb-head'))
    print('errors:',errs); b.close()
