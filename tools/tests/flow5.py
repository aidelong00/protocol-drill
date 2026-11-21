import json
from playwright.sync_api import sync_playwright
C=json.load(open('/home/claude/packet/cards.json'))
key=lambda n: n.split(' (')[0].upper() if not n.startswith('Epinephrine') else n.upper()
IND={c[0]:c for c in C['ind2']}; CON={c[0]:c for c in C['contra']}; PED={c[0]:c for c in C['peds']}
def full(name,sub): return name+(f' ({sub})' if sub else '')
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
    pg = b.new_page(viewport={'width':390,'height':1150}, device_scale_factor=2)
    errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file:///home/claude/protocol-drill/index.html'); pg.wait_for_timeout(400)
    print('home rows:', [t for t in pg.locator('.row-title').all_inner_texts()])
    pg.click('[data-act=start][data-id=ind]'); pg.wait_for_timeout(150)
    def cur():
        n=pg.inner_text('#drug').title(); s=pg.inner_text('#sub')
        for k in IND:
            if k.split(' (')[0].upper()==pg.inner_text('#drug') and (not s or k.endswith('('+s+')')): return IND[k]
    c=cur(); print('card 1:', c[0], '| protocols row visible:', pg.is_visible('#protRow'))
    pg.fill('#ans', c[1]); pg.keyboard.press('Enter'); pg.wait_for_timeout(100)
    print('  focus after Enter:', pg.evaluate('document.activeElement.id'))
    pg.fill('#prot', ' '.join(x[2:] for x in c[2])); pg.keyboard.press('Enter'); pg.wait_for_timeout(200)
    print('  head:', pg.inner_text('.fb-head'), '|', pg.inner_text('.fb-prot'))
    pg.keyboard.press('Enter'); pg.wait_for_timeout(200)
    c=cur(); print('card 2:', c[0])
    pg.fill('#ans', c[1]); pg.fill('#prot', '101'); pg.keyboard.press('Enter'); pg.wait_for_timeout(250)
    print('  head:', pg.inner_text('.fb-head'), '| ans readonly:', pg.evaluate('document.getElementById("ans").readOnly'), '| focus:', pg.evaluate('document.activeElement.id'))
    pg.screenshot(path='prot.png')
    pg.fill('#prot', ', '.join(c[2])); pg.keyboard.press('Enter'); pg.wait_for_timeout(500)
    c=cur(); print('card 3:', c[0])
    words=c[1].split(' '); bad=' '.join(words[:-1]+['zzzz'])
    pg.fill('#ans', bad); pg.fill('#prot', '999'); pg.keyboard.press('Enter'); pg.wait_for_timeout(250)
    print('  head:', pg.inner_text('.fb-head'), '|', pg.inner_text('.fix-label'))
    pg.fill('#ans', pg.inner_text('.fix-text')); pg.keyboard.press('Enter'); pg.wait_for_timeout(450)
    print('  step 2:', pg.inner_text('.fix-label'), '| focus:', pg.evaluate('document.activeElement.id'))
    pg.fill('#prot', ' '.join(c[2])); pg.keyboard.press('Enter'); pg.wait_for_timeout(500)
    print('  moved on to:', pg.inner_text('#drug'))
    # contraindications None card + peds NA card
    for deck,store_,want in [('contra',CON,'None'),('peds',PED,'NA')]:
        pg.click('[data-act=home]'); pg.click(f'[data-act=start][data-id={deck}]'); pg.wait_for_timeout(150)
        print(deck,'hint:', pg.inner_text('#cardHint'))
        for _ in range(40):
            d=pg.inner_text('#drug'); s=pg.inner_text('#sub')
            k=[k for k in store_ if k.split(' (')[0].upper()==d and (not s or k.endswith('('+s+')'))][0]; c=store_[k]
            if c[2]: break
            pg.fill('#ans', c[1]); pg.keyboard.press('Enter'); pg.wait_for_timeout(100); pg.keyboard.press('Enter'); pg.wait_for_timeout(120)
        pg.fill('#ans', want); pg.keyboard.press('Enter'); pg.wait_for_timeout(200)
        print(f'  {c[0]} typed "{want}":', pg.inner_text('.fb-head'))
    print('errors:', errs); b.close()
