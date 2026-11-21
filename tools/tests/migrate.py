import json
from playwright.sync_api import sync_playwright
def ok(c,m): print(('PASS ' if c else 'FAIL ')+m)
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':390,'height':900}); errs=[]; pg.on('pageerror',lambda e: errs.append(str(e)))
    pg.goto('file:///home/claude/protocol-drill/index.html'); pg.wait_for_timeout(300)
    pg.click('[data-act=start][data-id=moa]'); pg.wait_for_timeout(150)
    r=pg.evaluate("JSON.parse(localStorage.getItem('pdrill:v1')).runs.moa")
    # make it look like an old-style run in its own key
    pg.evaluate("r=>{ const s=JSON.parse(localStorage.getItem('pdrill:v1')); delete s.runs; delete s.stamp; localStorage.setItem('pdrill:v1',JSON.stringify(s)); delete r.t; r.cleared=[r.ids[1],r.ids[2]]; localStorage.setItem('pdrill:run:moa',JSON.stringify(r)); }",r)
    pg.goto('file:///home/claude/protocol-drill/index.html'); pg.wait_for_timeout(300)
    st=pg.evaluate("JSON.parse(localStorage.getItem('pdrill:v1'))")
    ok('moa' in st['runs'] and st['runs']['moa']['t']==3,'old run moved into the store (t=3)')
    ok(pg.evaluate("localStorage.getItem('pdrill:run:moa')") is None,'old key removed')
    ok('2/26' in pg.inner_text('#app'),'home shows it in progress')
    print('errors',errs); b.close()
