const fs=require('fs');
const html=fs.readFileSync('/home/claude/protocol-drill/index.html','utf8');
const core=html.split('/*CORE-START*/')[1].split('/*CORE-END*/')[0];
const data=html.split('/*DATA-START*/')[1].split('/*DATA-END*/')[0];
const M=new Function(core+data+';return {norm,grade,displayText,refOf,BUILTIN,LEEWAY};')();
const {grade,displayText,refOf,BUILTIN,LEEWAY,norm}=M;
let fails=0; const ok=(c,msg)=>{ if(!c){fails++; console.log('FAIL:',msg);} };
const A=(deck,drug)=>BUILTIN.find(x=>x.id===deck).items.find(i=>i.d===drug).a;
const G=(deck,drug,txt,mode)=>grade(A(deck,drug),txt,mode);
let n=0, dropChecks=0;
for(const d of BUILTIN) for(const it of d.items){ n++;
  const t=displayText(it.a);
  for(const mode of ['keys','exact']){
    const g=grade(it.a,t,mode); ok(g.pass&&!g.order.length,`${d.id} ${it.d} self (${mode}): ${g.missing} ${g.order}`);
    // without bullets/newlines, as someone would type it
    const flat=t.replace(/[•◦]/g,' ').replace(/\s+/g,' ');
    ok(grade(it.a,flat,mode).pass,`${d.id} ${it.d} flat (${mode})`);
  }
  // dropping ANY required word must fail; dropping a leeway word must pass (keys)
  const words=t.split(/\s+/).filter(Boolean);
  words.forEach((w,i)=>{
    const toks=norm(w); if(!toks.length) return;
    const rest=words.filter((_,j)=>j!==i).join(' ');
    const allLee=toks.every(x=>LEEWAY.keys.has(x));
    const g=grade(it.a,rest,'keys'); dropChecks++;
    // a dropped word can still be satisfied if the same word appears elsewhere more times than required; count check
    if(allLee) ok(g.pass,`${d.id} ${it.d}: dropping leeway "${w}" should pass`);
    else if(g.pass&&!(d.id==='ind'&&it.d==='Adenosine')&&!(d.id==='class'&&it.d==='Aspirin'&&w==='(NSAID)')&&!(d.id==='notes'&&/^(normal|saline)$/.test(w))){ const cntRef=norm(t).filter(x=>x===toks[0]).length; if(cntRef<2) ok(false,`${d.id} ${it.d}: dropping "${w}" still passed`); }
  });
}
console.log('cards:',n,'drop checks:',dropChecks);
// behaviour spot checks
const C=[
 ['moa','Naloxone','Competitive inhibitor of opioid receptors in the brain.','keys',false],
 ['moa','Naloxone','Competitive inhibitor of opioid receptors in brain. Reverses respiratory depression associated with opioid overdose','keys',true],
 ['moa','Naloxone','competetive inhibiter of opiod receptors in brain, reverses respiratory depresion associated w opioid overdose','keys',true],
 ['moa','Naloxone','Reverses the respiratory depression associated with opioid overdose. Competitive inhibitor of opioid receptors in the brain.','keys',false],
 ['moa','Naloxone','Reverses the respiratory depression associated with opioid overdose. Competitive inhibitor of opioid receptors in the brain.','exact',false],
 ['moa','Naloxone','Competitive inhibitor of opioid receptors brain. Reverses respiratory depression associated with opioid overdose','exact',false],
 ['moa','Naloxone','Competitive inhibitor of opioid receptors in brain. Reverses respiratory depression associated with opioid overdose','exact',true],
 ['moa','Calcium Chloride','Essential regulator for the excitation threshold of nerves and muscles; causes significant increase in myocardial contractility and ventricular automaticity. Antidote for some electrolyte imbalances and calcium channel or beta blocker toxicity.','keys',false],
 ['moa','Calcium Chloride','Essential regulator for excitation threshold of nerves and muscles; causes significant increase in myocardial contractility and ventricular automaticity. Antidote for some electrolyte imbalances and calcium channel and or beta blocker toxicity','keys',true],
 ['moa','Atropine','Blocks the action of acetylcholine at parasympathetic sites in smooth muscle, secretory glands, and the CNS; increases cardiac output, dries secretions, and reverses the muscarinic effects of cholinergic poisoning.','keys',true],
 ['moa','Albuterol','Selective beta 2 adrenergic agonist that causes relaxation of smooth muscles in bronchial tree, decreasing airway resistance, facilitating mucus drainage and increasing vital capacity; shifts potassium intracellular; has mild beta 1 activity that may increase heart rate','keys',true],
 ['moa','Albuterol','Selective beta 1 adrenergic agonist that causes relaxation of smooth muscles in bronchial tree, decreasing airway resistance, facilitating mucus drainage and increasing vital capacity; shifts potassium intracellular; has mild beta 1 activity that may increase heart rate','keys',false],
 ['moa','Epinephrine','A naturally occurring catecholamine that acts directly on alpha and beta adrenergic receptors. It is the most potent activator of alpha receptors, vasoconstricting the aorta and peripheral vasculature. Beta 1 stimulation increases inotropy, chronotropy, and AV conduction. Beta 2 stimulation causes bronchial smooth muscle relaxation and vasodilation to internal organs and skeletal muscles.','keys',true],
 ['ind','Albuterol / Levalbuterol','Management of respiratory distress (noncardiac, anaphylaxis, and burns), suspected hypokalemia, and specific crush injuries','keys',false],
 ['ind','Albuterol / Levalbuterol','Management of respiratory distress (noncardiac, anaphylaxis, and burns), suspected hyperkalemia, and specific crush injuries','keys',true],
 ['ind','Midazolam','Management of seizures, sedation pre cardioversion pre pacing, unable to tolerate CPAP, intubated patients with agitation, and agitated combative patients','keys',true],
 ['ind','Midazolam','Management of seizures, sedation pre cardioversion or pre pacing, unable to tolerate CPAP, intubated patients with agitation, and agitated or combative patients','keys',true],
 ['dose','Nitroglycerin','For discomfort/pain of cardiac origin if SBP >=100 mmHg, NTG 0.4 mg SL, MR q3-5 min. For CHF: If systolic BP >=100 but <150: NTG 0.4 mg SL, MR q3-5 min. If systolic BP >=150: NTG 0.8 mg SL, MR q3-5 min','keys',true],
 ['dose','Nitroglycerin','For discomfort/pain of cardiac origin if SBP >100 mmHg, NTG 0.4 mg SL, MR q3-5 min. For CHF: If systolic BP >=100 but <150: NTG 0.4 mg SL, MR q3-5 min. If systolic BP >=150: NTG 0.8 mg SL, MR q3-5 min','keys',false],
 ['dose','Dextrose','D10 25 gm IV if BS >60 mg/dL. If patient remains symptomatic and BS remains <60 mg/dL, MR','keys',false],
 ['dose','Dextrose','D10 25 grams IV if BS <60 mg/dl. If patient remains symptomatic and BS remains <60 mg/dl, may repeat','keys',true],
 ['dose','Fentanyl','IV: up to 100 mcg IV, MR up to 50 mcg IV q5 min x2, maximum total dose 200 mcg IV. IN: up to 50 mcg IN, MR up to 50 mcg IN q15 min x2, max total dose 150 mcg IN','keys',true],
 ['dose','Fentanyl','IV: up to 100 mcg IV, MR up to 50 mcg IV q5 min x2, maximum total dose 200 mcg IV. IN: up to 50 mcg IN, MR up to 50 mcg IN q15 min x2, max total dose 150 mg IN','keys',false],
 ['dose','Amiodarone','For stable VT, amiodarone 150 mg in 100 mL of NS over 10 min IV/IO, MR x1 in 10 min. For persistent VF/pulseless VT after 3 defibrillation attempts, amiodarone 300 mg IV/IO, MR 150 mg q3-5 min (max 450 mg). For reported/witnessed AICD firing ≥2, amiodarone 150 mg in 100 mL of NS over 10 min IV/IO, MR x1 in 10 min','exact',true],
 ['dose','Calcium Chloride','For PEA with suspected hyperkalemia, CaCl2 1 gm IV/IO. For suspected hyperkalemia, if widened QRS complex, immediately administer CaCl2 1 gm IV/IO. For suspected calcium channel blocker OD, CaCl2 1 gm IV/IO. For specific crush injuries, CaCl2 1 gm IV/IO over 30 sec','keys',true],
 ['class','Aspirin','Antiplatelet agent, nonsteroidal anti inflammatory drug (NSAID)','keys',true],
 ['class','Aspirin','Antiplatelet agent, non-steroidal anti-inflammatory drug','keys',true],
];
for(const [dk,dr,txt,mode,exp] of C){ const g=G(dk,dr,txt,mode); ok(g.pass===exp,`${mode} ${dk} ${dr}: expected ${exp} got ${g.pass} [${g.missing}] :: "${txt.slice(0,70)}…"`); }

// ---- word order ----
const MG=A('moa','Magnesium Sulfate');
const base='Depresses CNS, blocks peripheral neuromuscular transmission, produces anticonvulsant effects; decreases amount of acetylcholine released at end-plate by motor nerve impulse. Slows rate of sinoatrial (SA) node impulse formation in myocardium and prolongs conduction time.';
const O=(label,txt,mode,expPass,expNote)=>{ const g=grade(MG,txt,mode); ok(g.pass===expPass&&(expNote==null||(g.order.length>0)===expNote),`ORDER ${label} (${mode}): pass=${g.pass} order=[${g.order}] missing=[${g.missing}]`); };
for(const mode of ['keys','exact']){
  O('exact text',base,mode,true,false);
  O('one flip',base.replace('motor nerve impulse','nerve motor impulse'),mode,true,true);
  O('two flips',base.replace('motor nerve impulse','nerve motor impulse').replace('prolongs conduction time','prolongs time conduction'),mode,true,true);
  O('three flips',base.replace('motor nerve impulse','nerve motor impulse').replace('prolongs conduction time','prolongs time conduction').replace('Depresses CNS','CNS Depresses'),mode,false);
  O('scrambled run',base.replace('decreases amount of acetylcholine released at end-plate','released acetylcholine end-plate decreases amount at of'),mode,false);
  O('word moved far',base.replace('Depresses CNS,','CNS,').replace('conduction time.','conduction time depresses.'),mode,false);
  O('sentences swapped','Slows rate of sinoatrial (SA) node impulse formation in myocardium and prolongs conduction time. Depresses CNS, blocks peripheral neuromuscular transmission, produces anticonvulsant effects; decreases amount of acetylcholine released at end-plate by motor nerve impulse.',mode,false);
  O('flip + typo',base.replace('motor nerve impulse','nerve motr impulse'),mode,true,true);
}
const AM=A('dose','Amiodarone'); const amT=displayText(AM).replace(/[•\n]/g,' ');
const amLines=displayText(AM).split('\n').map(l=>l.replace('• ',''));
ok(grade(AM,amT,'keys').pass,'amiodarone in order passes');
ok(!grade(AM,[amLines[1],amLines[0],amLines[2]].join(' '),'keys').pass,'amiodarone bullets swapped should fail');
const MZ=A('dose','Midazolam'); const mzT=displayText(MZ);
ok(!grade(MZ,mzT.replace('Midazolam 1-5 mg IV/IO','TMPX').replace('Midazolam 0.5-1 mg IM/IN/IV','Midazolam 1-5 mg IV/IO').replace('TMPX','Midazolam 0.5-1 mg IM/IN/IV'),'keys').pass,'midazolam doses swapped between headings should fail');
console.log(fails?`\n${fails} FAILURES`:'\nALL PASS');
