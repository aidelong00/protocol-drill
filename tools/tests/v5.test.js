const fs=require('fs');
const html=fs.readFileSync('/home/claude/protocol-drill/index.html','utf8');
const core=html.split('/*CORE-START*/')[1].split('/*CORE-END*/')[0];
const data=html.split('/*DATA-START*/')[1].split('/*DATA-END*/')[0];
const M=new Function(core+data+';return {gradeItem,liveCheck,nextWord,displayText,BUILTIN};')();
const I=(d,n)=>M.BUILTIN.find(x=>x.id===d).items.find(i=>i.d===n);
let fails=0; const ok=(c,m)=>{ if(!c){fails++;console.log('FAIL:',m);} };
const G=(it,t,mode)=>M.gradeItem(it,t,mode);
const live=(it,t,mode)=>{ let typed='',worst='ok'; for(const w of t.split(/\s+/)){ typed+=w+' '; const s=M.liveCheck(it,typed,mode).state; if(s!=='ok'){ worst=s; break; } } return worst; };
const cls=I('class','Aspirin'), moa=I('moa','Aspirin');
for(const mode of ['keys','exact']){
  // NSAID: one, the other, or both
  for(const t of ['Antiplatelet agent, NSAID','Antiplatelet agent, non-steroidal anti-inflammatory drug','Antiplatelet agent, non-steroidal anti-inflammatory drug (NSAID)','Antiplatelet agent, nonsteroidal antiinflammatory drug','Antiplatelet agent, non steroidal anti inflammatory drug (NSAID)','Antiplatelet agent, non-steriodal anti-inflamatory drug']){
    ok(G(cls,t,mode).pass,`class "${t}" (${mode})`); ok(live(cls,t+' ',mode)==='ok',`class live "${t}" (${mode})`);
  }
  ok(!G(cls,'Antiplatelet agent, steroidal anti-inflammatory drug (NSAID)',mode).pass,`"steroidal" + (NSAID) fails (${mode})`);
  ok(!G(cls,'Antiplatelet agent',mode).pass,`missing NSAID fails (${mode})`);
  // aspirin mechanism: swap + effects
  const base='Inhibits platelet aggregation and inhibits synthesis of prostaglandin by cyclooxygenase; has ';
  for(const end of ['antipyretic and analgesic activity.','analgesic and antipyretic activity.','analgesic and antipyretic effects.','antipyretic and analgesic effect.','analgesic and antipyretic effects']){
    const g=G(moa,base+end,mode); ok(g.pass&&!(g.order&&g.order.length),`aspirin moa "${end}" passes, no order flag (${mode}) ${JSON.stringify(g.missing)} ${JSON.stringify(g.order)}`);
    ok(live(moa,base+end+' ',mode)==='ok',`aspirin live "${end}" (${mode})`);
  }
  ok(!G(moa,base+'analgesic or antipyretic activity.',mode).pass,`"or" still fails (${mode})`);
  ok(!G(moa,base+'analgesic activity.',mode).pass,`dropping antipyretic still fails (${mode})`);
  // effects for activity on other mechanisms, both directions
  const alb=I('moa','Albuterol'); ok(G(alb,M.displayText(alb.a).replace('beta-1 activity','beta-1 effects'),mode).pass,`albuterol effects (${mode})`);
  const atr=I('moa','Atropine'); ok(G(atr,M.displayText(atr.a).replace('muscarinic effects','muscarinic activity'),mode).pass,`atropine activity (${mode})`);
  ok(!G(atr,M.displayText(atr.a).replace('muscarinic effects','muscarinic'),mode).pass,`atropine dropping "effects" fails (${mode})`);
  // not outside mechanisms
  const glu=I('ind','Glucagon'); ok(!G(glu,M.displayText(glu.a).replace('cardiac effects','cardiac activity'),mode).pass,`indications keep "effects" exact (${mode})`);
}
// next word stays sensible with effects
console.log('next word after "...has analgesic and antipyretic":', M.nextWord(moa,'Inhibits platelet aggregation and inhibits synthesis of prostaglandin by cyclooxygenase; has analgesic and antipyretic ','keys'));
// every card typed correctly still passes, no live false alarms
let reg=0, alarms=0;
for(const d of M.BUILTIN) for(const it of d.items){ if(it.none||it.na||typeof it.a!=='string') continue;
  for(const mode of ['keys','exact']){ if(!G(it,it.a,mode).pass){ reg++; console.log('regress',d.id,it.d,mode); } if(live(it,M.displayText(it.a).replace(/[•◦]/g,' ')+' ',mode)!=='ok'){ alarms++; console.log('alarm',d.id,it.d,mode); } } }
ok(reg===0&&alarms===0,`regressions ${reg}, live alarms ${alarms}`);
console.log(fails?`${fails} FAILED`:'ALL PASS');
