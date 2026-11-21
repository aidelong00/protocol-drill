const fs=require('fs');
const html=fs.readFileSync('/home/claude/protocol-drill/index.html','utf8');
const core=html.split('/*CORE-START*/')[1].split('/*CORE-END*/')[0];
const data=html.split('/*DATA-START*/')[1].split('/*DATA-END*/')[0];
const {grade,fixTargets,displayText,BUILTIN}=new Function(core+data+';return {grade,fixTargets,displayText,BUILTIN};')();
let fails=0; const ok=(c,m)=>{ if(!c){fails++;console.log('FAIL:',m);} };
const A=(deck,drug)=>BUILTIN.find(x=>x.id===deck).items.find(i=>i.d===drug).a;
function check(label,deck,drug,mutate,expMistakes,expTargets,mode='keys'){
  const a=A(deck,drug); const t=mutate(displayText(a).replace(/[•◦]/g,'').replace(/\s+/g,' '));
  const g=grade(a,t,mode); const tg=g.mistakes.length&&g.mistakes.length<3?fixTargets(a,g):[];
  const okM=g.mistakes.length===expMistakes, okT=expTargets==null||JSON.stringify(tg.map(x=>x.text))===JSON.stringify(expTargets);
  ok(!g.pass&&okM&&okT,`${label}: pass=${g.pass} mistakes=${g.mistakes.length} targets=${JSON.stringify(tg.map(x=>x.text))} missing=[${g.missing}]`);
  // each target must pass when typed back, and fail when left as originally typed
  tg.forEach(x=>ok(grade(x.text,x.text,mode).pass,`${label}: target retype passes`));
  return {g,tg};
}
check('albuterol beta 1 for beta 2','moa','Albuterol',t=>t.replace('beta-2','beta 1'),1,
  ['Selective beta-2 adrenergic agonist that causes relaxation of smooth muscles in the bronchial tree,']);
check('albuterol alpha 1 for beta 2','moa','Albuterol',t=>t.replace('Selective beta-2','Selective alpha 1'),1,
  ['Selective beta-2 adrenergic agonist that causes relaxation of smooth muscles in the bronchial tree,']);
check('albuterol two separate mistakes','moa','Albuterol',t=>t.replace('beta-2','beta 1').replace('vital capacity','tidal capacity'),2,
  ['Selective beta-2 adrenergic agonist that causes relaxation of smooth muscles in the bronchial tree,','facilitating mucous drainage and increasing vital capacity;']);
check('albuterol three mistakes -> full','moa','Albuterol',t=>t.replace('beta-2','beta 1').replace('vital capacity','tidal capacity').replace('shifts potassium','shifts sodium'),3,[]);
check('naloxone missing "in the brain"','moa','Naloxone',t=>t.replace(' in the brain',''),1,['Competitive inhibitor of opioid receptors in the brain.']);
check('calcium "or" for "and/or"','moa','Calcium Chloride',t=>t.replace('and/or','or'),1);
check('nitro wrong SBP sign','dose','Nitroglycerin',t=>t.replace('SBP ≥100','SBP >100'),1);
check('amiodarone wrong max','dose','Amiodarone',t=>t.replace('max 450 mg','max 400 mg'),1,['MR 150 mg q3-5 min (max 450 mg)']);
check('fentanyl wrong IN max','dose','Fentanyl',t=>t.replace('150 mcg','100 mcg'),1);
const r=check('midazolam CPAP dose wrong','dose','Midazolam',t=>t.replace('0.5-1 mg','1-2 mg'),1);
console.log('  e.g. midazolam target:',JSON.stringify(r.tg.map(x=>x.text)));
const r2=check('epi 1:10,000 hypothermia x2','dose','Epinephrine (1:10,000)',t=>t.replace('IV/IO x1','IV/IO x2'),1);
console.log('  e.g. epi target:',JSON.stringify(r2.tg.map(x=>x.text)));
// word-for-word mode too
check('exact: albuterol beta 1','moa','Albuterol',t=>t.replace('beta-2','beta 1'),1,null,'exact');
console.log(fails?`\n${fails} FAILURES`:'\nALL PASS');
