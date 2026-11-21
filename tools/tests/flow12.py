import json
from playwright.sync_api import sync_playwright
C=json.load(open('/home/claude/packet/cards.json'))
def A(deck,name): return [c for c in C[deck] if c[0]==name][0]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':390,'height':1000}); errs=[]; pg.on('pageerror',lambda e: errs.append(str(e)))
    pg.goto('file:///home/claude/protocol-drill/index.html'); pg.wait_for_timeout(300)
    pg.evaluate("()=>localStorage.clear()"); pg.reload(); pg.wait_for_timeout(300)
    head=lambda: pg.inner_text('.fb-head') if pg.query_selector('.fb-head') else '-'
    # Drug card: miss the mechanism, retype, then the redo from memory
    pg.click('[data-act=cards]'); pg.fill('#cardSearch','aspirin'); pg.wait_for_timeout(80); pg.click('#cardList [data-act=start]'); pg.wait_for_timeout(150)
    pg.fill('#ans','Antiplatelet agent, NSAID'); pg.keyboard.press('Enter'); pg.wait_for_timeout(200)
    print('class "NSAID" only ->', head()); pg.click('#go'); pg.wait_for_timeout(200)
    print('S2:', pg.inner_text('#ask'), '| next word visible:', pg.is_visible('#nwBtn'))
    moa=A('moa','Aspirin')[1]
    pg.fill('#ans', moa.replace('platelet','red cell')); pg.keyboard.press('Enter'); pg.wait_for_timeout(200)
    print('  wrong ->', head(), '| next word visible while copying the fix:', pg.is_visible('#nwBtn'))
    for _ in range(4):
        if pg.get_attribute('#ans','placeholder')=='Type it again from memory': break
        pg.fill('#ans', pg.locator('.fix-target, .fb-target').first.inner_text() if pg.query_selector('.fix-target, .fb-target') else moa); pg.keyboard.press('Enter'); pg.wait_for_timeout(500)
    print('  redo placeholder:', pg.get_attribute('#ans','placeholder'), '| next word visible:', pg.is_visible('#nwBtn'), '| enabled:', not pg.is_disabled('#nwBtn'))
    pg.fill('#ans','Inhibits platelet aggregation '); pg.click('#nwBtn'); pg.wait_for_timeout(100)
    print('  pressed ->', pg.inner_text('#nwHint'), '| disabled now:', pg.is_disabled('#nwBtn'))
    pg.fill('#ans','Inhibits platelet aggregation and inhibits synthesis of prostaglandin by cyclooxygenase; has analgesic and antipyretic effects.'); pg.keyboard.press('Enter'); pg.wait_for_timeout(200)
    print('  swapped + effects ->', head())
    # Regular deck: live stop, then retype from memory
    pg.goto('file:///home/claude/protocol-drill/index.html'); pg.wait_for_timeout(300); pg.click('[data-act=start][data-id=moa]'); pg.wait_for_timeout(150)
    pg.click('label.switch-row:has(#liveSwitch)'); pg.wait_for_timeout(60)
    d=pg.inner_text('#drug'); full=[c[1] for c in C['moa'] if c[0].split(' (')[0].upper()==d][0]
    words=full.split(' '); t=''
    for w in words[:3]+['zebra','giraffe','walrus','otter','badger','lemur']:
        t+=w+' '; pg.fill('#ans',t); pg.dispatch_event('#ans','input'); pg.wait_for_timeout(10)
        if head()=='STOPPED': break
    print('live stop on', d, '->', head(), '| next word visible:', pg.is_visible('#nwBtn'), '| enabled:', not pg.is_disabled('#nwBtn'))
    pg.click('#nwBtn'); pg.wait_for_timeout(100); print('  pressed ->', pg.inner_text('#nwHint'))
    pg.fill('#ans',full); pg.click('#go'); pg.wait_for_timeout(150); print('  finish ->', head())
    print('errors:',errs); b.close()
