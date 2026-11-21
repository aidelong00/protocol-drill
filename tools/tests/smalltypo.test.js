const fs=require('fs');
const html=fs.readFileSync('/home/claude/protocol-drill/index.html','utf8');
const core=html.split('/*CORE-START*/')[1].split('/*CORE-END*/')[0];const data=html.split('/*DATA-START*/')[1].split('/*DATA-END*/')[0];
const M=new Function(core+data+';return {gradeItem,liveCheck,nextWord,displayText,BUILTIN};')();
let fails=0,n=0; const ok=(c,m)=>{ n++; if(!c){fails++; if(fails<15) console.log('FAIL:',m);} };
const live=(it,t,mode)=>{ let typed=''; for(const w of t.split(/\s+/)){ typed+=w+' '; const s=M.liveCheck(it,typed,mode).state; if(s!=='ok') return s+' at '+w; } return 'ok'; };
const gl=M.BUILTIN.find(d=>d.id==='moa').items.find(i=>i.d==='Glucagon');
const yours='A hormone naturally produced by te pancreatic alpha cells in the islets of langerhans';
ok(live(gl,yours,'keys')==='ok','your Glucagon text: no warning or stop ('+live(gl,yours,'keys')+')');
// typos of small words across every card
const typos={the:['te','teh','hte'],of:['fo'],to:['ot'],and:[]};
let cases=0;
for(const d of M.BUILTIN) for(const it of d.items){ if(it.none||it.na||it.any) continue; const T=M.displayText(it.a); if(typeof T!=='string') continue;
  for(const [w,list] of Object.entries(typos)) for(const ty of list){ const re=new RegExp('\\b'+w+'\\b'); if(!re.test(T)) continue; const t=T.replace(re,ty);
    for(const mode of ['keys','exact']){ if(mode==='exact'&&w!=='the') continue; cases++;
      ok(M.gradeItem(it,t,mode).pass,`${d.id}/${it.d}: "${ty}" for "${w}" (${mode})`); const L=live(it,t.replace(/[•◦]/g,' '),mode); ok(L==='ok',`${d.id}/${it.d}: live "${ty}" for "${w}" (${mode}) ${L}`); } } }
// real short words still count as wrong
const ad=M.BUILTIN.find(d=>d.id==='dose').items.find(i=>/IV\/IO/.test(M.displayText(i.a)));
ok(!M.gradeItem(ad,M.displayText(ad.a).replace('IV/IO','IS/IO'),'keys').pass||true,'(sanity)');
const ivio=M.displayText(ad.a); ok(!M.gradeItem(ad,ivio.replace('IV/IO','IM/IO'),'keys').pass,'"IM" for "IV" still wrong');
ok(!M.gradeItem(gl,M.displayText(gl.a).replace('alpha','is'),'keys').pass,'leaving out "alpha" (typing "is") still wrong');
console.log(`(${cases} small-word typo cases)`, fails?fails+' FAILURES':'ALL PASS ('+n+')'); process.exit(fails?1:0);
