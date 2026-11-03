"use strict";
/* Source-guarded ONLY numeric/boolean game decision leaves for OWN team P0/P1.
   No inputs, no dispatch, no API, no clicking, no saved changes. */
const fs=require("fs"),path=require("path");
const d=path.join(process.env.HOME,"Downloads/ecosim-r257-evening-p1-live-readonly-20261103");
const pages=JSON.parse(fs.readFileSync(path.join(d,"R257_BROWSER_TABS_PRIVATE.json"),"utf8")).filter(p=>p.type==="page");
if(pages.length!==1||!pages[0].url.startsWith("https://edu.ecosim.hu/dashboard"))throw Error("HOLD_AUTH");
const ws=new WebSocket(pages[0].webSocketDebuggerUrl),pending=new Map();let counter=0;
ws.onmessage=e=>{let q;try{q=JSON.parse(e.data)}catch{return}const cb=pending.get(q.id);if(cb){pending.delete(q.id);cb(q)}};
function send(method,params={}){return new Promise((yes,no)=>{const n=++counter;const tt=setTimeout(()=>{pending.delete(n);no(Error("HOLD_CDP_TIMEOUT"))},13000);pending.set(n,x=>{clearTimeout(tt);yes(x)});ws.send(JSON.stringify({id:n,method,params}))})}
function readDecisionsOnly(){
 const root=document.querySelector("#root");if(!root)return{status:"NO_ROOT"};
 const k=Object.keys(root).find(x=>x.startsWith("__reactFiber$")||x.startsWith("__reactContainer$"));
 const initial=root._reactRootContainer?._internalRoot?.current||root[k];
 if(!initial)return {status:"NO_FIBER"};
 const seen=new Set(),stack=[initial];
 let count=0;
 const allowed=["institutions","publicTransport","income","projects","loans","training","communication","financing"];
 function leaf(v){
   if(v===null)return null;
   if(typeof v==="number" && Number.isFinite(v))return v;
   if(typeof v==="boolean")return v;
   if(typeof v==="string"&& /^[-+]?\d{1,12}(\.\d{1,10})?$/.test(v))return Number(v);
   return undefined;
 }
 function flatObject(v,prefix,depth,output){
   if(depth>10)return;
   const n=leaf(v);
   if(n!==undefined){output[prefix]=n;return}
   if(!v||typeof v!=="object" || Array.isArray(v))return;
   for(const key of Object.keys(v).slice(0,180)){
     if(!/^[A-Za-z][A-Za-z0-9_]*$/.test(key))continue;
     flatObject(v[key],prefix+"."+key,depth+1,output);
   }
 }
 while(stack.length&&count<40000){
  const node=stack.pop();
  if(!node||seen.has(node))continue;seen.add(node);count++;
  const p=node.memoizedProps;
  if(p&&typeof p==="object"&&p.decisionSetup&&p.teams&&typeof p.teamIndex==="number"){
    const team=p.teams[p.teamIndex];
    if(!team||team.name!=="Jutalom a nap végén"||p.selectedPeriod!==1) return {status:"HOLD_TEAM_PERIOD"};
    const x=team.decisions,vals={};
    for(const per of ["0","1"]){
      if(!x[per]||typeof x[per]!=="object")return {status:"MISSING_PERIOD_"+per};
      vals[per]={};
      for(const field of allowed)if(Object.hasOwn(x[per],field)){
        flatObject(x[per][field],field,0,vals[per]);
      }
    }
    const keys=new Set([...Object.keys(vals[0]),...Object.keys(vals[1])]);
    const diffs=[];
    for(const key of [...keys].sort()){
      if(!(key in vals[0])||!(key in vals[1])||vals[0][key]!==vals[1][key])
        diffs.push({field:key,p0:vals[0][key]??null,p1:vals[1][key]??null});
    }
    const projectNames=Object.keys(x[1].projects||{});
    const projectInfo=projectNames.map(id=>({
      id,
      p0:x[0].projects[id],
      p1:x[1].projects[id]
    })).filter(r=>typeof r.p0!=="object" && typeof r.p1!=="object");
    return {status:"FOUND_AUTH_CURRENT_OWNER_DECISIONS",
      path:location.pathname,period:1,team_match:true,team_count:p.teams.length,
      source_selected_period:p.selectedPeriod,
      scalar_leaf_count_p0:Object.keys(vals[0]).length,
      scalar_leaf_count_p1:Object.keys(vals[1]).length,
      numeric_boolean_diffs:diffs,officeHire:{
        p0:x[0].publicTransport?.hr?.office?.hire ?? null,
        p1:x[1].publicTransport?.hr?.office?.hire ?? null},
      projects:projectInfo,all_numeric_boolean_leaf_values:vals,
      saved_receipt_verified:false,game_mutations:0};
  }
  if(node.child)stack.push(node.child);
  if(node.sibling)stack.push(node.sibling);
 }
 return {status:"NO_TEAM_PROPS",nodes:count};
}
(async()=>{
 await new Promise((yes,no)=>{ws.addEventListener("open",yes,{once:true});ws.addEventListener("error",no,{once:true})});
 const r=await send("Runtime.evaluate",{expression:"("+readDecisionsOnly.toString()+")()",
    returnByValue:true,throwOnSideEffect:true,awaitPromise:false,timeout:8500});
 if(r.error||r.result?.exceptionDetails)throw Error("HOLD_READONLY_SIDE_EFFECT_GUARD");
 const v=r.result?.result?.value;
 if(!v||v.status!=="FOUND_AUTH_CURRENT_OWNER_DECISIONS")throw Error("HOLD_"+(v?.status||"INVALID"));
 if(v.scalar_leaf_count_p1<50||v.scalar_leaf_count_p0<50)throw Error("HOLD_DECISION_SCALAR_COVERAGE");
 const target=path.join(d,"R257_CURRENT_OWNER_P0_P1_DECISIONS_NUMERIC_PRIVATE.json");
 if(fs.existsSync(target))throw Error("HOLD_NO_OVERWRITE");
 fs.writeFileSync(target,JSON.stringify(v,null,2)+"\n",{mode:0o600});
 console.log(JSON.stringify({status:v.status,period:v.period,
  total_p0_numeric:v.scalar_leaf_count_p0,total_p1_numeric:v.scalar_leaf_count_p1,
  diffs:v.numeric_boolean_diffs,officeHire:v.officeHire,projects:v.projects,
  saved_receipt_verified:false,game_mutations:0}));
 ws.close();
})().catch(e=>{console.error(e.message);ws.close();process.exitCode=2});
