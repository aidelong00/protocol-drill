import json, time
from playwright.sync_api import sync_playwright
ANS={'Alpha':'red blue green','Beta':'cat dog bird'}
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':390,'height':900},device_scale_factor=2); pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e: errs.append(str(e)))
    pg.goto('file:///home/claude/protocol-drill/index.html'); pg.wait_for_timeout(300)
    pg.evaluate("""()=>{ localStorage.clear(); const s={settings:{mode:'keys',auto:false,v:3,live:false,mnemView:'book'},progress:{},custom:[{id:'c1',title:'Tiny',src:'Alpha :: red blue green\\nBeta :: cat dog bird'}],mnem:{},mnemLast:{},updatedAt:Date.now()}; localStorage.setItem('pdrill:v1',JSON.stringify(s)); }""")
    pg.reload(); pg.wait_for_timeout(300)
    def P(): return pg.evaluate("JSON.parse(localStorage.getItem('pdrill:v1')).progress.c1||{}")
    def run(miss=False, quit_after_miss=False):
        pg.goto('file:///home/claude/protocol-drill/index.html'); pg.wait_for_timeout(200)
        pg.click('[data-act=start][data-id=c1]'); pg.wait_for_timeout(120)
        first=True
        for _ in range(8):
            if not pg.query_selector('#drug'): break
            d=pg.inner_text('#drug').title()
            if miss and first:
                pg.fill('#ans','wrong words here'); pg.keyboard.press('Enter'); pg.wait_for_timeout(120)
                if quit_after_miss: return None
                pg.fill('#ans',ANS[d]); pg.keyboard.press('Enter'); pg.wait_for_timeout(150)
                first=False
            else:
                pg.fill('#ans',ANS[d]); pg.keyboard.press('Enter'); pg.wait_for_timeout(120)
            if pg.query_selector('.fb-head') and pg.inner_text('.fb-head').startswith('CORRECT'): pg.click('#go'); pg.wait_for_timeout(150)
            if pg.query_selector('.h-res'): break
        bar=pg.query_selector('.pbar-wrap')
        return bar.inner_text().replace('\n',' | ') if bar else '(no bar)'
    def st(): q=P(); return f"learned={q.get('learned')} mastered={q.get('mastered')} streak={q.get('streak')} strikes={q.get('strikes')} lastPct={q.get('lastPct')}"
    print('1 failed run:', run(miss=True), '||', st())
    pg.screenshot(path='bar_fail.png')
    print('2 perfect   :', run(), '||', st()); pg.screenshot(path='bar_learned.png')
    for i in range(3): r=run()
    print('5 (+3 perf) :', r, '||', st())
    print('6 fail      :', run(miss=True), '||', st())
    print('7 fail quit :', run(miss=True, quit_after_miss=True), '||', st(), '(quit right after the miss)')
    print('8 perfect   :', run(), '||', st())
    for i in range(9): r=run()
    print('9..17 perf  :', r, '||', st()); pg.screenshot(path='bar_mastered.png')
    print('fail        :', run(miss=True), '||', st())
    print('perfect     :', run(), '||', st(), '(strike cleared)')
    print('fail        :', run(miss=True), '||', st())
    print('fail        :', run(miss=True), '||', st(), '(2 in a row: back to Learned)')
    print('fail        :', run(miss=True), '||', st())
    print('fail        :', run(miss=True), '||', st(), '(2 in a row: back to 0)')
    print('perfect     :', run(), '||', st())
    # countdown: last run 150h ago -> shows; 170h ago -> reset
    pg.evaluate("()=>{ const s=JSON.parse(localStorage.getItem('pdrill:v1')); s.progress.c1.lastAt=Date.now()-150*3600e3; localStorage.setItem('pdrill:v1',JSON.stringify(s)); }")
    pg.goto('file:///home/claude/protocol-drill/index.html'); pg.wait_for_timeout(1300)
    t=pg.query_selector('.reset-timer'); print('150h since last run -> countdown:', t.inner_text() if t else None); pg.screenshot(path='timer.png')
    pg.evaluate("()=>{ const s=JSON.parse(localStorage.getItem('pdrill:v1')); s.progress.c1.lastAt=Date.now()-140*3600e3; localStorage.setItem('pdrill:v1',JSON.stringify(s)); }")
    pg.goto('file:///home/claude/protocol-drill/index.html'); pg.wait_for_timeout(300)
    print('140h -> countdown shown:', bool(pg.query_selector('.reset-timer')))
    pg.evaluate("()=>{ const s=JSON.parse(localStorage.getItem('pdrill:v1')); s.progress.c1.lastAt=Date.now()-169*3600e3+2000; localStorage.setItem('pdrill:v1',JSON.stringify(s)); }")
    pg.goto('file:///home/claude/protocol-drill/index.html'); pg.wait_for_timeout(300)
    print('2s before reset:', pg.inner_text('.reset-timer') if pg.query_selector('.reset-timer') else None, '||', st()); pg.wait_for_timeout(3500)
    print('after it runs out:', bool(pg.query_selector('.reset-timer')), '||', st())
    # old save (streak 4, no learned field) loads as Learned 40%
    pg.evaluate("()=>{ const s=JSON.parse(localStorage.getItem('pdrill:v1')); s.progress.c1={runs:6,perfect:4,streak:4,lastMisses:0,lastAt:Date.now()-3600e3}; localStorage.setItem('pdrill:v1',JSON.stringify(s)); }")
    print('old save, then perfect:', run(), '||', st())
    print('errors:',errs); b.close()
