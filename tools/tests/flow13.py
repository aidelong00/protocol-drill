import json
from playwright.sync_api import sync_playwright
C=json.load(open('/home/claude/packet/cards.json'))
ADV={c[0].split(' (')[0].upper():c[2] for c in C['adv']}
def lines(pg): return [l.strip().lstrip('•').strip() for l in pg.inner_text('.fb-ans').split('\n') if l.strip()]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':390,'height':1000}); errs=[]; pg.on('pageerror',lambda e: errs.append(str(e)))
    pg.goto('file:///home/claude/protocol-drill/index.html'); pg.wait_for_timeout(300)
    pg.evaluate("()=>localStorage.clear()"); pg.reload(); pg.wait_for_timeout(300)
    pg.click('[data-act=start][data-id=adv]'); pg.wait_for_timeout(150)
    X=pg.inner_text('#drug'); items=ADV[X]
    pg.click('#mnBtn'); pg.click('[data-act=mnview][data-v=az]'); pg.wait_for_timeout(60)
    pg.click('#reveal'); pg.wait_for_timeout(120)
    shown=lines(pg); print(X,'A–Z picked, Show answer ->', shown)
    print('  is A–Z:', shown==sorted(items,key=str.lower))
    pg.fill('#ans', ', '.join(items)); pg.keyboard.press('Enter'); pg.wait_for_timeout(500)
    # second card: custom mnemonic, reversed book order
    Y=pg.inner_text('#drug'); yi=ADV[Y]
    pg.click('#mnBtn'); pg.click('[data-act=mnview][data-v=mine]'); pg.wait_for_timeout(50)
    mine=' '.join(x.split(' ')[0].split('/')[0]+'y' for x in reversed(yi)); pg.fill('#mnInput',mine); pg.click('[data-act=mnsave]'); pg.wait_for_timeout(60)
    pg.click('#reveal'); pg.wait_for_timeout(120); shownY=lines(pg)
    print(Y,'mine "'+mine+'" ->', shownY, '| reversed:', shownY==list(reversed(yi)))
    pg.fill('#ans', ', '.join(yi)); pg.keyboard.press('Enter'); pg.wait_for_timeout(500)
    # answer the next cards correctly until X and Y come back; show the answer without opening the mnemonic
    seen={}
    for _ in range(12):
        d=pg.inner_text('#drug')
        if d in (X,Y) and d not in seen:
            pg.click('#reveal'); pg.wait_for_timeout(120); s=lines(pg)
            seen[d]=s; print('came back:', d, '| mnemonic opened this time:', pg.is_visible('.mn-panel'), '->', s)
            pg.fill('#ans', ', '.join(ADV[d])); pg.keyboard.press('Enter'); pg.wait_for_timeout(500)
        else:
            pg.fill('#ans', ', '.join(ADV[d])); pg.keyboard.press('Enter'); pg.wait_for_timeout(120)
            if pg.query_selector('.fb-head') and pg.inner_text('.fb-head').startswith('CORRECT'): pg.click('#go'); pg.wait_for_timeout(100)
        if len(seen)==2: break
    if X in seen: print('X still A–Z:', seen[X]==sorted(items,key=str.lower))
    if Y in seen: print('Y still mine order:', seen[Y]==list(reversed(yi)))
    st=pg.evaluate("JSON.parse(localStorage.getItem('pdrill:v1')).mnemLast"); print('saved per drug:', st)
    # a drug never touched: book order unless a global A–Z preference applies
    print('errors:',errs); b.close()
