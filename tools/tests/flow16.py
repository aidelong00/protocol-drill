from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':390,'height':900}); errs=[]; pg.on('pageerror',lambda e: errs.append(str(e)))
    pg.goto('file:///home/claude/protocol-drill/index.html'); pg.wait_for_timeout(300); pg.evaluate("()=>localStorage.clear()"); pg.reload(); pg.wait_for_timeout(300)
    pg.click('[data-act=cards]'); pg.fill('#cardSearch','sodium bicarbonate'); pg.wait_for_timeout(80); pg.click('#cardList [data-act=start]'); pg.wait_for_timeout(150)
    pg.fill('#ans','Alkalizing agent, antidote'); pg.keyboard.press('Enter'); pg.wait_for_timeout(200); pg.click('#go'); pg.wait_for_timeout(200)
    print(pg.inner_text('#ask'),'|',pg.inner_text('#drug'))
    pg.fill('#ans','Increases blood and urinary pH by neutralizing hydrogen ions'); pg.dispatch_event('#ans','input'); pg.click('#nwBtn'); pg.wait_for_timeout(100)
    print('typed "...hydrogen ions" (no space) ->', pg.inner_text('#nwHint'))
    pg.fill('#ans','Increases blood and urinary pH by neutralizing hydrogen ions concentration.'); pg.keyboard.press('Enter'); pg.wait_for_timeout(200)
    print('submitted with "ions" ->', pg.inner_text('.fb-head'))
    print('errors:',errs); b.close()
