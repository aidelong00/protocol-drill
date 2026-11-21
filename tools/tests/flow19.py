from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':390,'height':900}); pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e: errs.append(str(e)))
    pg.goto('file:///home/claude/protocol-drill/index.html'); pg.wait_for_timeout(300)
    pg.evaluate("()=>{ localStorage.clear(); localStorage.setItem('pdrill:v1',JSON.stringify({settings:{mode:'keys',auto:false,v:3,live:false},progress:{},custom:[],mnem:{},mnemLast:{},updatedAt:Date.now()})); }")
    pg.goto('file:///home/claude/protocol-drill/index.html'); pg.wait_for_timeout(200)
    pg.click('[data-act=start][data-id=moa]'); pg.wait_for_timeout(150)
    drug=pg.inner_text('#drug')
    pg.type('#ans','Increases'); pg.click('#nwBtn'); pg.wait_for_timeout(120)
    hint1=pg.inner_text('#nwHint'); val1=pg.input_value('#ans')
    print('card:',drug,'| typed:',repr(val1),'|',hint1)
    pg.click('[data-act=home]'); pg.wait_for_timeout(150)
    pg.click('[data-act=start][data-id=moa]'); pg.wait_for_timeout(200)
    print('back  :',pg.inner_text('#drug'),'| typed:',repr(pg.input_value('#ans')),'|',pg.inner_text('#nwHint'),'| btn disabled:',pg.is_disabled('#nwBtn'))
    # caret at end: type more
    pg.keyboard.type(' X'); print('after typing:',repr(pg.input_value('#ans')))
    # reload page too
    pg.reload(); pg.wait_for_timeout(200); pg.click('[data-act=start][data-id=moa]'); pg.wait_for_timeout(200)
    print('reload:',repr(pg.input_value('#ans')))
    # miss -> retype full: text cleared, then go away/back keeps the retype text
    pg.fill('#ans','zzz qqq'); pg.keyboard.press('Enter'); pg.wait_for_timeout(150)
    print('after miss box:',repr(pg.input_value('#ans')), 'phase', pg.evaluate("JSON.parse(localStorage.getItem('pdrill:v1')).runs.moa.phase"))
    pg.type('#ans','partial retype'); pg.click('[data-act=home]'); pg.wait_for_timeout(100); pg.click('[data-act=start][data-id=moa]'); pg.wait_for_timeout(200)
    print('retype kept:',repr(pg.input_value('#ans')))
    # restart gives empty box
    pg.click('#restartBtn'); pg.wait_for_timeout(80)
    if pg.is_visible('#restartBtn'): pg.click('#restartBtn'); pg.wait_for_timeout(200)
    print('after restart:',repr(pg.input_value('#ans')), pg.inner_text('#barTxt'))
    print('errors:',errs); b.close()
