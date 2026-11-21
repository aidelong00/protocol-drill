const fs=require('fs');
const html=fs.readFileSync('/home/claude/protocol-drill/index.html','utf8');
const core=html.split('/*CORE-START*/')[1].split('/*CORE-END*/')[0];const data=html.split('/*DATA-START*/')[1].split('/*DATA-END*/')[0];
const M=new Function(core+data+';return {gradeItem,liveCheck,nextWord,displayText,BUILTIN};')();
let fails=0,n=0; const ok=(c,m)=>{ n++; if(!c){fails++; if(fails<20) console.log('FAIL:',m);} };
const live=(it,t,mode)=>{ let typed=''; for(const w of t.split(/\s+/)){ typed+=w+' '; const s=M.liveCheck(it,typed,mode).state; if(s!=='ok') return s+' at '+w; } return 'ok'; };
const moa=M.BUILTIN.find(d=>d.id==='moa');
let dropped=0;
for(const it of moa.items){ const T=M.displayText(it.a);
  const re=/(,?)\s\band\b(?!\/)\s/g; let m; const spots=[];
  while((m=re.exec(T))){ if(T.slice(m.index-3,m.index+1).includes('/')) continue; spots.push(m.index); }
  for(const at of spots){ const mm=/(,?)\s\band\b\s/.exec(T.slice(at)); const t=T.slice(0,at)+', '+T.slice(at+mm[0].length);
    for(const mode of ['keys','exact']){ dropped++; const g=M.gradeItem(it,t,mode); ok(g.pass,`${it.d}: "and" left out (${mode}) ${JSON.stringify(g.missing)} :: ${t.slice(Math.max(0,at-30),at+30)}`);
      const L=live(it,t,mode); ok(L==='ok',`${it.d}: live with "and" left out (${mode}) ${L}`); } }
  // all of them at once
  const all=T.replace(/,?\s\band\b(?!\/)\s/g,(x,c,off)=>T.slice(off-3,off+1).includes('/')?x:', ');
  ok(M.gradeItem(it,all,'keys').pass,`${it.d}: every joining "and" left out`);
  // typed with the "and" still passes, and next word after it keeps going
  ok(M.gradeItem(it,T,'exact').pass,`${it.d}: verbatim still passes`);
}
// and/or stays word for word
for(const name of ['Calcium Chloride','Ondansetron']){ const it=moa.items.find(i=>i.d===name); const T=M.displayText(it.a);
  for(const v of ['or','and']) ok(!M.gradeItem(it,T.replace('and/or',v),'keys').pass,`${name}: "${v}" for "and/or" still fails`); }
// the user's Glucagon example
const gl=moa.items.find(i=>i.d==='Glucagon'); const GT=M.displayText(gl.a); console.log(GT);
ok(M.gradeItem(gl,GT.replace(' and inhibits',', inhibits'),'keys').pass,'Glucagon: "glucose, inhibits" passes');
// outside mechanisms, a left-out "and" still counts
const ind=M.BUILTIN.find(d=>d.id==='ind').items.find(i=>/\band\b/.test(M.displayText(i.a))&&!/and\//.test(M.displayText(i.a)));
const IT=M.displayText(ind.a); ok(!M.gradeItem(ind,IT.replace(/\sand\s/,', '),'keys').pass,`${ind.d} indications: left-out "and" still fails`);
// next word: after "glucose " it shows the next word, and after "glucose and " too
const pre=GT.slice(0,GT.indexOf(' and inhibits'));
console.log('next after "glucose":',M.nextWord(gl,pre+' ','keys'),'| after "glucose and":',M.nextWord(gl,pre+' and ','keys'));
ok(M.nextWord(gl,pre+' and ','keys')==='inhibits','next word after "glucose and" is "inhibits"');
console.log(`(${dropped} left-out "and" cases)`, fails?fails+' FAILURES':'ALL PASS ('+n+')'); process.exit(fails?1:0);
