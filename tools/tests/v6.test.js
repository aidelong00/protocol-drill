const fs=require('fs');
const html=fs.readFileSync('/home/claude/protocol-drill/index.html','utf8');
const core=html.split('/*CORE-START*/')[1].split('/*CORE-END*/')[0];
const data=html.split('/*DATA-START*/')[1].split('/*DATA-END*/')[0];
const M=new Function(core+data+';return {gradeItem,liveCheck,nextWord,displayText,BUILTIN};')();
const I=(d,n)=>M.BUILTIN.find(x=>x.id===d).items.find(i=>i.d===n);
let fails=0; const ok=(c,m)=>{ if(!c){fails++;console.log('FAIL:',m);} };
const live=(it,t,mode)=>{ let typed='',st='ok',msg=''; for(const w of t.split(/\s+/)){ typed+=w+' '; const lc=M.liveCheck(it,typed,mode); if(lc.state!=='ok'){ st=lc.state; msg=lc.msg; break; } } return st; };
const dose=I('dose','Aspirin'), notes=I('notes','Aspirin'); const N=M.displayText(notes.a);
for(const mode of ['keys','exact']){
  for(const t of ['Aspirin 324 mg chewable PO','ASA 324 mg chewable PO','asa 324 mg chewable PO','Aspirn 324 mg chewable PO']){ ok(M.gradeItem(dose,t,mode).pass,`dose "${t}" (${mode})`); ok(live(dose,t+' x',mode)==='ok',`dose live "${t}" (${mode})`); }
  ok(!M.gradeItem(dose,'ASA 325 mg chewable PO',mode).pass,`325 still fails (${mode})`);
  ok(!M.gradeItem(dose,'324 mg chewable PO',mode).pass,`no drug name fails (${mode})`);
  const vars=[
    N.replace(/aspirin/g,'ASA').replace(/Aspirin/g,'ASA'),
    N.replace('If aspirin is not given','If aspirin is withheld'),
    N.replace('Aspirin may be withheld','Aspirin may not be given'),
    N.replace('If aspirin is not given','If ASA is witheld').replace('Aspirin may be withheld','ASA may not be given'),
  ];
  vars.forEach((t,i)=>{ const g=M.gradeItem(notes,t,mode); ok(g.pass,`notes variant ${i} (${mode}) ${JSON.stringify(g.missing)}`); ok(live(notes,M.displayText(t).replace(/[•◦]/g,' ')+' ',mode)==='ok',`notes live variant ${i} (${mode})`); });
  ok(!M.gradeItem(notes,N.replace('If aspirin is not given','If aspirin is given'),mode).pass,`"given" for "not given" fails (${mode})`);
  ok(!M.gradeItem(notes,N.replace('Aspirin may be withheld','Aspirin may not be withheld'),mode).pass,`"not withheld" fails (${mode})`);
  ok(!M.gradeItem(notes,N.replace('Aspirin may be withheld','Aspirin may be given'),mode).pass,`"may be given" for "may be withheld" fails (${mode})`);
}
console.log('next word at "If aspirin is":', M.nextWord(notes,N.split('If aspirin is')[0]+'If aspirin is ','keys'));
let reg=0, alarms=0;
for(const d of M.BUILTIN) for(const it of d.items){ if(it.none||it.na||typeof it.a!=='string') continue;
  for(const mode of ['keys','exact']){ if(!M.gradeItem(it,it.a,mode).pass){ reg++; console.log('regress',d.id,it.d,mode); } if(live(it,M.displayText(it.a).replace(/[•◦]/g,' ')+' ',mode)!=='ok'){ alarms++; console.log('alarm',d.id,it.d,mode); } } }
ok(reg===0&&alarms===0,`regressions ${reg}, live alarms ${alarms}`);
console.log(fails?`${fails} FAILED`:'ALL PASS');
