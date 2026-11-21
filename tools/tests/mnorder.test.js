const fs=require('fs');
const html=fs.readFileSync('/home/claude/protocol-drill/index.html','utf8');
const core=html.split('/*CORE-START*/')[1].split('/*CORE-END*/')[0];
const data=html.split('/*DATA-START*/')[1].split('/*DATA-END*/')[0];
const M=new Function(core+data+';return {mnemonicOrder,gradeItem,BUILTIN};')();
let fails=0; const ok=(c,m)=>{ if(!c){fails++;console.log('FAIL:',m);} else console.log('ok  ',m); };
const ad=M.BUILTIN.find(d=>d.id==='adv').items.find(i=>i.d==='Adenosine'); const items=ad.mn;
console.log('book:',items.join(' | '));
const az=M.mnemonicOrder(items,'az'); console.log('A-Z: ',az.join(' | '));
ok(az[0][0]==='D'&&az.length===items.length,'A-Z sorted');
ok(M.mnemonicOrder(items,'book').join()===items.join(),'book unchanged');
// a custom mnemonic in a different order; duplicate letters resolved by the closest start
const S2=items.filter(x=>x[0]==='S'), F2=items.filter(x=>x[0]==='F');
console.log('S items:',S2,'F items:',F2);
const mine=`Playful ${S2[1].slice(0,3)}dogs ${F2[1].slice(0,2)}zzy Hats Never Don't ${S2[0].slice(0,2)}ep ${F2[0].slice(0,3)}e`;
const o=M.mnemonicOrder(items,'mine',mine); console.log('mine "'+mine+'":',o.join(' | '));
ok(o[0][0]==='P'&&o[1]===S2[1]&&o[2]===F2[1]&&o[3][0]==='H'&&o[4][0]==='N'&&o[5][0]==='D'&&o[6]===S2[0]&&o[7]===F2[0],'mine follows the mnemonic, closest start wins');
ok(M.mnemonicOrder(items,'mine','PSFHNDSF').map(x=>x[0]).join('')==='PSFHNDSF','capitals-only mnemonic, letter by letter');
ok(M.mnemonicOrder(items,'mine','Hats Never').slice(2).join()===items.filter(x=>x[0]!=='H'&&x[0]!=='N').join()||M.mnemonicOrder(items,'mine','Hats Never').join()===items.join(),'short mnemonic -> book order');
ok(M.mnemonicOrder(items,'mine','zzz qqq').join()===items.join(),'unrelated mnemonic -> book order');
ok(M.mnemonicOrder(items,'mine','').join()===items.join(),'empty -> book order');
const all=new Set(o); ok(all.size===items.length,'no effect lost or duplicated');
// reordered answer still grades the same
const reord={...ad,a:'• '+az.join('\n• ')};
ok(M.gradeItem(reord,items.join(', '),'keys').pass&&M.gradeItem(ad,az.join(', '),'keys').pass,'grading unaffected');
console.log(fails?`${fails} FAILED`:'ALL PASS');
