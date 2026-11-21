import subprocess, time
from playwright.sync_api import sync_playwright
srv=subprocess.Popen(['python3','-m','http.server','8765','--bind','127.0.0.1'],cwd='/home/claude/web/site',stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(0.8)
FAKE=open('/home/claude/tests/fakefb.js').read()
try:
  with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    for scheme in ['light','dark']:
      ctx=b.new_context(viewport={'width':390,'height':760},device_scale_factor=2,color_scheme=scheme)
      ctx.route('**/config.js',lambda r: r.fulfill(body="window.FIREBASE_CONFIG={apiKey:'x'};",content_type='application/javascript'))
      ctx.route('**/firebase.js',lambda r: r.fulfill(body=FAKE,content_type='application/javascript'))
      pg=ctx.new_page(); pg.goto('http://127.0.0.1:8765/'); pg.wait_for_timeout(300)
      pg.screenshot(path=f'/home/claude/tests/web_out_{scheme}.png')
      if scheme=='light':
        pg.evaluate("window.__nextUser={uid:'A',email:'student.medic@gmail.com'}"); pg.click('[data-act=signin]'); pg.wait_for_timeout(300)
        pg.screenshot(path='/home/claude/tests/web_in.png')
      ctx.close()
    b.close()
finally: srv.terminate()
