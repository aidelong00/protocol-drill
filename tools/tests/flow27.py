from playwright.sync_api import sync_playwright
def ok(c,m): print(('PASS ' if c else 'FAIL ')+m)
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':390,'height':1000},device_scale_factor=2); errs=[]; pg.on('pageerror',lambda e: errs.append(str(e)+' '+str(e.stack)[:300]))
    pg.goto('file:///home/claude/protocol-drill/index.html'); pg.wait_for_timeout(300)
    pg.evaluate("()=>{ localStorage.clear(); localStorage.setItem('pdrill:v1',JSON.stringify({settings:{mode:'keys',auto:false,v:3,live:true,prot:true},progress:{},custom:[],mnem:{},mnemLast:{},updatedAt:Date.now()})); }")
    pg.reload(); pg.wait_for_timeout(200)
    pg.click('[data-act=cards]'); pg.fill('#cardSearch','bupren'); pg.wait_for_timeout(80); pg.click('#cardList [data-act=start]'); pg.wait_for_timeout(200)
    print('section:',pg.inner_text('#drug'))
    ok(pg.locator('#drugBoxes .db-box').count()==2 and not pg.is_visible('#ans'),'two boxes, main box hidden')
    ok([e.inner_text() for e in pg.query_selector_all('.db-name')]==['Buprenorphine:','Naloxone:'],'labels in front')
    ok(pg.evaluate("document.activeElement.dataset.i")=='0','first box focused')
    pg.keyboard.type('analgesic, opioid antagonist, opioid partial agonist'); pg.keyboard.press('Enter'); pg.wait_for_timeout(100)
    ok(pg.evaluate("document.activeElement.dataset.i")=='1','Enter moves to the Naloxone box')
    pg.keyboard.type('opioid reversal agent')
    pg.screenshot(path='/home/claude/tests/drugboxes.png',full_page=True)
    print('composed:',repr(pg.input_value('#ans')))
    pg.keyboard.press('Enter'); pg.wait_for_timeout(300)
    fb=pg.inner_text('.fb-head') if pg.query_selector('.fb-head') else ''
    print('after check:',fb)
    ok(pg.query_selector('.fb.miss') is None and pg.query_selector('.fb') is not None,'both boxes right: correct')
    # go on to the next section and come back to the class section later? test a wrong answer on a fresh deck
    pg.click('[data-act=cards]'); pg.wait_for_timeout(100); pg.fill('#cardSearch','bupren'); pg.wait_for_timeout(80); pg.click('#cardList [data-act=start]'); pg.wait_for_timeout(200)
    if pg.query_selector('#restartBtn'): pg.click('#restartBtn'); pg.wait_for_timeout(60); pg.click('#restartBtn'); pg.wait_for_timeout(200)
    print('after restart:', pg.inner_text('#ask') if pg.query_selector('#ask') else pg.inner_text('#app')[:200])
    bx=pg.query_selector_all('#drugBoxes .db-box')
    bx[0].fill('analgesic, opioid antagonist, opioid partial agonist'); bx[0].dispatch_event('input')
    bx[1].fill('opioid blocker'); bx[1].dispatch_event('input'); pg.click('#go'); pg.wait_for_timeout(300)
    print('wrong ->',pg.inner_text('.fb-head'),'| fix box:',pg.inner_text('.fix .fix-text') if pg.query_selector('.fix .fix-text') else '')
    ok(pg.locator('#drugBoxes .db-box').count()==2 and all(e.input_value()=='' for e in pg.query_selector_all('#drugBoxes .db-box')),'boxes cleared for the retype')
    part=pg.inner_text('.fix .fix-text').replace('Naloxone:','').strip()
    bx=pg.query_selector_all('#drugBoxes .db-box'); bx[1].fill(part); bx[1].dispatch_event('input')
    # leave and come back: text stays in the right box
    pg.click('[data-act=cards]'); pg.wait_for_timeout(100); pg.fill('#cardSearch','bupren'); pg.wait_for_timeout(80); pg.click('#cardList [data-act=start]'); pg.wait_for_timeout(250)
    vals=[e.input_value() for e in pg.query_selector_all('#drugBoxes .db-box')]; print('after leaving and coming back:',vals)
    ok(vals[1]==part and vals[0]=='','typed text comes back in the Naloxone box')
    pg.click('#go'); pg.wait_for_timeout(500)
    ok(pg.query_selector('.fb.miss') is None,'retyped part passes')
    # Albuterol / Levalbuterol mechanism sections show which drug
    pg.click('[data-act=cards]'); pg.wait_for_timeout(100); pg.fill('#cardSearch','albuterol'); pg.wait_for_timeout(80); pg.click('#cardList [data-act=start]'); pg.wait_for_timeout(200)
    seen=[]
    for i in range(4):
        sec=pg.inner_text('#ask'); lab=pg.inner_text('#drugLbl') if pg.is_visible('#drugLbl') else ''
        seen.append((sec,lab)); pg.click('#reveal'); pg.wait_for_timeout(100); a=pg.inner_text('.fb-ans'); pg.fill('#ans',a)
        if pg.is_visible('#prot'): pg.fill('#prot',pg.inner_text('.fb-prot').replace('Protocols:','') if pg.query_selector('.fb-prot') else '')
        pg.keyboard.press('Enter'); pg.wait_for_timeout(500)
        for _ in range(3):
            if pg.query_selector('.fb.miss'): pg.fill('#ans',a); pg.keyboard.press('Enter'); pg.wait_for_timeout(500)
            elif pg.query_selector('#go') and pg.inner_text('#go')!='Check': pg.click('#go'); pg.wait_for_timeout(200)
            else: break
        if pg.inner_text('#ask')==sec: pg.fill('#ans',a); pg.keyboard.press('Enter'); pg.wait_for_timeout(400); pg.click('#go') if pg.inner_text('#go')!='Check' else None; pg.wait_for_timeout(200)
    print('albuterol sections:',seen)
    ok(any(l=='Albuterol:' for s,l in seen) or any(l=='Levalbuterol:' for s,l in seen),'mechanism sections name their drug')
    print('errors:',errs); b.close()
