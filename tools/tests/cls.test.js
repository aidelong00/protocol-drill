const fs=require('fs');
const html=fs.readFileSync('/home/claude/protocol-drill/index.html','utf8');
const core=html.split('/*CORE-START*/')[1].split('/*CORE-END*/')[0];
const data=html.split('/*DATA-START*/')[1].split('/*DATA-END*/')[0];
const M=new Function(core+data+';return {gradeItem,liveCheck,fixTargets,displayText,BUILTIN};')();
let fails=0; const ok=(c,m)=>{ if(!c){fails++;console.log('FAIL:',m);} };
const live=(it,t,mode)=>{ let typed=''; for(const w of t.split(/\s+/)){ typed+=w+' '; const lc=M.liveCheck(it,typed,mode); if(lc.state!=='ok') return lc.state+': '+lc.msg; } return 'ok'; };
const C=M.BUILTIN.find(d=>d.id==='class').items; const I=n=>C.find(i=>i.d===n);
for(const mode of ['keys','exact']){
  for(const it of C){ if(it.d==='Buprenorphine-Naloxone') continue;
    const ph=it.a.split(/,\s*/); if(ph.length<2) continue;
    const rev=ph.slice().reverse().join(', ');
    const g=M.gradeItem(it,rev,mode); ok(g.pass,`${it.d} reversed "${rev}" (${mode}) ${JSON.stringify(g.missing)}`);
    ok(live(it,rev+' ',mode)==='ok',`${it.d} reversed live (${mode})`);
    // swap two words inside a multi-word phrase -> fails
    const k=ph.findIndex(x=>x.split(' ').length>=2&&!/\(/.test(x));
    if(k>=0){ const w=ph[k].split(' '); [w[0],w[1]]=[w[1],w[0]]; const bad=ph.slice(); bad[k]=w.join(' '); { const g=M.gradeItem(it,bad.join(', '),mode); ok(g.pass&&(it.d==='Fentanyl'||g.order&&g.order.length),`${it.d} flip inside "${bad[k]}" passes with order note (${mode}) ${JSON.stringify(g.missing)}`); } }
  }
  ok(M.gradeItem(I('Midazolam'),'Benzodiazepines, anxiolytics, antianxiety agent, anticonvulsant',mode).pass,`Midazolam fully reversed (${mode})`);
  ok(M.gradeItem(I('Calcium Chloride'),'Antidote and electrolyte',mode).pass,`"and" between two phrases (${mode})`);
  ok(!M.gradeItem(I('Calcium Chloride'),'Antidote',mode).pass,`missing a phrase fails (${mode})`);

  { const g=M.gradeItem(I('Aspirin'),'NSAID, agent antiplatelet',mode); ok(g.pass&&g.order.length,`Aspirin "agent antiplatelet" passes with note (${mode})`); }
  { const g=M.gradeItem(I('Epinephrine'),'Beta/alpha adrenergic agonist',mode); ok(g.pass&&g.order.length,`Epi beta/alpha passes with note (${mode})`); }
  ok(!M.gradeItem(I('Tranexamic Acid'),'Agent hemostatic, agent antifibrinolytic, inhibitor plasminogen',mode).pass,`three flips fails (${mode})`);
  ok(!M.gradeItem(I('Atropine'),'Anticholinergic, toxicity',mode).pass,`missing word still fails (${mode})`);
  ok(!M.gradeItem(I('Fentanyl'),'Synthetic analgesic, opioid opioid',mode).pass,`words scrambled across phrases fails (${mode})`);
  ok(M.gradeItem(I('Aspirin'),'NSAID, antiplatelet agent',mode).pass,`Aspirin NSAID first (${mode})`);
  const B=I('Buprenorphine-Naloxone');
  const good=['Buprenorphine: analgesic, opioid antagonist, opioid partial agonist. Naloxone: opioid reversal agent',
    'Naloxone: opioid reversal agent. Buprenorphine: opioid partial agonist, analgesic, opioid antagonist',
    'Buprenorphine: partial opioid agonist, opioid antagonist, analgesic; Naloxone: opioid reversal agent',
    '• Buprenorphine: opioid antagonist, analgesic, partial opioid agonist\n• Naloxone: opioid reversal agent'];
  good.forEach((t,i)=>{ const g=M.gradeItem(B,t,mode); ok(g.pass,`Bup good ${i} (${mode}) ${JSON.stringify(g.missing)}`); ok(live(B,t.replace(/[•◦]/g,' ')+' ',mode)==='ok',`Bup good ${i} live (${mode})`); });
  const bad=['Buprenorphine: analgesic, opioid partial agonist. Naloxone: opioid reversal agent, opioid antagonist',
    'Naloxone: analgesic, opioid antagonist, opioid partial agonist. Buprenorphine: opioid reversal agent'];
  { const g=M.gradeItem(B,'Buprenorphine: analgesic, opioid antagonist, opioid agonist partial. Naloxone: opioid reversal agent',mode); ok(g.pass&&g.order.length,`Bup flip passes with note (${mode})`); }
  { const g=M.gradeItem(B,'Buprenorphine: analgesic, opioid antagonist, partial opioid agonist. Naloxone: opioid reversal agent',mode); ok(g.pass&&!g.order.length,`Bup partial opioid agonist passes clean (${mode})`); }
  bad.forEach((t,i)=>{ const g=M.gradeItem(B,t,mode); ok(!g.pass,`Bup bad ${i} fails (${mode})`); if(!g.pass&&mode==='keys') console.log('  bad',i,'missing:',JSON.stringify(g.missing)); });
}
{ const G=I('Glucagon'); console.log('retype target for a missing phrase:', JSON.stringify(M.fixTargets(G.a, M.gradeItem(G,'Antidote','keys'), {any:1,phr:1}))); }
let reg=0; for(const d of M.BUILTIN) for(const it of d.items){ if(it.none||it.na||typeof it.a!=='string') continue; for(const mode of ['keys','exact']) if(!M.gradeItem(it,it.a,mode).pass){ reg++; console.log('regress',d.id,it.d,mode); } }
ok(reg===0,'every card correct in book order passes');
console.log(fails?`${fails} FAILED`:'ALL PASS');
