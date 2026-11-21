import json
from playwright.sync_api import sync_playwright
C=json.load(open('/home/claude/packet/cards.json'))
def get(deck,name): return [c for c in C[deck] if c[0]==name][0]
name='Tranexamic Acid'
answers=[get('class',name)[1],get('moa',name)[1],get('ind2',name)[1],get('contra',name)[1],get('dose',name)[1],'NA',get('adv',name)[1],get('notes',name)[1]]
def chips(pg):
    pg.click('[data-act=cards]'); pg.fill('#cardSearch','tranex'); pg.wait_for_timeout(60)
    return pg.inner_text('#cardList .row-meta').replace('\n',' ')
def runcard(pg, mistake=False):
    pg.click('#cardList [data-act=start]'); pg.wait_for_timeout(120)
    for i,a in enumerate(answers):
        if mistake and i==1:
            pg.fill('#ans','wrong answer'); pg.click('#go'); pg.wait_for_timeout(100)
            return
        pg.fill('#ans',a)
        if pg.is_visible('#protRow'): pg.fill('#prot','133 139 166')
        pg.click('#go'); pg.wait_for_timeout(100); pg.click('#go'); pg.wait_for_timeout(100)
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
    pg = b.new_page(viewport={'width':390,'height':900})
    errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file:///home/claude/protocol-drill/index.html'); pg.wait_for_timeout(300)
    print('start:', chips(pg))
    runcard(pg)
    print('perfect run 1 ->', pg.inner_text('.stamp'), '|', pg.inner_text('.pbar-wrap').replace(chr(10),' | '))
    print('  list:', chips(pg))
    pg.click('[data-act=home]'); runcard(pg, mistake=True) if False else None
    chips(pg); runcard(pg, mistake=True)
    pg.click('[data-act=cards]'); pg.fill('#cardSearch','tranex'); pg.wait_for_timeout(60)
    print('after one mistake mid-run, list:', pg.inner_text('#cardList .row-meta').replace('\n',' '))
    # seed a 9-run streak, then a perfect run should master it
    pg.evaluate("""()=>{ const s=JSON.parse(localStorage.getItem('pdrill:v1')); s.progress['card:Tranexamic Acid']={runs:9,perfect:9,streak:9,lastMisses:0}; if(s.runs) delete s.runs['card:Tranexamic Acid']; localStorage.setItem('pdrill:v1',JSON.stringify(s)); localStorage.removeItem('pdrill:run:card:Tranexamic Acid'); }""")
    pg.reload(); pg.wait_for_timeout(300)
    print('seeded 9:', chips(pg))
    runcard(pg)
    print('10th perfect run ->', pg.inner_text('.stamp'), '|', pg.inner_text('.pbar-wrap').replace(chr(10),' | '))
    print('  list:', chips(pg), '| gold icon:', pg.locator('#cardList .dc-icon.gold').count())
    # mnemonic counts as a miss
    pg.click('[data-act=home]'); pg.click('[data-act=start][data-id=adv]'); pg.wait_for_timeout(120)
    print('mnemonic button:', pg.inner_text('#mnBtn'))
    d=pg.inner_text('#drug'); s=pg.inner_text('#sub')
    k=[c for c in C['adv'] if c[0].upper()==d][0]
    pg.click('#mnBtn'); pg.fill('#ans',k[1]); pg.click('#go'); pg.wait_for_timeout(120)
    print('  correct after mnemonic ->', pg.inner_text('.fb-head'), '|', pg.inner_text('#missTxt'), '|', pg.locator('.fb-small').first.inner_text())
    print('live warn text:', pg.evaluate("document.getElementById('liveWarn').textContent"))
    print('errors:', errs); b.close()
