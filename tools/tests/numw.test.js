const fs=require('fs');
const html=fs.readFileSync('/home/claude/protocol-drill/index.html','utf8');
const core=html.split('/*CORE-START*/')[1].split('/*CORE-END*/')[0];const data=html.split('/*DATA-START*/')[1].split('/*DATA-END*/')[0];
const M=new Function(core+data+';return {gradeItem,liveCheck,nextWord,displayText,BUILTIN};')();
let fails=0,n=0; const ok=(c,m)=>{ n++; if(!c){fails++;console.log('FAIL:',m);} };
const card=(deck,name)=>M.BUILTIN.find(d=>d.id===deck).items.find(i=>i.d.startsWith(name));
const live=(it,t,mode)=>{ let typed=''; for(const w of t.split(/\s+/)){ typed+=w+' '; const s=M.liveCheck(it,typed,mode).state; if(s!=='ok') return s+' at '+w; } return 'ok'; };
const cases=[
  ['moa','Albuterol','beta-2','beta two'],['moa','Albuterol','beta-1','beta one'],['moa','Albuterol','beta-2','beta-two'],['moa','Albuterol','beta-1','beta 1'],
  ['notes','Calcium Chloride','three times','3 times'],
  ['dose','Naloxone','one nostril','1 nostril'],
  ['contra','Adenosine','Second- or third-degree','2nd- or 3rd-degree'],['contra','Adenosine','Second- or third-degree','Second or third degree'],['contra','Adenosine','Second- or third-degree','2nd or 3rd degree'],
  ['notes','Adenosine','6-second','6-second'],
];
for(const [d,name,from,to] of cases){ const it=card(d,name); if(!it){ ok(false,`no card ${d}/${name}`); continue; } const T=M.displayText(it.a);
  if(!T.includes(from)){ ok(false,`${d}/${name}: "${from}" not in answer`); continue; }
  const t=T.split(from).join(to);
  for(const mode of ['keys','exact']){ const g=M.gradeItem(it,t,mode); ok(g.pass,`${d}/${name}: "${to}" for "${from}" (${mode}) ${JSON.stringify(g.missing)}`);
    if(!it.any){ const L=live(it,t.replace(/[•◦]/g,' '),mode); ok(L==='ok',`${d}/${name}: live "${to}" (${mode}) ${L}`); } }
}
// a wrong number still fails, written out or not
const alb=card('moa','Albuterol'), AT=M.displayText(alb.a);
ok(!M.gradeItem(alb,AT.replace('beta-2','beta three'),'keys').pass,'"beta three" for beta-2 fails');
ok(!M.gradeItem(alb,AT.replace('beta-1','beta two'),'keys').pass,'"beta two" for beta-1 fails');
const cc=card('notes','Calcium Chloride'); ok(!M.gradeItem(cc,M.displayText(cc.a).replace('three times','two times'),'keys').pass,'"two times" for three times fails');
// next word after a written-out number keeps going
const pre=AT.slice(0,AT.indexOf('beta-2'))+'beta two ';
ok(M.nextWord(alb,pre,'keys')===M.nextWord(alb,AT.slice(0,AT.indexOf('beta-2'))+'beta-2 ','keys'),'next word after "beta two" = after "beta-2"');
console.log(fails?fails+' FAILURES':'ALL PASS ('+n+')'); process.exit(fails?1:0);
