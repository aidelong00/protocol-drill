const fs=require('fs');
const html=fs.readFileSync('/home/claude/protocol-drill/index.html','utf8');
const core=html.split('/*CORE-START*/')[1].split('/*CORE-END*/')[0];
const data=html.split('/*DATA-START*/')[1].split('/*DATA-END*/')[0];
const M=new Function(core+data+';return {gradeItem,grade,optsOf,nextWord,liveCheck,displayText,norm,BUILTIN,CRIT};')();
let fails=0,n=0; const ok=(c,m)=>{ n++; if(!c){fails++; if(fails<25) console.log('FAIL:',m);} };
const live=(it,t,mode)=>{ let typed=''; for(const w of t.split(/\s+/)){ typed+=w+' '; const lc=M.liveCheck(it,typed,mode); if(lc.state!=='ok') return lc.state; } return 'ok'; };
let crit=0;
for(const deck of M.BUILTIN) for(const it of deck.items){
  if(it.none||it.na) continue;
  const T=M.displayText(it.a); if(typeof T!=='string') continue;
  const W=T.split(/(\s+)/);
  W.forEach((w,i)=>{
    if(!w.trim()||/^[•◦]$/.test(w)) return;
    const toks=M.norm(w.replace(/[^\w-]+$/,'')); if(toks.length!==1) return;
    const bare=w.replace(/^[^\w]+|[^\w%]+$/g,''); if(!bare) return;
    const t2=W.slice(0,i).join('')+bare+' '+w+W.slice(i+1).join('');   // "and and", "IV IV/IO"
    const isCrit=M.CRIT(toks[0])&&toks[0]!=='and'&&toks[0]!=='or';
    for(const mode of ['keys','exact']){
      const g=M.gradeItem(it,t2,mode);
      if(isCrit){ if(mode==='keys'&&/^(not|no)$/.test(toks[0])){ crit++; ok(!g.pass,`${deck.id}/${it.d}: doubled "${bare}" must fail`); } }
      else { ok(g.pass,`${deck.id}/${it.d}: doubled "${bare}" (${mode}) ${JSON.stringify(g.missing)}`);
        if(mode==="keys"&&i%7===0&&W.length<200){ const L=live(it,t2.replace(/[•◦]/g,' ')+' ',mode); ok(L==='ok',`${deck.id}/${it.d}: live doubled "${bare}" ${L}`); } }
    }
  });
}
// doubled numbers still count
const it=M.BUILTIN.find(d=>d.id==='dose').items.find(x=>/\b\d+ mg\b/.test(M.displayText(x.a)));
const T=M.displayText(it.a), nm=T.match(/\b(\d+) mg\b/)[1];
ok(!M.gradeItem(it,T.replace(nm+' mg',nm+' '+nm+' mg'),'keys').pass,`doubled number "${nm}" in ${it.d} must fail`);
console.log(`${n-fails}/${n} passed (not/no doubles checked: ${crit})`); process.exit(fails?1:0);
