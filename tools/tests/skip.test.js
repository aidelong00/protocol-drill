const fs=require('fs');
const html=fs.readFileSync('/home/claude/protocol-drill/index.html','utf8');
const core=html.split('/*CORE-START*/')[1].split('/*CORE-END*/')[0];const data=html.split('/*DATA-START*/')[1].split('/*DATA-END*/')[0];
const M=new Function(core+data+';return {liveCheck,gradeItem,displayText,norm,BUILTIN,LEEWAY};')();
let fails=0,n=0; const ok=(c,m)=>{ n++; if(!c){fails++; if(fails<30) console.log('FAIL:',m);} };
const steps=(it,t,mode,from=0)=>{ const W=t.split(/(\s+)/); let typed='', res=[]; for(let i=0;i<W.length;i++){ typed+=W[i]; if(/\s/.test(W[i])&&i>=from){ res.push([i,M.liveCheck(it,typed,mode).state]); } } res.push([W.length,M.liveCheck(it,typed+' ',mode).state]); return res; };
let skipCaught=0, skipTotal=0, skipLate=[], flipStops=0, flips=0;
for(const deck of M.BUILTIN) for(const it of deck.items){
  if(it.any||it.none||it.na||it.mn) continue;
  const T=M.displayText(it.a); if(typeof T!=='string') continue;
  const t=T.replace(/[•◦]\s*/g,'');
  for(const mode of ['keys','exact']){
    const bad=steps(it,t,mode).filter(s=>s[1]!=='ok');
    ok(!bad.length,`${deck.id}/${it.d} verbatim false alarm (${mode})`);
    if(mode!=='keys') continue;
    const W=t.split(' ');
    // skip one content word (not the last 3) at a few positions
    for(let i=2;i<W.length-3;i+=Math.max(1,Math.floor(W.length/6))){
      const w=W[i].replace(/[^\w-]/g,''); if(!w||w.length<4||/^\d/.test(w)||M.LEEWAY.keys.has(w.toLowerCase())) continue;
      if(W.filter(x=>x.replace(/[^\w-]/g,'').toLowerCase()===w.toLowerCase()).length>1) continue;
      const sk=W.slice(0,i).concat(W.slice(i+1));
      if(M.gradeItem(it,sk.join(' '),mode).pass) continue;   // a word the grader doesn't require here
      skipTotal++; let typed=sk.slice(0,i).join(' ')+' ', caughtAt=-1;
      let stopAt=-1; for(let j=i;j<sk.length;j++){ typed+=sk[j]+' '; const stt=M.liveCheck(it,typed,mode).state; if(stt!=='ok'&&caughtAt<0) caughtAt=j-i+1; if(stt==='stop'){ stopAt=j-i+1; break; } }
      if(caughtAt>0&&stopAt>0&&stopAt<caughtAt) skipLate.push('stopped before warning');
      if(caughtAt>0&&caughtAt<=6) skipCaught++; else skipLate.push(`${it.d} skip "${w}" caught after ${caughtAt} words`);
    }
    // swap adjacent content words: if the grade passes, live shouldn't stop
    for(let i=1;i<W.length-2;i+=3){
      const a=W[i],b=W[i+1]; if(/[.,;:]$/.test(a)||/[.,;:]$/.test(b)||/\s/.test(a+b)) continue;
      const sw=W.slice(); sw[i]=b; sw[i+1]=a; const txt=sw.join(' ');
      if(!M.gradeItem(it,txt,mode).pass) continue; flips++;
      if(steps(it,txt,mode).some(s=>s[1]==='stop')) { flipStops++; if(flipStops<6) console.log('flip stop:',it.d,`"${b} ${a}"`); }
    }
  }
}
console.log(`skips warned within 6 words (2 content words): ${skipCaught}/${skipTotal}; flips that pass grading but stop live: ${flipStops}/${flips}`);
skipLate.slice(0,8).forEach(x=>console.log('  late:',x));
ok(flipStops<=42,"flips stopped no more than before (42)"); ok(skipCaught>=skipTotal*0.98,"skips caught (a few near the end of an answer are left to Check)");
console.log(fails?fails+' FAILURES':'ALL PASS ('+n+')'); process.exit(fails?1:0);
