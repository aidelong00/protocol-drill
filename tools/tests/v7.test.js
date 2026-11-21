const fs=require('fs');
const html=fs.readFileSync('/home/claude/protocol-drill/index.html','utf8');
const core=html.split('/*CORE-START*/')[1].split('/*CORE-END*/')[0];
const data=html.split('/*DATA-START*/')[1].split('/*DATA-END*/')[0];
const M=new Function(core+data+';return {gradeItem,nextWord,liveCheck,displayText,BUILTIN};')();
let fails=0; const ok=(c,m)=>{ if(!c){fails++;console.log('FAIL:',m);} };
const I=(d,n)=>M.BUILTIN.find(x=>x.id===d).items.find(i=>i.d===n);
const live=(it,t,mode)=>{ let typed=''; for(const w of t.split(/\s+/)){ typed+=w+' '; const lc=M.liveCheck(it,typed,mode); if(lc.state!=='ok') return lc.state; } return 'ok'; };
for(const [d,n] of [['notes','Calcium Chloride'],['notes','Sodium Bicarbonate']]){
  const it=I(d,n), T=M.displayText(it.a);
  for(const mode of ['keys','exact']){
    const t=T.replace(/sodium bicarbonate/gi,'sodium bicarb'); ok(M.gradeItem(it,t,mode).pass,`${n} notes with "sodium bicarb" (${mode})`); ok(live(it,t.replace(/[•◦]/g,' ')+' ',mode)==='ok',`${n} live (${mode})`);
    ok(!M.gradeItem(it,T.replace(/sodium bicarbonate/gi,'sodium'),mode).pass,`${n} "sodium" alone fails (${mode})`);
  }
}
// next word: a finished word without the space gives the same answer as with the space
let checked=0, diff=0;
for(const d of M.BUILTIN) for(const it of d.items){ if(!it.nw||it.none||typeof it.a!=='string') continue;
  const words=M.displayText(it.a).replace(/[•◦]/g,' ').split(/\s+/).filter(Boolean);
  for(let i=1;i<words.length;i++){ const pre=words.slice(0,i).join(' '); const a=M.nextWord(it,pre,'keys'), b=M.nextWord(it,pre+' ','keys'); checked++; if(a!==b){ diff++; if(diff<=8) console.log('diff',d.id,it.d,JSON.stringify(pre.slice(-30)),'no space:',a,'| space:',b); } }
}
console.log(`next word checked at ${checked} spots, differences: ${diff}`);
ok(diff===0,'next word same with or without the space');
// plural tolerance doesn't hide real differences
const dose=I('dose','Aspirin'); ok(!M.gradeItem(dose,'Aspirin 324 mcg chewable PO','keys').pass,'mcg for mg still fails');
let reg=0, alarms=0;
for(const d of M.BUILTIN) for(const it of d.items){ if(it.none||it.na||typeof it.a!=='string') continue;
  for(const mode of ['keys','exact']){ if(!M.gradeItem(it,it.a,mode).pass){ reg++; console.log('regress',d.id,it.d,mode); } if(live(it,M.displayText(it.a).replace(/[•◦]/g,' ')+' ',mode)!=='ok'){ alarms++; console.log('alarm',d.id,it.d,mode); } } }
ok(reg===0&&alarms===0,`regressions ${reg}, live alarms ${alarms}`);
console.log(fails?`${fails} FAILED`:'ALL PASS');
