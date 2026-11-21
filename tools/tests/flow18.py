from playwright.sync_api import sync_playwright
ANS={'Alpha':'red blue green','Beta':'cat dog bird'}
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':390,'height':900},device_scale_factor=2); pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e: errs.append(str(e)))
    pg.goto('file:///home/claude/protocol-drill/index.html'); pg.wait_for_timeout(300)
    pg.evaluate("""()=>{ localStorage.clear(); const s={settings:{mode:'keys',auto:false,v:3,live:false,mnemView:'book'},progress:{c1:{runs:9,perfect:9,streak:9,learned:true,strikes:0,lastPct:100,lastMisses:0,lastAt:Date.now()}},custom:[{id:'c1',title:'Tiny',src:'Alpha :: red blue green\\nBeta :: cat dog bird'}],mnem:{},mnemLast:{},updatedAt:Date.now()}; localStorage.setItem('pdrill:v1',JSON.stringify(s)); }""")
    def P(): return pg.evaluate("JSON.parse(localStorage.getItem('pdrill:v1')).progress.c1||{}")
    def st(): q=P(); return f"learned={q.get('learned')} mastered={q.get('mastered')} streak={q.get('streak')} strikes={q.get('strikes')}"
    def run(miss=False,shot=None):
        pg.goto('file:///home/claude/protocol-drill/index.html'); pg.wait_for_timeout(200)
        pg.click('[data-act=start][data-id=c1]'); pg.wait_for_timeout(120); first=True
        for _ in range(8):
            d=pg.inner_text('#drug').title()
            if miss and first: pg.fill('#ans','wrong words here'); pg.keyboard.press('Enter'); pg.wait_for_timeout(120); first=False
            pg.fill('#ans',ANS[d]); pg.keyboard.press('Enter'); pg.wait_for_timeout(120)
            if pg.query_selector('.fb-head') and pg.inner_text('.fb-head').startswith('CORRECT'): pg.click('#go'); pg.wait_for_timeout(150)
            if pg.query_selector('.h-res'): break
        if shot: pg.screenshot(path=shot,full_page=True)
        return pg.inner_text('.pbar-wrap').replace('\n',' | ')
    print('10th perfect:', run(shot='bar_mastered.png'), '||', st(), '| stamp:', pg.inner_text('.stamp'))
    print('fail        :', run(True,'bar_mstrike.png'), '||', st())
    print('perfect     :', run(), '||', st())
    print('fail        :', run(True), '||', st())
    print('fail        :', run(True), '||', st())
    pg.goto('file:///home/claude/protocol-drill/index.html'); pg.wait_for_timeout(200)
    print('home row:', pg.locator('.row:has([data-id=c1]) .row-meta').inner_text().replace('\n',' '))
    pg.evaluate("()=>{ const s=JSON.parse(localStorage.getItem('pdrill:v1')); s.progress.c1.lastAt=Date.now()-150*3600e3; s.progress['card:Adenosine']={runs:3,perfect:3,streak:3,learned:true,strikes:0,lastPct:100,lastMisses:0,lastAt:Date.now()-160*3600e3}; localStorage.setItem('pdrill:v1',JSON.stringify(s)); }")
    pg.goto('file:///home/claude/protocol-drill/index.html'); pg.wait_for_timeout(400)
    pg.locator('.row:has([data-id=c1])').screenshot(path='timer_row.png')
    pg.click('[data-act=cards]'); pg.wait_for_timeout(200); pg.locator('.row:has([data-id="card:Adenosine"])').screenshot(path='timer_card.png')
    print('drug card countdown:', pg.locator('.row:has([data-id="card:Adenosine"]) .reset-timer').inner_text().replace('\n',' '))
    print('errors:',errs); b.close()
