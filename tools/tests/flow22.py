from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':390,'height':900},device_scale_factor=2); pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e: errs.append(str(e)))
    pg.goto('file:///home/claude/protocol-drill/index.html'); pg.wait_for_timeout(300)
    pg.evaluate("()=>{ localStorage.clear(); localStorage.setItem('pdrill:v1',JSON.stringify({settings:{mode:'keys',auto:false,v:3,live:true,prot:true},progress:{},custom:[],mnem:{},mnemLast:{},updatedAt:Date.now()})); }")
    pg.reload(); pg.wait_for_timeout(200)
    print('home label:', [e.inner_text() for e in pg.query_selector_all('.set-row')][1].split('\n')[0])
    pg.click('[data-act=cards]'); pg.fill('#cardSearch','calcium chloride'); pg.wait_for_timeout(80); pg.click('#cardList [data-act=start]'); pg.wait_for_timeout(150)
    # get to the mechanism section
    for _ in range(3):
        if 'MECHANISM' in pg.inner_text('.ask, h2, .q-title, #ask').upper() if pg.query_selector('#ask') else False: break
        pg.click('#reveal'); pg.wait_for_timeout(100); a=pg.inner_text('.fb-ans'); pg.fill('#ans',a); pg.dispatch_event('#ans','input'); pg.keyboard.press('Enter'); pg.wait_for_timeout(500)
        for _ in range(4):
            if pg.query_selector('.fb.miss') is None and pg.query_selector('#go') and pg.inner_text('#go')!='Check': pg.click('#go'); pg.wait_for_timeout(200)
            elif pg.query_selector('.fb.miss'): pg.fill('#ans',a); pg.keyboard.press('Enter'); pg.wait_for_timeout(500)
            else: break
    print('section:', pg.inner_text('#ask'))
    pg.screenshot(path='/home/claude/tests/live_skip0.png')
    print('switch label:', pg.inner_text('label.switch-row') if pg.query_selector('label.switch-row') else None)
    text='Essential regulator for the excitation threshold of nerves and muscles, causes significant increase in myocardial contractility is the antidote for some calcium chan'
    pg.click('#ans')
    for w in text.split(' '):
        pg.keyboard.type(w+' ')
        if pg.query_selector('.fb.miss') or pg.is_visible('#liveWarn'): break
    pg.wait_for_timeout(200)
    print('stopped after:', repr(w), '| box now:', repr(pg.input_value('#ans')))
    fb=pg.query_selector('.fb'); print('feedback:', pg.inner_text('.fb')[:300] if fb else None)
    pg.screenshot(path='/home/claude/tests/live_skip.png')
    print('errors:',errs); b.close()
