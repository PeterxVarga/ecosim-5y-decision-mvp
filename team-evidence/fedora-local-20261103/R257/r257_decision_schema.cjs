"use strict";
const fs=require("fs"),path=require("path");
const d=path.join(process.env.HOME,"Downloads/ecosim-r257-evening-p1-live-readonly-20261103");
const page=JSON.parse(fs.readFileSync(path.join(d,"R257_BROWSER_TABS_PRIVATE.json"),"utf8")).filter(x=>x.type==="page");
if(page.length!==1||!page[0].url.startsWith("https://edu.ecosim.hu/dashboard"))throw Error("HOLD_AUTH");
const ws=new WebSocket(page[0].webSocketDebuggerUrl),pending=new Map();let n=0;
ws.onmessage=e=>{let q;try{q=JSON.parse(e.data)}catch{return}const fn=pending.get(q.id);if(fn){pending.delete(q.id);fn(q)}};
function send(method,params={}){return new Promise((yes,no)=>{const id=++n;const time=setTimeout(()=>{pending.delete(id);no(Error("TIMEOUT"))},11000);pending.set(id,x=>{clearTimeout(time);yes(x)});ws.send(JSON.stringify({id,method,params}))})}
function read(){
 const root=document.querySelector("#root");if(!root)return{status:"NO_ROOT"};
 const k=Object.keys(root).find(x=>x.startsWith("__reactContainer$")||x.startsWith("__reactFiber$"));
 const a=root._reactRootContainer?._internalRoot?.current||root[k];
 if(!a)return {status:"NO_ROOT_FIBER"};
 const seen=new Set(),stack=[a];let count=0;
 const shape=x=>Array.isArray(x)?{type:"array",length:x.length,indices:[0,1,2,3,4,5].map(i=>({i,keys:x[i]&&typeof x[i]==="object"?Object.keys(x[i]).slice(0,40):typeof x[i]}))}:x&&typeof x==="object"?{type:"object",keys:Object.keys(x).slice(0,80)}:{type:typeof x};
 while(stack.length&&count<40000){
  const node=stack.pop();if(!node||seen.has(node))continue;seen.add(node);count++;
  const p=node.memoizedProps;
  if(p&&p.decisionSetup&&p.teams&&typeof p.teamIndex==="number"){
   const t=p.teams[p.teamIndex];
   if(!t||t.name!=="Jutalom a nap végén")return {status:"WRONG_TEAM",team_index:p.teamIndex};
   const ds=t.decisions;
   const result={status:"FOUND_CURRENT_TEAM",p1_visible_period:p.selectedPeriod,team_index:p.teamIndex,
     total_teams:p.teams.length,decisions:shape(ds)};
   for(const i of ["0","1","2","3","4","5"]){
    const v=ds[i];
    if(v&&typeof v==="object"){
      result["period_"+i]=shape(v);
      for(const k of ["institutions","publicTransport","income","projects","loans","training","communication","financing","decisions"]){
       if(k in v)result["period_"+i+"_"+k]=shape(v[k]);
      }
    }
   }
   return result;
  }
  if(node.child)stack.push(node.child);if(node.sibling)stack.push(node.sibling);
 }
 return {status:"NO_TEAM_PROPS",nodes:count};
}
(async()=>{
 await new Promise((yes,no)=>{ws.addEventListener("open",yes,{once:true});ws.addEventListener("error",no,{once:true})});
 const q=await send("Runtime.evaluate",{expression:"("+read.toString()+")()",returnByValue:true,throwOnSideEffect:true,awaitPromise:false,timeout:8500});
 if(q.error||q.result?.exceptionDetails)throw Error("HOLD_RUNTIME_SIDE_EFFECT");
 const v=q.result?.result?.value;if(!v||v.status!=="FOUND_CURRENT_TEAM")throw Error("HOLD_"+(v?.status||"UNKNOWN"));
 const output=path.join(d,"R257_DECISIONS_CURRENT_TEAM_SCHEMA_PRIVATE.json");
 if(fs.existsSync(output))throw Error("HOLD_EXISTS");
 fs.writeFileSync(output,JSON.stringify(v,null,2)+"\n",{mode:0o600});
 console.log(JSON.stringify(v));
 ws.close();
})().catch(e=>{console.error(e.message);ws.close();process.exitCode=2});
