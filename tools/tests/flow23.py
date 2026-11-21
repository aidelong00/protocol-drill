import json, datetime
from playwright.sync_api import sync_playwright
def dk(off): return (datetime.date.today()+datetime.timedelta(days=off)).isoformat()
def ok(c,m): print(('PASS ' if c else 'FAIL ')+m)
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':390,'height':900},device_scale_factor=2); pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e: errs.append(str(e)))
    pg.goto('file:///home/claude/protocol-drill/index.html'); pg.wait_for_timeout(300)
    def seed(days,today=None):
        st={'days':days,'today':today or {'d':'','k':[]}}
        pg.evaluate("s=>{ localStorage.clear(); localStorage.setItem('pdrill:v1',JSON.stringify({settings:{mode:'keys',auto:false,v:3,live:false,prot:true},progress:{},custom:[],mnem:{},mnemLast:{},streak:s,updatedAt:Date.now()})); }",st)
        pg.reload(); pg.wait_for_timeout(200)
    seed([])
    t=pg.inner_text('.dayrow'); print('fresh:',repr(t))
    ok('0 day streak' in t and datetime.date.today().strftime('%B') in t,'fresh: date and 0 day streak')
    seed([dk(-2),dk(-1)])
    ok('2 day streak' in pg.inner_text('.dayrow') and pg.locator('.day-streak.pending').count()==1,'yesterday+day before: 2, today pending (grey)')
    seed([dk(-3)])
    ok('0 day streak' in pg.inner_text('.dayrow'),'gap yesterday: streak 0')
    seed([dk(-2),dk(-1)])
    pg.screenshot(path='/home/claude/tests/streak_home.png')
    # answer cards correctly in the mechanisms deck
    pg.click('[data-act=start][data-id=moa]'); pg.wait_for_timeout(150)
    pg.screenshot(path='/home/claude/tests/back_btn.png',clip={'x':0,'y':0,'width':390,'height':120})
    MOA=json.loads(pg.evaluate("()=>JSON.stringify(null)") or 'null')
    html=open('/home/claude/protocol-drill/index.html').read()
    def answer_for(drug):
        import re
        m=re.search(r'\["'+re.escape(drug)+r'", "((?:[^"\\]|\\.)*)"\]',html.split('const MOA=')[1])
        return json.loads('"'+m.group(1)+'"')
    def st(): return pg.evaluate("JSON.parse(localStorage.getItem('pdrill:v1')).streak")
    done=[]
    # 1st: miss it (wrong answer) -> doesn't count
    pg.fill('#ans','totally wrong words here'); pg.keyboard.press('Enter'); pg.wait_for_timeout(200)
    ok(len(st()['today']['k'])==0,'a missed card does not count')
    pg.click('[data-act=home]'); pg.wait_for_timeout(100)
    pg.click('#restartBtn') if pg.query_selector('#restartBtn') else None
    pg.click('[data-act=start][data-id=moa]'); pg.wait_for_timeout(150)
    if pg.query_selector('#restartBtn'): pg.click('#restartBtn'); pg.wait_for_timeout(60); pg.click('#restartBtn'); pg.wait_for_timeout(150)
    for i in range(3):
        drug=pg.inner_text('#drug').title()
        names=[n for n in ['Acetaminophen (IV)','Activated Charcoal','Adenosine','Albuterol','Amiodarone','Aspirin','Atropine','Buprenorphine-Naloxone','Calcium Chloride','Dextrose','Diphenhydramine','Epinephrine','Fentanyl','Glucagon','Ipratropium','Ketamine','Ketorolac','Lidocaine','Magnesium Sulfate','Midazolam','Morphine','Naloxone','Nitroglycerin','Ondansetron','Sodium Bicarbonate','Tranexamic Acid','Oral Glucose','Levalbuterol','Olanzapine'] if n.upper()==pg.inner_text('#drug').upper()]
        a=answer_for(names[0]) if names else None
        if not a:
            print('  no answer for',pg.inner_text('#drug')); break
        pg.fill('#ans',a); pg.keyboard.press('Enter'); pg.wait_for_timeout(200)
        cnt=len(st()['today']['k'])
        print('  answered',names[0],'-> today count',cnt)
        pg.click('#go'); pg.wait_for_timeout(200)
    s2=st(); ok(len(s2['today']['k'])==3 and dk(0) in s2['days'],'3 first-try answers: today counted')
    pg.click('[data-act=home]'); pg.wait_for_timeout(150)
    ok('3 day streak' in pg.inner_text('.dayrow') and pg.locator('.day-streak.pending').count()==0,'home shows 3 day streak, fire lit')
    pg.screenshot(path='/home/claude/tests/streak_home2.png')
    print('errors:',errs); b.close()
