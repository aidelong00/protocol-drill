import json, re
from playwright.sync_api import sync_playwright
def ok(c,m): print(('PASS ' if c else 'FAIL ')+m)
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':390,'height':1000},device_scale_factor=2); errs=[]; pg.on('pageerror',lambda e: errs.append(str(e)))
    pg.goto('file:///home/claude/protocol-drill/index.html'); pg.wait_for_timeout(200)
    pg.evaluate("()=>{ localStorage.clear(); localStorage.setItem('pdrill:v1',JSON.stringify({settings:{mode:'keys',auto:false,v:3,live:false,prot:true},progress:{},custom:[],mnem:{},mnemLast:{},updatedAt:Date.now()})); }")
    pg.reload(); pg.wait_for_timeout(200)
    st=lambda: pg.evaluate("JSON.parse(localStorage.getItem('pdrill:v1'))")
    # a full run of the Amiodarone card, one section cleared
    pg.click('[data-act=cards]'); pg.fill('#cardSearch','amiodarone'); pg.wait_for_timeout(80); pg.click('#cardList [data-act=start]'); pg.wait_for_timeout(200)
    pg.click('#reveal'); pg.wait_for_timeout(100); a=pg.inner_text('.fb-ans'); pg.fill('#ans',a); pg.keyboard.press('Enter'); pg.wait_for_timeout(500)
    for _ in range(3):
        if pg.query_selector('.fb.miss') is None and pg.query_selector('#go') and pg.inner_text('#go')!='Check': pg.click('#go'); pg.wait_for_timeout(200)
        elif pg.query_selector('#go') and pg.evaluate("JSON.parse(localStorage.getItem('pdrill:v1')).runs['card:Amiodarone'].pres.redo"): pg.fill('#ans',a); pg.keyboard.press('Enter'); pg.wait_for_timeout(500)
        else: break
    before=st()['runs']['card:Amiodarone']; print('full run before:',len(before['cleared']),'cleared, at',pg.inner_text('#ask'))
    # Review -> Drill just the Notes
    pg.click('[data-act=cards]'); pg.wait_for_timeout(100); pg.fill('#cardSearch','amiodarone'); pg.wait_for_timeout(80)
    pg.click('#cardList [data-act=study]'); pg.wait_for_timeout(200)
    n=pg.locator('[data-act=drillone]').count(); ok(n==8,f'Review shows a Drill button on each of the 8 sections ({n})')
    pg.screenshot(path='/home/claude/tests/review_drill.png',clip={'x':0,'y':0,'width':390,'height':700})
    notes=[e for e in pg.query_selector_all('.study li') if e.query_selector('.q').inner_text().lower().startswith('notes')][0]
    notes.query_selector('[data-act=drillone]').click(); pg.wait_for_timeout(200)
    print('drilling:',pg.inner_text('#ask'),'| back button:',pg.inner_text('.back'))
    ok('NOTES' in pg.inner_text('#drug').upper() and 'JUST THIS SECTION' in pg.inner_text('#ask').upper() and 'Review' in pg.inner_text('.back') and not pg.is_visible('#skipBtn'),'drill shows just the Notes, back goes to Review, no Skip')
    pg.click('#reveal'); pg.wait_for_timeout(100); a=pg.inner_text('.fb-ans'); pg.fill('#ans',a); pg.keyboard.press('Enter'); pg.wait_for_timeout(500)
    for _ in range(4):
        if pg.query_selector('.h-res'): break
        if pg.query_selector('#go') and pg.inner_text('#go')!='Check': pg.click('#go'); pg.wait_for_timeout(300)
        else: pg.fill('#ans',a); pg.keyboard.press('Enter'); pg.wait_for_timeout(500)
    print('result:',pg.inner_text('.h-res') if pg.query_selector('.h-res') else '?', '|', pg.inner_text('.lede')[:120] if pg.query_selector('.lede') else '')
    ok(pg.query_selector('[data-act=drillone]') is not None,'result offers Drill it again / Back to review')
    after=st()['runs']['card:Amiodarone']
    ok(after['cleared']==before['cleared'] and after['ids']==before['ids'],'the full Amiodarone run in progress is untouched')
    ok(not st()['progress'].get('card:Amiodarone',{}).get('learned'),'drilling one section does not count toward progress')
    pg.click('[data-act=review]'); pg.wait_for_timeout(150); ok(pg.query_selector('.study') is not None,'Back to review works')
    # a regular deck: drill one card from the Notes deck review
    pg.click('.back'); pg.wait_for_timeout(150)
    if pg.query_selector('[data-act=study][data-id=notes]'): pg.click('[data-act=study][data-id=notes]')
    else: pg.click('[data-act=home]'); pg.wait_for_timeout(100); pg.click('[data-act=study][data-id=notes]')
    pg.wait_for_timeout(150); pg.query_selector_all('[data-act=drillone]')[2].click(); pg.wait_for_timeout(200)
    ok('NOTES' in pg.inner_text('#ask').upper() or pg.query_selector('#drug') is not None,'Notes deck: drill one drug\'s notes')
    print('errors:',errs); b.close()
