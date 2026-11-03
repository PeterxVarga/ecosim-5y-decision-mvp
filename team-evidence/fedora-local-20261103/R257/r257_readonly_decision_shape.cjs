"use strict";
const fs=require("fs"),path=require("path");
const d=path.join(process.env.HOME,"Downloads/ecosim-r257-evening-p1-live-readonly-20261103");
const pages=JSON.parse(fs.readFileSync(path.join(d,"R257_BROWSER_TABS_PRIVATE.json"),"utf8")).filter(p=>p.type==="page");
if(pages.length!==1||!pages[0].url.startsWith("https://edu.ecosim.hu/dashboard"))throw Error("HOLD_AUTH");
const ws=new WebSocket(pages[0].webSocketDebuggerUrl),pends=new Map();let serial=0;
ws.onmessage=e=>{let x;try{x=JSON.parse(e.data)}catch{return}const cb=pends.get(x.id);if(cb){pends.delete(x.id);cb(x)}};
function send(method,params={}){return new Promise((yes,no)=>{const n=++serial;const timer=setTimeout(()=>{pends.delete(n);no(Error("HOLD_CDP_TIMEOUT"))},14000);pends.set(n,m=>{clearTimeout(timer);yes(m)});ws.send(JSON.stringify({id:n,method,params}))})}
function readShapes(){
 const root=document.querySelector("#root");if(!root)return {status:"NO_ROOT"};
 const k=Object.keys(root).find(x=>x.startsWith("__reactContainer$")||x.startsWith("__reactFiber$"));
 const start=root._reactRootContainer?._internalRoot?.current||root[k];
 if(!start)return {status:"NO_FIBER"};
 const seen=new Set(),stack=[start],rows=[];let n=0;
 function shape(v){
  if(Array.isArray(v))return {type:"array",length:v.length,firstKeys:v[0]&&typeof v[0]==="object"?Object.keys(v[0]).slice(0,45):undefined};
  if(v&&typeof v==="object")return {type:"object",keys:Object.keys(v).slice(0,70)};
  return {type:typeof v};
 }
 while(stack.length&&n<40000){
  const x=stack.pop();if(!x||typeof x!=="object"||seen.has(x))continue;
  seen.add(x);n++;
  const p=x.memoizedProps;
  if(p&&typeof p==="object"&&("decisionSetup" in p||"setDecision" in p)&&rows.length<10){
   const q={ownerPropKeys:Object.keys(p).slice(0,35)};
   for(const fld of ["decisionSetup","simulation","teams","teamIndex","selectedPeriod","valueObj","data","body","currentPeriod","finalPeriod"]){
    if(fld in p)q[fld]=shape(p[fld]);
   }
   const sim=p.simulation;
   if(sim&&typeof sim==="object"){
    for(const fld of ["teams","rounds","course","market","team","periods","decision","decisions","state"])
      if(fld in sim)q["simulation_"+fld]=shape(sim[fld]);
   }
   rows.push(q);
  }
  if(x.child)stack.push(x.child);
  if(x.sibling)stack.push(x.sibling);
 }
 return {status:"SCHEMA_ONLY",path:location.pathname,examined:n,rows};
}
(async()=>{
 await new Promise((ok,no)=>{ws.addEventListener("open",ok,{once:true});ws.addEventListener("error",no,{once:true})});
 const r=await send("Runtime.evaluate",{expression:"("+readShapes.toString()+")()",throwOnSideEffect:true,returnByValue:true,awaitPromise:false,timeout:9000});
 if(r.error||r.result?.exceptionDetails)throw Error("HOLD_READ_ONLY_RUNTIME");
 const x=r.result?.result?.value;
 if(!x||x.status!=="SCHEMA_ONLY")throw Error("HOLD_SCHEMA");
 const out=path.join(d,"R257_DECISION_SHAPE_KEYS_ONLY_PRIVATE.json");
 if(fs.existsSync(out))throw Error("HOLD_ALREADY_EXISTS");
 fs.writeFileSync(out,JSON.stringify(x,null,2)+"\n",{mode:0o600});
 console.log(JSON.stringify(x));
 ws.close();
})().catch(e=>{console.error(e.message);ws.close();process.exitCode=2});
