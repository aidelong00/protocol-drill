const fs=require('fs');
const html=fs.readFileSync('/home/claude/protocol-drill/index.html','utf8');
const core=html.split('/*CORE-START*/')[1].split('/*CORE-END*/')[0];
const data=html.split('/*DATA-START*/')[1].split('/*DATA-END*/')[0];
const M=new Function(core+data+';return {gradeItem,fixTargets,optsOf,liveCheck,nextWord,mnemonicLetters,displayText,BUILTIN};')();
const {gradeItem,fixTargets,optsOf,liveCheck,nextWord,mnemonicLetters,displayText,BUILTIN}=M;
let fails=0; const ok=(c,m)=>{ if(!c){fails++;console.log('FAIL:',m);} };
const D=id=>BUILTIN.find(x=>x.id===id); const I=(id,d)=>D(id).items.find(i=>i.d===d);
const flat=t=>t.replace(/[•◦]/g,' ').replace(/\s+/g,' ').trim();
console.log('decks:',BUILTIN.map(d=>`${d.id}(${d.items.length})`).join(' '));
// ---- adverse effects: any order ----
const ad=I('adv','Adenosine'); const items=ad.mn;
ok(items.length===8&&items[0]==='Flushing','adenosine items');
for(const mode of ['keys','exact']){
  ok(gradeItem(ad,items.join(', '),mode).pass,`adv in book order (${mode})`);
  ok(gradeItem(ad,items.slice().reverse().join(', '),mode).pass,`adv reversed (${mode})`);
  ok(gradeItem(ad,items.slice().sort().join('\n'),mode).pass,`adv A-Z (${mode})`);
  const g=gradeItem(ad,items.filter(x=>x!=='Sweating'&&x!=='Paresthesia').join(', '),mode);
  ok(!g.pass&&g.mistakes.length===2,`adv two missing items = 2 mistakes (${mode}) got ${g.mistakes.length}`);
  const t=fixTargets(ad.a,g,optsOf(ad)); ok(JSON.stringify(t.map(x=>x.text))===JSON.stringify(['Sweating','Paresthesia']),`adv retype just the missing items (${mode}) ${JSON.stringify(t)}`);
  const g2=gradeItem(ad,items.map(x=>x==='Severe bronchospasm in patients with asthma'?'asthma with patients bronchospasm in severe':x).join(', '),mode);
  ok(!g2.pass,`adv words scrambled inside one item fail (${mode})`);
}
const ac=I('adv','Acetaminophen (IV)');
ok(gradeItem(ac,'Nausea and vomiting, skin rash, itching, overdose can cause hepatotoxicity','keys').pass,'adv: "nausea and vomiting" for nausea/vomiting is fine');
ok(gradeItem(ac,'skin rash, itching, overdose can cause hepatotoxicity, nausea/vomiting','keys').pass,'adv: list order free');
// ---- notes: bullets any order, words in order ----
const nl=I('notes','Lidocaine'); const nb=displayText(nl.a).split('\n').map(l=>l.replace(/^• /,''));
ok(gradeItem(nl,[nb[2],nb[0],nb[1]].join(' '),'keys').pass,'notes bullets in any order');
ok(!gradeItem(nl,[nb[0],nb[1]].join(' '),'keys').pass,'notes missing a bullet fails');
ok(!gradeItem(nl,[nb[0],nb[1],nb[2].split(' ').reverse().join(' ')].join(' '),'keys').pass,'notes scrambled bullet fails');
// every new card passes itself, both modes, flat and in a shuffled bullet order
for(const id of ['adv','notes']) for(const it of D(id).items) for(const mode of ['keys','exact']){
  const t=displayText(it.a); ok(gradeItem(it,t,mode).pass,`${id} ${it.d} self (${mode})`);
  const lines=t.split('\n'); ok(gradeItem(it,flat(lines.slice().reverse().join('\n')),mode).pass,`${id} ${it.d} reversed bullets (${mode})`);
}
// ---- live check: typing every card correctly never warns ----
let steps=0, falseAlarms=[];
for(const d of BUILTIN) for(const it of d.items) for(const mode of ['keys','exact']){
  if(it.none||it.na) continue;
  const words=flat(displayText(it.a)).split(' ');
  let typed='';
  for(const w of words){ typed+=w+' '; steps++; const lc=liveCheck(it,typed,mode); if(lc.state!=='ok'){ falseAlarms.push(`${d.id} ${it.d} (${mode}) at "${w}": ${lc.state} ${lc.msg}`); break; } }
}
console.log('live-check steps typed:',steps,'false alarms:',falseAlarms.length); falseAlarms.slice(0,8).forEach(x=>console.log('   ',x));
ok(falseAlarms.length===0,'no false alarms while typing correctly');
// the example: sympathetic for parasympathetic
const at=I('moa','Atropine'); const aw=flat(displayText(at.a)).replace('parasympathetic','sympathetic').split(' ');
let states=[]; let typed='';
for(const w of aw){ typed+=w+' '; const lc=liveCheck(at,typed,'keys'); states.push(lc.state); if(lc.state==='stop'){ console.log('   stop message:',lc.msg); break; } }
const iSym=aw.indexOf('sympathetic');
ok(states[iSym]==='ok','no signal on the wrong word itself');
ok(states.indexOf('warn')>iSym&&states.indexOf('warn')<=iSym+4,`warns within 2-4 words (warn at +${states.indexOf('warn')-iSym})`);
ok(states.includes('stop'),'eventually stops');
// skipped word
const nx=I('moa','Naloxone'); let st=[]; typed='';
for(const w of flat(displayText(nx.a)).replace('opioid receptors','receptors').split(' ')){ typed+=w+' '; const lc=liveCheck(nx,typed,'keys'); st.push(lc.state); if(lc.state==='stop'){ console.log('   stop message:',lc.msg); break; } }
const iw=st.indexOf('warn'), is=st.indexOf('stop');
ok(iw>=0&&is>iw&&is-iw<=3,`skipped word warns, then stops a couple of words later (warn at ${iw}, stop at ${is})`);
// flip does not warn
const mg=I('moa','Magnesium Sulfate'); typed=''; let bad=false;
for(const w of flat(displayText(mg.a)).replace('motor nerve impulse','nerve motor impulse').split(' ')){ typed+=w+' '; if(liveCheck(mg,typed,'keys').state!=='ok') bad=true; }
ok(!bad,'a one-word flip never warns');
// adverse effects (any order): unknown word warns
const am=I('adv','Amiodarone'); typed=''; st=[];
for(const w of 'Hypotension, bradycardia, seizures, dizziness, AV block, nausea, vomiting, burning'.split(' ')){ typed+=w+' '; st.push(liveCheck(am,typed,'keys').state); }
ok(st.includes('warn')||st.includes('stop'),'adv: an effect not on the list warns');
// ---- next word ----
ok(nextWord(nx,'','keys')==='Competitive','next word at start');
ok(nextWord(nx,'Competitive inhibitor of ','keys')==='opioid','next word mid-answer');
ok(nextWord(I('contra','Amiodarone'),'','keys')==='None','next word on a None card');
ok(nextWord(nl,nb[0]+' '+nb[1]+' ','keys')==='Lidocaine','notes: after bullets 1-2, next is the start of bullet 3 ('+nextWord(nl,nb[0]+' '+nb[1]+' ','keys')+')');
ok(nextWord(nl,nb[1]+' ','keys')==='If','notes: after only bullet 2, next is the start of skipped bullet 1');
ok(nextWord(nl,nb[2].split(' ').slice(0,3).join(' ')+' ','keys')==='to'||nextWord(nl,nb[2].split(' ').slice(0,3).join(' ')+' ','keys')==='applied','notes: mid-bullet next word ('+nextWord(nl,nb[2].split(' ').slice(0,3).join(' ')+' ','keys')+')');
// ---- mnemonic letters ----
ok(mnemonicLetters(items,false)==='F S D N H F S P','book order letters: '+mnemonicLetters(items,false));
ok(mnemonicLetters(items,true)==='D F F H N P S S','A-Z letters: '+mnemonicLetters(items,true));
console.log(fails?`\n${fails} FAILURES`:'\nALL PASS');
