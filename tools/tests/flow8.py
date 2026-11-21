import json
from playwright.sync_api import sync_playwright
C=json.load(open('/home/claude/packet/cards.json'))
def get(deck,name): return [c for c in C[deck] if c[0]==name][0]
name='Tranexamic Acid'
answers=[get('class',name)[1],get('moa',name)[1],get('ind2',name)[1],get('contra',name)[1],get('dose',name)[1],'NA',get('adv',name)[1],get('notes',name)[1]]
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
    pg = b.new_page(viewport={'width':390,'height':900})
    errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file:///home/claude/protocol-drill/index.html'); pg.wait_for_timeout(300)
    pg.click('[data-act=cards]'); pg.fill('#cardSearch','tranex'); pg.click('#cardList [data-act=start]'); pg.wait_for_timeout(150)
    for i,a in enumerate(answers):
        sec=pg.inner_text('#ask')
        pg.fill('#ans',a)
        if pg.is_visible('#protRow'): pg.fill('#prot',' '.join(x[2:] for x in get('ind2',name)[2]))
        pg.click('#go'); pg.wait_for_timeout(150)
        print(f'{sec:34} -> {pg.inner_text(".fb-head")} | {pg.inner_text("#barTxt")}')
        pg.click('#go'); pg.wait_for_timeout(150)
    print('results:', pg.inner_text('.h-res'), '| stamp:', pg.is_visible('.stamp'))
    pg.click('[data-act=cards]'); pg.fill('#cardSearch','tranex'); pg.wait_for_timeout(80)
    print('list row:', pg.inner_text('#cardList .row-meta'))
    print('errors:', errs); b.close()
