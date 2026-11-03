"use strict";
const fs=require("fs"),path=require("path");
const d=path.join(process.env.HOME,"Downloads/ecosim-r257-evening-p1-live-readonly-20261103");
const pages=JSON.parse(fs.readFileSync(path.join(d,"R257_BROWSER_TABS_PRIVATE.json"),"utf8")).filter(p=>p.type==="page");
if(pages.length!==1||!pages[0].url.startsWith("https://edu.ecosim.hu/dashboard"))throw Error("HOLD_AUTH_PAGE");
const ws=new WebSocket(pages[0].webSocketDebuggerUrl),pend=new Map();
let id=0;
ws.onmessage=e=>{let v;try{v=JSON.parse(e.data)}catch{return}const cb=pend.get(v.id);if(cb){pend.delete(v.id);cb(v)}};
function send(method,params={}){return new Promise((res,rej)=>{const k=++id;let t=setTimeout(()=>{pend.delete(k);rej(Error("CDP_TIMEOUT"))},14000);pend.set(k,m=>{clearTimeout(t);res(m)});ws.send(JSON.stringify({id:k,method,params}))})}
const sleep=t=>new Promise(r=>setTimeout(r,t));
function schemaOnly(){
 const root=document.querySelector("#root");
 if(!root)return {status:"NO_ROOT",path:location.pathname};
 const names=Object.keys(root).filter(k=>k.startsWith("__reactFiber$")||k.startsWith("__reactContainer$"));
 const candidates=[root._reactRootContainer?._internalRoot?.current,
 root._reactRootContainer?._internalRoot?.current?.child,
 root[names[0]]];
 const initial=candidates.find(v=>v&&typeof v==="object"&&v.child);
 if(!initial)return {status:"NO_FIBER",path:location.pathname};
 const stack=[initial],seen=new Set(),sample=[],matches=[];
 let count=0;
 while(stack.length&&count<40000){
  const node=stack.pop();
  if(!node||typeof node!=="object"||seen.has(node))continue;
  seen.add(node);count++;
  const p=node.memoizedProps;
  if(p&&typeof p==="object"&&p.market?.smartCityIndex&&matches.length<3){
   const keys=Object.keys(p).slice(0,55);
   const shape={keys,marketKeys:Object.keys(p.market).slice(0,50)};
   for(const k of keys){
    if(/simulation|data|round|state|team|decision|period|form|model/i.test(k)){
      const x=p[k];
      shape["schema_"+k]=x&&typeof x==="object"?Object.keys(x).slice(0,50):typeof x;
    }
   }
   matches.push(shape);
  }
  if(p&&typeof p==="object"&&sample.length<10&&Object.keys(p).some(k=>/decision/i.test(k))){
   sample.push(Object.keys(p).slice(0,35));
  }
  if(node.child)stack.push(node.child);
  if(node.sibling)stack.push(node.sibling);
 }
 return {status:"INSPECTED",path:location.pathname,nodes:count,marketPropsMatches:matches,decisionNameOnlySamples:sample};
}
(async()=>{
 await new Promise((ok,fail)=>{ws.addEventListener("open",ok,{once:true});ws.addEventListener("error",fail,{once:true})});
 const nv=await send("Page.navigate",{url:"https://edu.ecosim.hu/simulation/transport"});if(nv.error)throw Error("HOLD_NAV");
 await sleep(2100);
 const q=await send("Runtime.evaluate",{expression:"("+schemaOnly.toString()+")()",returnByValue:true,throwOnSideEffect:true,awaitPromise:false,timeout:8500});
 if(q.error||q.result?.exceptionDetails)throw Error("HOLD_SIDE_EFFECT_GUARD");
 const x=q.result?.result?.value;if(!x||x.status!=="INSPECTED"||x.path!=="/simulation/transport")throw Error("HOLD_SCHEMA");
 const out=path.join(d,"R257_REACT_SCHEMA_KEYS_ONLY_PRIVATE.json");
 if(fs.existsSync(out))throw Error("HOLD_NO_OVERWRITE");
 fs.writeFileSync(out,JSON.stringify(x,null,2)+"\n",{mode:0o600});
 console.log(JSON.stringify(x));
 ws.close();
})().catch(e=>{console.error(e.message);ws.close();process.exitCode=2});
