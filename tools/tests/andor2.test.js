const fs=require('fs');
const html=fs.readFileSync('/home/claude/protocol-drill/index.html','utf8');
const core=html.split('/*CORE-START*/')[1].split('/*CORE-END*/')[0];const data=html.split('/*DATA-START*/')[1].split('/*DATA-END*/')[0];
const M=new Function(core+data+';return {gradeItem,displayText,BUILTIN};')();
let fails=0,n=0; const ok=(c,m)=>{ n++; if(!c){fails++;console.log('FAIL:',m);} };
for(const deck of M.BUILTIN) for(const it of deck.items){ const T=M.displayText(it.a); if(typeof T!=='string'||!/\band\/or\b/.test(T)) continue;
  for(const mode of ['keys','exact']){
    for(const v of ['and/or','and and/or','and or']) ok(M.gradeItem(it,T.replace(/\band\/or\b/,v),mode).pass,`${it.d} "${v}" passes (${mode})`);
    for(const v of ['and','or','or/and','or and','and/and','or/or']){ const g=M.gradeItem(it,T.replace(/\band\/or\b/,v),mode); ok(!g.pass,`${it.d} "${v}" fails (${mode})`); }
  }
}
console.log(fails?fails+' FAILURES':'ALL PASS ('+n+')'); process.exit(fails?1:0);
