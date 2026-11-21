from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':390,'height':900},device_scale_factor=2); pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e: errs.append(str(e)))
    pg.goto('file:///home/claude/protocol-drill/index.html'); pg.wait_for_timeout(300)
    pg.evaluate("()=>{ localStorage.clear(); localStorage.setItem('pdrill:v1',JSON.stringify({settings:{mode:'keys',auto:false,v:3,live:false,prot:true},progress:{},custom:[],mnem:{},mnemLast:{},updatedAt:Date.now()})); }")
    def card(q):
        pg.goto('file:///home/claude/protocol-drill/index.html'); pg.wait_for_timeout(200)
        pg.click('[data-act=cards]'); pg.fill('#cardSearch',q); pg.wait_for_timeout(80); pg.click('#cardList [data-act=start]'); pg.wait_for_timeout(150)
    card('ondansetron')
    pg.fill('#ans','Antiemetic agent'); pg.keyboard.press('Enter'); pg.wait_for_timeout(150)
    print('1)', pg.inner_text('.fb-head'), '| top highlights:', pg.locator('.fb-ans .w.miss').count(), '| top bold:', [e.inner_text() for e in pg.query_selector_all('.fb-ans b.xb')], '| box highlights:', [e.inner_text() for e in pg.query_selector_all('.fix-text .w.miss')])
    pg.screenshot(path='part_retype.png',full_page=True)
    pg.fill('#ans','Antiemetic agent agent'); pg.keyboard.press('Enter'); pg.wait_for_timeout(200)
    print('   part retyped with a wrong word:', pg.inner_text('.fb-still') if pg.query_selector('.fb-still') else None)
    # mechanism deck: Show answer, then full retype with "and and", then extra "not"
    pg.goto('file:///home/claude/protocol-drill/index.html'); pg.wait_for_timeout(200)
    for attempt in range(40):
        pg.click('[data-act=start][data-id=moa]'); pg.wait_for_timeout(150)
        if pg.inner_text('#drug')=='ONDANSETRON': break
        pg.click('#restartBtn'); pg.wait_for_timeout(60); pg.click('#restartBtn'); pg.wait_for_timeout(120)
        if pg.inner_text('#drug')=='ONDANSETRON': break
        pg.click('[data-act=home]'); pg.wait_for_timeout(80)
    print('2) card:', pg.inner_text('#drug'))
    pg.click('#reveal'); pg.wait_for_timeout(150)
    A=pg.inner_text('.fb-ans'); print('   answer:', A)
    print('   top highlighted after Show answer (full retype):', pg.locator('.fb-ans .w.miss').count()>0)
    pg.fill('#ans',A.replace('and/or','and and/or')); pg.dispatch_event('#ans','input'); pg.wait_for_timeout(80)
    print('   still before Check:', pg.query_selector('.fb-still') is not None)
    pg.fill('#ans',A.replace(' to ',' to not ',1)); pg.dispatch_event('#ans','input'); pg.keyboard.press('Enter'); pg.wait_for_timeout(200)
    print('   extra not -> markers:', [e.inner_text() for e in pg.query_selector_all('.fb-ans .xtra')], '| still:', pg.inner_text('.fb-still') if pg.query_selector('.fb-still') else None)
    pg.screenshot(path='retype_extra.png',full_page=True)
    pg.fill('#ans',A.replace('and/or','and and/or')); pg.dispatch_event('#ans','input'); pg.wait_for_timeout(80)
    print('   fixed text, still line:', pg.query_selector('.fb-still') is not None)
    pg.keyboard.press("Enter"); pg.wait_for_timeout(700); print("   \"and and/or\" -> next card:", pg.inner_text("#drug"), "| missed:", pg.inner_text("#missTxt"))
    # slash "and": IV/IO style
    print('errors:',errs); b.close()
