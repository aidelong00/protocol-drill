const fs=require('fs');
const html=fs.readFileSync('/home/claude/protocol-drill/index.html','utf8');
const core=html.split('/*CORE-START*/')[1].split('/*CORE-END*/')[0];
const data=html.split('/*DATA-START*/')[1].split('/*DATA-END*/')[0];
const M=new Function(core+data+';return {gradeItem,nextWord,liveCheck,displayText,BUILTIN};')();
let fails=0,n=0; const ok=(c,m)=>{ n++; if(!c){fails++;console.log('FAIL:',m);} };
const live=(it,t,mode)=>{ let typed=''; for(const w of t.split(/\s+/)){ typed+=w+' '; const lc=M.liveCheck(it,typed,mode); if(lc.state!=='ok') return lc.state+' at "'+typed.slice(-30)+'"'; } return 'ok'; };
let wi=0,inn=0;
for(const deck of M.BUILTIN) for(const it of deck.items){
  const T=M.displayText(it.a); if(typeof T!=='string') continue;
  for(const mode of ['keys','exact']){
    if(/\bwithin\b/i.test(T)){ wi++;
      const t=T.replace(/\bwithin\b/g,'in').replace(/\bWithin\b/g,'In');
      ok(M.gradeItem(it,t,mode).pass,`${deck.id}/${it.d}: "in" for "within" (${mode})`);
      const L=live(it,t.replace(/[•◦]/g,' ')+' ',mode); ok(L==='ok',`${deck.id}/${it.d}: live "in" for "within" (${mode}) ${L}`);
      ok(!M.gradeItem(it,T.replace(/\bwithin\b/gi,'with'),mode).pass,`${deck.id}/${it.d}: "with" for "within" still fails (${mode})`);
      if(mode==='exact') ok(!M.gradeItem(it,T.replace(/\bwithin /gi,''),mode).pass,`${deck.id}/${it.d}: dropping "within" fails word for word`);
      // next word after "... in" continues past it
      const wI=T.search(/\b[Ww]ithin\b/); const want=M.nextWord(it,T.slice(0,wI+6)+' ',mode);
      const nw=M.nextWord(it,T.slice(0,wI)+'in ',mode); ok(nw&&nw===want,`${deck.id}/${it.d}: next word after "in" = ${nw} (want ${want}) (${mode})`);
    }
    const m=T.match(/\bin\b(?! \d+ m[lL])/);
    if(m){ inn++;
      const t=T.replace(/\bin\b(?! \d+ m[lL])/g,'within');
      ok(M.gradeItem(it,t,mode).pass,`${deck.id}/${it.d}: "within" for "in" (${mode})`);
    }
  }
}
console.log(`within cards ${wi/2}, in cards ${inn/2}; ${n-fails}/${n} passed`); process.exit(fails?1:0);
