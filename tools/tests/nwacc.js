const fs=require('fs');
function load(f){const html=fs.readFileSync(f,'utf8');const core=html.split('/*CORE-START*/')[1].split('/*CORE-END*/')[0];const data=html.split('/*DATA-START*/')[1].split('/*DATA-END*/')[0];return new Function(core+data+';return {nextWord,displayText,BUILTIN,LEEWAY};')();}
const O=load('/home/claude/protocol-drill/index.base.html'), N=load('/home/claude/protocol-drill/index.html');
const stats={}; const add=(k,o,n)=>{ stats[k]=stats[k]||{n:0,old:0,neu:0}; stats[k].n++; if(o) stats[k].old++; if(n) stats[k].neu++; };
const bad=[];
for(const deck of N.BUILTIN) for(const it of deck.items){
  if(!it.nw||it.none||it.na) continue; const T=N.displayText(it.a); if(typeof T!=='string') continue;
  const W=T.replace(/[•◦]\s*/g,'').split(/\s+/).filter(Boolean);
  const content=w=>/^[A-Za-z][A-Za-z-]{3,}$/.test(w);
  for(let i=4;i<W.length;i+=2){
    const pre=W.slice(0,i), exp=O.nextWord(it,pre.join(' ')+' ','keys');
    if(!exp) continue;
    if(N.nextWord(it,pre.join(' ')+' ','keys')!==exp) bad.push(['verbatim',it.d,pre.slice(-4).join(' '),exp,N.nextWord(it,pre.join(' ')+' ','keys')]);
    add('verbatim',true,N.nextWord(it,pre.join(' ')+' ','keys')===exp);
    const cases={};
    if(content(pre[i-2])&&content(pre[i-3])){ const f=pre.slice(); [f[i-3],f[i-2]]=[f[i-2],f[i-3]]; cases.flip=f; }
    if(content(pre[i-2])){ const f=pre.slice(); f[i-2]='zebra'; cases.wrongword=f; }
    { const f=pre.slice(); f.splice(i-2,0,'zebra'); cases.extra=f; }
    const later=W.slice(i+3).filter(w=>content(w.replace(/[.,;:]$/,'')));
    if(later.length&&content(pre[i-2])){ const f=pre.slice(); f[i-2]=later[later.length-1].replace(/[.,;:]$/,''); cases.laterword=f; }
    if(later.length){ const f=pre.slice(); f.push(later[0].replace(/[.,;:]$/,'')); cases.wordfromlater_at_end=null; }
    for(const k in cases){ const f=cases[k]; if(!f) continue; const txt=f.join(' ')+' ';
      const o=O.nextWord(it,txt,'keys')===exp, n=N.nextWord(it,txt,'keys')===exp; add(k,o,n);
      if(!n&&bad.length<400) bad.push([k,it.d,f.slice(-4).join(' '),exp,N.nextWord(it,txt,'keys')]); }
  }
}
for(const k in stats){ const s=stats[k]; console.log(k.padEnd(10),'cases',s.n,'old right',(100*s.old/s.n).toFixed(1)+'%','new right',(100*s.neu/s.n).toFixed(1)+'%'); }
const vb=bad.filter(b=>b[0]==='verbatim'); console.log('verbatim mismatches:',vb.length); vb.slice(0,8).forEach(b=>console.log('  ',JSON.stringify(b)));
['flip','wrongword','extra','laterword'].forEach(k=>bad.filter(b=>b[0]===k).slice(0,3).forEach(b=>console.log('  ',JSON.stringify(b))));
// half-typed last word (no space): stays on the word being typed
let ht=0,htOk=0;
for(const deck of N.BUILTIN) for(const it of deck.items){
  if(!it.nw||it.none||it.na) continue; const T=N.displayText(it.a); if(typeof T!=='string') continue;
  const W=T.replace(/[•◦]\s*/g,'').split(/\s+/).filter(Boolean);
  for(let i=4;i<W.length;i+=3){ const w=W[i]; if(!/^[A-Za-z]{6,}$/.test(w)) continue;
    const pre=W.slice(0,i).join(' ')+' '; const exp=O.nextWord(it,pre,'keys'); if(!exp||exp.toLowerCase()!==w.toLowerCase()) continue;
    ht++; if(N.nextWord(it,pre+w.slice(0,3),'keys')===exp) htOk++; }
}
console.log('half-typed word: still shows that word',htOk+'/'+ht);
const ip=N.BUILTIN.find(d=>d.id==='moa').items.find(i=>i.d.startsWith('Ipratropium'));
console.log('your Ipratropium case:',N.nextWord(ip,'Anticholinergic (parasympatholytic) agent; inhibits vagally mediated reflexes by antagonizing action of acetylcholine. ','keys'));
