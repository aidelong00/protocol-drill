const fs=require('fs');
const html=fs.readFileSync(process.argv[2]||'/home/claude/protocol-drill/index.html','utf8');
const core=html.split('/*CORE-START*/')[1].split('/*CORE-END*/')[0];const data=html.split('/*DATA-START*/')[1].split('/*DATA-END*/')[0];
const M=new Function(core+data+';return {liveCheck,gradeItem,displayText,BUILTIN};')();
const it=M.BUILTIN.find(d=>d.id==='moa').items.find(i=>/Calcium Chloride/.test(i.d));
console.log(it.d,'|',M.displayText(it.a));
const typed='Essential regulator for the excitation threshold of nerves and muscles, causes significant increase in myocardial contractility is the antidote for some calcium chan';
for(const mode of ['keys','exact']){ let t=''; const out=[];
  for(const w of typed.split(' ')){ t+=w+' '; const lc=M.liveCheck(it,t,mode); out.push(w+':'+lc.state+(lc.n!=null?'('+lc.n+')':'')); }
  console.log(mode, out.slice(12).join('  '));
}
const t2='Essential regulator for the excitation threshold of nerves and muscles, causes significant increase in myocardial contractility is the antidote for some ';
const r=M.liveCheck(it,t2,'keys'); console.log(r.state,'|',r.msg,'| kept:',JSON.stringify(t2.slice(0,r.cut)));
const t3='Essential regulator for the excitation threshold of nerves and muscles; causes significant increase in myocardial contractility and automaticity. Antidote ';
const r3=M.liveCheck(it,t3,'keys'); console.log(r3.state,'|',r3.msg);
const t4='Essential regulator for the excitation threshold of nerves and muscles; causes significant increase in myocardial contractility and automaticity ventricular. Antidote ';
console.log('flip:',M.liveCheck(it,t4,'keys').state, M.gradeItem(it,t4+'for some electrolyte imbalances and calcium channel and/or beta blocker toxicity.','keys').pass);
