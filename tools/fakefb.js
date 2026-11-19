// Stand-in for Firebase in tests: auth state and the "server" are kept in localStorage keys the app doesn't touch.
(function(){
  const LS=k=>{ try{ return JSON.parse(localStorage.getItem(k)||'null'); }catch(e){ return null; } };
  const W=(k,v)=>localStorage.setItem(k,JSON.stringify(v));
  let cbs=[]; const cur=()=>LS('__fakeauth');
  const fire=()=>setTimeout(()=>cbs.forEach(cb=>cb(cur())),30);
  window.FBLIB={
    initializeApp:c=>({c}), getAuth:()=>({}), getFirestore:()=>({}),
    GoogleAuthProvider:function(){ this.setCustomParameters=()=>{}; },
    onAuthStateChanged:(a,cb)=>{ cbs.push(cb); fire(); },
    getRedirectResult:()=>Promise.resolve(null),
    signInWithPopup:async()=>{ const u=window.__nextUser||{uid:'A',email:'a@example.com'}; W('__fakeauth',u); fire(); return {user:u}; },
    signInWithRedirect:async()=>{},
    signOut:async()=>{ localStorage.removeItem('__fakeauth'); fire(); },
    doc:(db,c,id)=>({path:c+'/'+id}),
    getDoc:async ref=>{ if(window.__dbDown) throw {code:'unavailable'}; let d; if(window.__srvGet){ const j=await window.__srvGet(ref.path); d=j?JSON.parse(j):null; } else d=(LS('__fakedb')||{})[ref.path]; return {exists:()=>!!d, data:()=>d}; },
    setDoc:async (ref,v)=>{ if(window.__dbDown) throw {code:'unavailable'}; if(window.__srvSet) await window.__srvSet(ref.path,JSON.stringify(v)); else { const db=LS('__fakedb')||{}; db[ref.path]=v; W('__fakedb',db); } window.__writes=(window.__writes||0)+1; }
  };
})();
