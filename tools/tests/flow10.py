import json
from playwright.sync_api import sync_playwright
C=json.load(open('/home/claude/packet/cards.json'))
MOA={c[0].split(' (')[0].upper():c[1] for c in C['moa']}
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
    pg = b.new_page(viewport={'width':390,'height':1000})
    errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file:///home/claude/protocol-drill/index.html'); pg.wait_for_timeout(300)
    pg.evaluate("""()=>{ const s=JSON.parse(localStorage.getItem('pdrill:v1')||'{}'); s.settings=Object.assign({mode:'keys',v:3},s.settings||{}); s.progress={moa:{runs:10,perfect:10,streak:10,lastMisses:0,mastered:true},class:{runs:1,perfect:1,streak:1,lastMisses:0},ind:{runs:8,perfect:8,streak:8,lastMisses:0}}; s.runs={}; s.updatedAt=Date.now(); localStorage.setItem('pdrill:v1',JSON.stringify(s)); Object.keys(localStorage).filter(k=>k.startsWith('pdrill:run:')).forEach(k=>localStorage.removeItem(k)); }""")
    pg.reload(); pg.wait_for_timeout(300)
    rows=pg.locator('.list').nth(1).locator('.row-meta').all_inner_texts()
    print('home:', [r.replace('\n',' ') for r in rows[:3]], '| gold icons:', pg.locator('.dc-icon.gold').count())
    # two misses on the mastered MOA deck
    pg.click('[data-act=start][data-id=moa]'); pg.wait_for_timeout(120)
    for i in range(2):
        pg.click('#reveal'); pg.wait_for_timeout(80)
        pg.fill('#ans', pg.inner_text('.fb-ans')); pg.keyboard.press('Enter'); pg.wait_for_timeout(450)
        st=pg.evaluate("JSON.parse(localStorage.getItem('pdrill:v1')).progress.moa")
        print(f'after miss {i+1}: mastered={st.get("mastered")} slips={st.get("slips")} streak={st.get("streak")}')
    # live checker on: stop keeps earlier sentences; correct answers count as missed
    pg.click('label.switch-row:has(#liveSwitch)'); pg.wait_for_timeout(60)
    for _ in range(40):
        if pg.inner_text('#drug')=='GLUCAGON': break
        d=pg.inner_text('#drug'); pg.fill('#ans', MOA[d]); pg.click('#go'); pg.wait_for_timeout(80)
        if pg.inner_text('.fb-head')=='CORRECT, ASSISTED' and _==0: print('assisted card ->', pg.inner_text('.fb-head'), '|', pg.inner_text('#missTxt'))
        pg.click('#go'); pg.wait_for_timeout(80)
    wrong=MOA['GLUCAGON'].replace('Causes breakdown of glycogen','Causes synthesis of glycogen')
    typed=''
    for w in wrong.split(' '):
        typed+=w+' '; pg.fill('#ans',typed); pg.dispatch_event('#ans','input'); pg.wait_for_timeout(15)
        if pg.query_selector('.fb-head') and pg.inner_text('.fb-head')=='STOPPED': break
    print('stop:', pg.inner_text('.fb-ans'))
    print('  textarea now:', repr(pg.input_value('#ans')), '| placeholder:', pg.get_attribute('#ans','placeholder'))
    print('  instructions:', pg.locator('.fb-small').first.inner_text())
    pg.fill('#ans', MOA['GLUCAGON']); pg.click('#go'); pg.wait_for_timeout(120)
    print('  finish ->', pg.inner_text('.fb-head'))
    print('errors:', errs); b.close()
