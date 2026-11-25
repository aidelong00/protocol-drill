const fs=require('fs');
const html=fs.readFileSync('/home/claude/protocol-drill/index.html','utf8');
const core=html.split('/*CORE-START*/')[1].split('/*CORE-END*/')[0];const data=html.split('/*DATA-START*/')[1].split('/*DATA-END*/')[0];
const M=new Function(core+data+';return {gradeItem,liveCheck,nextWord,displayText,BUILTIN};')();
let fails=0,n=0; const ok=(c,m)=>{ n++; if(!c){fails++; if(fails<15) console.log('FAIL:',m);} };
const card=(d,name)=>M.BUILTIN.find(x=>x.id===d).items.find(i=>i.d.startsWith(name));
const clean=g=>g.pass&&!(g.order&&g.order.length)&&!g.res.some(r=>(r.parts||[]).some(p=>p.ord||p.bad));
const live=(it,t,mode)=>{ let typed=''; for(const w of t.split(/\s+/)){ typed+=w+' '; const s=M.liveCheck(it,typed,mode).state; if(s!=='ok') return s+' at '+w; } return 'ok'; };
// the user's Acetaminophen answer: correct, no word-order note
const ac=card('moa','Acetaminophen'); const yours='Mechanism of action unclear may work peripherally to block pain impulse generation; may also inhibi synthesis of prostaglandin in the cns';
for(const mode of ['keys','exact']){ const g=M.gradeItem(ac,yours,mode); ok(clean(g),`Acetaminophen "synthesis of prostaglandin" clean (${mode}) order=${JSON.stringify(g.order)} missing=${JSON.stringify(g.missing)}`); ok(live(ac,yours,mode)==='ok',`live (${mode})`); }
ok(clean(M.gradeItem(ac,yours.replace('prostaglandin','prostaglandins'),'keys')),'plural "synthesis of prostaglandins"');
ok(clean(M.gradeItem(ac,yours.replace('synthesis of prostaglandin','synthesis of the prostaglandin'),'keys')),'"synthesis of the prostaglandin"');
// next word after "inhibit synthesis of prostaglandin " is "in"/"CNS" territory, not "prostaglandin" again
const nw=M.nextWord(ac,'Mechanism of action unclear; may work peripherally to block pain impulse generation; may also inhibit synthesis of prostaglandin ','keys');
ok(nw&&!/prostaglandin|synthesis/i.test(nw),'next word moves on after "synthesis of prostaglandin": '+nw);
// the other way round: card says "action of acetylcholine" (Atropine), you write "acetylcholine action"
const at=card('moa','Atropine'); const AT=M.displayText(at.a);
for(const mode of ['keys','exact']) ok(clean(M.gradeItem(at,AT.replace('action of acetylcholine','acetylcholine action'),mode)),`Atropine "acetylcholine action" clean (${mode})`);
// Ipratropium (card: "acetylcholine action"), you: "action of acetylcholine"
const ip=card('moa','Ipratropium'); const IP=M.displayText(ip.a);
ok(clean(M.gradeItem(ip,IP.replace('acetylcholine action','action of acetylcholine'),'keys')),'Ipratropium "action of acetylcholine" clean');
// verbatim still clean everywhere, and swapping in unrelated words still fails
let checked=0;
for(const d of M.BUILTIN) for(const it of d.items){ const T=M.displayText(it.a); if(typeof T!=='string'||it.none||it.na) continue; checked++;
  for(const mode of ['keys','exact']){ const g=M.gradeItem(it,T,mode); ok(g.pass,`${d.id}/${it.d} verbatim (${mode})`); } }
ok(!M.gradeItem(ac,yours.replace('synthesis of prostaglandin','synthesis of serotonin'),'keys').pass,'"synthesis of serotonin" still wrong');
ok(!M.gradeItem(ac,yours.replace('synthesis of prostaglandin','prostaglandin of synthesis'),'keys').pass||true,'(no crash)');
console.log(`(${checked} cards verbatim)`, fails?fails+' FAILURES':'ALL PASS ('+n+')'); process.exit(fails?1:0);
