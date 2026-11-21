const fs=require('fs');
const html=fs.readFileSync('/home/claude/protocol-drill/index.html','utf8');
const core=html.split('/*CORE-START*/')[1].split('/*CORE-END*/')[0];
const data=html.split('/*DATA-START*/')[1].split('/*DATA-END*/')[0];
const {grade,gradeItem,gradeProt,displayText,BUILTIN}=new Function(core+data+';return {grade,gradeItem,gradeProt,displayText,BUILTIN};')();
let fails=0; const ok=(c,m)=>{ if(!c){fails++;console.log('FAIL:',m);} };
const D=id=>BUILTIN.find(x=>x.id===id); const I=(id,d)=>D(id).items.find(i=>i.d===d);
console.log('decks:',BUILTIN.map(d=>`${d.id}(${d.items.length})`).join(' '));
// protocols
const g1=I('ind','Glucagon');
ok(gradeProt(g1.p,'Protocols: S-123, S-134, S-161').pass,'exact protocol text');
ok(gradeProt(g1.p,'123 134 161').pass,'numbers only');
ok(gradeProt(g1.p,'161, 123, s-134').pass,'any order, lowercase s');
ok(!gradeProt(g1.p,'123 134').pass,'missing one');
ok(!gradeProt(g1.p,'123 134 161 165').pass,'extra one');
ok(JSON.stringify(gradeProt(g1.p,'123 134 165'))===JSON.stringify({pass:false,missing:['S-161'],extra:['S-165']}),'reports missing + extra');
ok(!gradeProt(g1.p,'').pass,'empty fails');
// None / NA
const am=I('contra','Amiodarone'); for(const t of ['None','none','NA','N/A','n/a','None.','none listed']) ok(gradeItem(am,t,'keys').pass,`contra none accepts "${t}"`);
ok(!gradeItem(am,'',"keys").pass,'contra none: blank fails');
ok(!gradeItem(am,'Hypotension','keys').pass,'contra none: wrong content fails');
ok(!gradeItem(I('contra','Fentanyl'),'None','keys').pass,'fentanyl contra "None" fails');
ok(gradeItem(I('contra','Fentanyl'),'Pregnancy with pain from active labor','keys').pass,'fentanyl contra exact passes');
const asp=I('peds','Aspirin'); for(const t of ['NA','N/A','na','Not indicated','Not indicated for use in pediatrics','not indicated for use in peds'.replace('peds','pediatrics')]) ok(gradeItem(asp,t,'keys').pass,`peds NA accepts "${t}"`);
ok(!gradeItem(asp,'per drug chart','keys').pass,'peds NA: wrong content fails');
ok(!gradeItem(I('peds','Glucagon'),'NA','keys').pass,'glucagon peds "NA" fails');
// every new card passes itself in both modes; dropping a required word fails
let n=0;
for(const id of ['contra','peds','ind']) for(const it of D(id).items){
  for(const mode of ['keys','exact']){
    const t=displayText(it.a); n++;
    ok(gradeItem(it,t,mode).pass,`${id} ${it.d} self (${mode})`);
    ok(gradeItem(it,t.replace(/[•◦]/g,' ').replace(/\s+/g,' '),mode).pass,`${id} ${it.d} flat (${mode})`);
  }
}
const F=I('peds','Fentanyl'), ft=displayText(F.a).replace(/[•◦]/g,' ');
ok(!gradeItem(F,ft.replace('≥10 kg: Fentanyl IV','>10 kg: Fentanyl IV'),'keys').pass,'peds fentanyl > vs ≥ counts');
ok(gradeItem(F,ft.replace(/≥/g,'>='),'keys').pass,'>= accepted for ≥');
ok(!gradeItem(F,ft.replace('Fentanyl IN per drug chart. MR at initial IN dose BHO','Fentanyl per drug chart. MR at initial dose BHO'),'keys').pass,'peds fentanyl missing IN route fails');
const DX=I('peds','Dextrose'), dt=displayText(DX.a);
ok(!gradeItem(DX,dt.replace('(<45 mg/dL for neonate), MR','(<40 mg/dL for neonate), MR'),'keys').pass,'peds dextrose neonate number');
console.log('self checks:',n);
console.log(fails?`\n${fails} FAILURES`:'\nALL PASS');
