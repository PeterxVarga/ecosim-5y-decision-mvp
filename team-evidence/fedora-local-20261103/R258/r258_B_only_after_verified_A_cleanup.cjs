"use strict";
/* Bounded, owner-approved TEMPORARY UI project trials only:
   A [4,13,27,33], rollback verified -> B [4,13,21,27], rollback verified.
   NEVER Save/Export/Next Period; no game API, no Redux dispatch. All gameplay
   interaction is native CDP mouse events, gated to exact visible buttons.
   Any failure STOP, with best-effort cancel before browser shutdown.
*/
const fs=require("fs"),path=require("path");
const DIR=path.join(process.env.HOME,"Downloads/ecosim-r258-sequential-A-B-ui-trial-20261103");
const FILE=path.join(DIR,"R258_B_ONLY_LIVE_UI_TRIAL_PRIVATE.json");
if(fs.existsSync(FILE))throw Error("HOLD_PREVIOUS_TRIAL_RECEIPT_EXISTS");
const tabs=JSON.parse(fs.readFileSync(path.join(DIR,"R258_INITIAL_TABS_PRIVATE.json"),"utf8")).filter(x=>x.type==="page");
if(tabs.length!==1 || tabs[0].url!=="https://edu.ecosim.hu/simulation/projects")throw Error("HOLD_BROWSER_IDENTITY");
const ws=new WebSocket(tabs[0].webSocketDebuggerUrl),pending=new Map();
let next=0,active=[],records=[],lastChecked=null;
const uniqueNew=[4,13,21,27,33];
const category={4:"Economic Development",13:"Economic Development",
  21:"Sports and Culture",27:"Transport",33:"Environment"};
const names={4:"Circular Economy Pilot Project",13:"IT Development",
  21:"Transport Museum",27:"Railway Development",33:"Renovation of Nepliget"};
const groups=[
 {label:"A",ids:[4,13,27,33],index:"53.28",projectCash:305200,netCash:768280},
 {label:"B",ids:[4,13,21,27],index:"53.16",projectCash:139200,netCash:929332}
];
ws.onmessage=e=>{
 let m;try{m=JSON.parse(e.data)}catch{return}
 const f=pending.get(m.id);if(f){pending.delete(m.id);f(m)}
};
function send(method,params={}){
 return new Promise((yes,no)=>{
   const id=++next, timer=setTimeout(()=>{pending.delete(id);no(Error("HOLD_CDP_TIMEOUT_"+method))},13000);
   pending.set(id,m=>{clearTimeout(timer);yes(m)});
   ws.send(JSON.stringify({id,method,params}));
 });
}
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const need=(ok,message)=>{if(!ok)throw Error("HOLD_"+message)};
function readCurrent(){
 const root=document.querySelector("#root");
 const name=Object.keys(root||{}).find(x=>x.startsWith("__reactFiber$")||x.startsWith("__reactContainer$"));
 const current=root?._reactRootContainer?._internalRoot?.current||root?.[name];
 if(!current)return {status:"NO_ROOT"};
 const seen=new Set(),stack=[current];
 let visits=0;
 while(stack.length&&visits<40000){
  const n=stack.pop();
  if(!n||seen.has(n))continue;seen.add(n);visits++;
  const p=n.memoizedProps;
  if(p&&p.decisionSetup&&p.teams&&typeof p.teamIndex==="number"){
   const team=p.teams[p.teamIndex],period=p.selectedPeriod;
   if(!team||team.name!=="Jutalom a nap végén"||period!==1)return {status:"WRONG_TEAM_PERIOD"};
   const dec=team.decisions[1],p0=team.decisions[0];
   if(!dec||!p0||!dec.projects||!p0.projects)return {status:"NO_PERIOD_DECISIONS"};
   const keys=Object.keys(dec.projects);
   // React Start/Cancel changes a project flag to string "1"/"0",
   // while initial hydrated flags are numbers 1/0. Normalize ONLY
   // those two proven flag encodings for equality comparisons.
   const norm=v=>v==="0"?0:v==="1"?1:v;
   const changes=keys.filter(k=>norm(dec.projects[k])!==norm(p0.projects[k]));
   const runningOld=keys.filter(k=>norm(p0.projects[k])===1);
   const nonProject={};
   const scalar=(v)=>typeof v==="number"&&Number.isFinite(v)||typeof v==="boolean";
   function collect(node,key,depth){
    if(depth>9)return;
    if(scalar(node)){nonProject[key]=node;return}
    if(!node||typeof node!=="object"||Array.isArray(node))return;
    for(const k of Object.keys(node).slice(0,200))collect(node[k],key+"."+k,depth+1);
   }
   for(const key of ["institutions","publicTransport","income","loans","training","communication","financing"]){
     if(key in dec)collect(dec[key],key,0);
   }
   const projectValues={};
   for(const key of keys)projectValues[key]=norm(dec.projects[key]);
   return {status:"VALID",path:location.pathname,team:team.name,period,
    projectKeys:keys,originalRunning:runningOld,
    changedProjects:changes, projectValues,
    otherPolicyLeaves:nonProject,
    display:document.body.innerText.slice(0,23000)};
  }
  if(n.child)stack.push(n.child);if(n.sibling)stack.push(n.sibling);
 }
 return {status:"NO_TEAM_PROPS"};
}
async function evaluate(fun,args=[]){
 const expr="("+fun.toString()+")("+args.map(x=>JSON.stringify(x)).join(",")+")";
 const m=await send("Runtime.evaluate",{
  expression:expr,throwOnSideEffect:true,returnByValue:true,
  awaitPromise:false,timeout:9000});
 need(!m.error && !m.result?.exceptionDetails,
     "GUARDED_EVALUATION_"+(JSON.stringify(m.error||m.result?.exceptionDetails)||"NONE").slice(0,800));
 return m.result?.result?.value;
}
async function read(){
 const v=await evaluate(readCurrent);
 need(v?.status==="VALID","LIVE_OWNER_DECISION_"+(v?.status||"EMPTY"));
 need(v.period===1&&v.team==="Jutalom a nap végén","CURRENT_GAME_CONTEXT");
 need(v.projectKeys.length===35&&v.originalRunning.length===6,"PROJECT_INVENTORY");
 need(v.display.includes("Pool: I")&&v.display.includes("Period: 1/5")&&
      v.display.includes("X-Challenge 2026 Selejtező"),"LIVE_UI_ROUND_CONTEXT");
 return v;
}
function buttonFor(kind,id){
 if(kind==="category"){
  const a=[...document.querySelectorAll("button")].filter(
   b=>b.title===id && !b.disabled);
  return a.length===1?a[0]:null;
 }
 if(kind==="nav"){
  const a=[...document.querySelectorAll('a[href]')].filter(
   b=>b.getAttribute("href")==="/simulation/"+id);
  return a.length===1?a[0]:null;
 }
 const boxes=[...document.querySelectorAll("div.box")].filter(b=>{
  const s=(b.innerText||"");
  return s.startsWith(id+" - ");
 });
 if(boxes.length!==1)return null;
 const buttons=[...boxes[0].querySelectorAll("button")].filter(
  b=>!b.disabled&& b.title===kind && b.innerText.trim()===kind);
 return buttons.length===1?buttons[0]:null;
}
async function clickUI(kind,id){
 need((kind==="Start"||kind==="Cancel")?uniqueNew.includes(id):
      kind==="category"?Object.values(category).includes(id):
      kind==="nav"&&["projects","summary","finance"].includes(id),
      "ALLOWED_UI_TARGET");
 const code=buttonFor.toString();
 const r=await send("Runtime.evaluate",{
  expression:"("+code+")("+JSON.stringify(kind)+","+JSON.stringify(id)+")",
  returnByValue:false,throwOnSideEffect:true,awaitPromise:false,timeout:9000});
 need(!r.error&&!r.result?.exceptionDetails,"FIND_UI_ELEMENT_"+kind);
 const objectId=r.result?.result?.objectId;
 need(Boolean(objectId),"UI_ELEMENT_NOT_FOUND_"+kind+"_"+id);
 try{
  const sc=await send("DOM.scrollIntoViewIfNeeded",{objectId});
  need(!sc.error,"SCROLL_ELEMENT_"+kind);
  await sleep(110);
  let box=null;
  for(let attempt=0;attempt<4;attempt++){
    box=await send("DOM.getBoxModel",{objectId});
    if(!box.error&&box.result?.model?.content)break;
    const retry=await send("DOM.scrollIntoViewIfNeeded",{objectId});
    need(!retry.error,"SCROLL_RETRY_"+kind+"_"+id);
    await sleep(330);
  }
  need(!box.error&&box.result?.model?.content,
       "UI_BOX_MODEL_"+kind+"_"+id);
  const q=box.result.model.content, x=(q[0]+q[4])/2, y=(q[1]+q[5])/2;
  const viewport=await evaluate(function(){return {w:innerWidth,h:innerHeight}});
  need(x>0&&y>0&&x<viewport.w&&y<viewport.h,
       "TARGET_OUTSIDE_VIEWPORT_"+kind+"_"+id);
  const exact=await send("DOM.describeNode",{objectId,depth:1});
  need(!exact.error&&exact.result?.node,"DOM_TARGET_ATTRIBUTES_UNAVAILABLE");
  const target=exact.result.node;
  const attrs={};
  for(let i=0;i<(target.attributes||[]).length;i+=2)
     attrs[target.attributes[i]]=target.attributes[i+1];
  need(kind==="nav"
         ? target.nodeName==="A"&&attrs.href==="/simulation/"+id
         : target.nodeName==="BUTTON"&&attrs.title===
            (kind==="category"?id:kind)&&!("disabled" in attrs),
       "DOM_TARGET_ATTRIBUTES_MISMATCH_"+kind+"_"+id);
  // Chromium's DOM.getNodeForLocation fails for this app's independently
  // scrolling project region. Use an EXACT, fixed, READ-ONLY hit check on
  // the already identified element. No onclick/dispatch/fetch/Redux code.
  const pick=await send("Runtime.callFunctionOn",{
    objectId,
    functionDeclaration:
      'function(x,y,kind){const e=document.elementFromPoint(x,y);const hit=e?.closest(kind==="nav"?"a":"button");return {matches:hit===this,hitTitle:hit?.getAttribute("title"),hitText:hit?.innerText?.slice(0,80),x,y}}',
    arguments:[{value:x},{value:y},{value:kind}],
    returnByValue:true,awaitPromise:false,silent:true
  });
  need(!pick.error&&!pick.result?.exceptionDetails,"DOM_EXACT_READONLY_HIT_FAILED");
  const hit=pick.result?.result?.value;
  need(hit?.matches,"DOM_EXACT_HIT_MISMATCH_"+kind+"_"+id+":"+
       (JSON.stringify(hit)||"NO_HIT"));
  hit.actualTitle=attrs.title||null;
  hit.actualLabel=kind==="nav"?id:kind;
  const press=await send("Input.dispatchMouseEvent",{type:"mouseMoved",x,y});
  need(!press.error,"MOVE_MOUSE");
  const down=await send("Input.dispatchMouseEvent",{type:"mousePressed",x,y,button:"left",clickCount:1});
  need(!down.error,"MOUSE_PRESS");
  const up=await send("Input.dispatchMouseEvent",{type:"mouseReleased",x,y,button:"left",clickCount:1});
  need(!up.error,"MOUSE_RELEASE");
  records.push({at:new Date().toISOString(),action:kind,target:id,observedButton:hit.actualTitle||hit.actualLabel});
  console.log("UI_"+kind+"="+id);
  await sleep(kind==="nav"?850:340);
 }finally{
  await send("Runtime.releaseObject",{objectId}).catch(()=>{});
 }
}
let initial=null;
function checkPolicy(state){
 need(initial,"NO_INITIAL_BASELINE");
 need(JSON.stringify(state.otherPolicyLeaves)===JSON.stringify(initial.otherPolicyLeaves),
      "NON_PROJECT_POLICY_CHANGED");
}
function matchesNew(state,changed){
 checkPolicy(state);
 need(state.changedProjects.length===changed,"UNEXPECTED_NEW_PROJECT_COUNT_"+state.changedProjects.length+"_EXPECTED_"+changed);
 const activeStates=state.changedProjects.map(k=>state.projectValues[k]);
 need(activeStates.every(v=>v===1),"UNEXPECTED_PROJECT_MUTATION_DIRECTION");
}
function capture(label,state){
 const text=state.display;
 const result={at:new Date().toISOString(),label,path:state.path,
  newProjectCount:state.changedProjects.length,
  changedProjectKeys:[...state.changedProjects].sort(),
  pageText:text};
 records.push({at:result.at,action:"CAPTURE_"+label,
  path:state.path,count:result.newProjectCount});
 return result;
}
function numberRow(text,label){
 const lines=text.split("\n");
 const row=lines.find(x=>x.startsWith(label+"\t"));
 need(row,"MISSING_FINANCE_SCORE_ROW_"+label);
 const parts=row.split("\t").slice(1);
 need(parts.length===2,"WRONG_ROW_FORMAT_"+label);
 const number=v=>Number(v.replace(/\s/g,"").replace(",",".")),
  [p0,p1]=parts.map(number);
 need(Number.isFinite(p0)&&Number.isFinite(p1),"ROW_NUMERICAL_"+label);
 return {p0,p1};
}
async function navigate(page){
 const prev=await read();checkPolicy(prev);
 await clickUI("nav",page);
 for(let i=0;i<12;i++){
  const v=await read();
  const ready=(page==="summary"
    ? v.display.includes("SmartCity index\t51.96\t")
    : page==="finance"
      ? v.display.includes("Period net efficiency\t")
      : v.display.includes("City overview") && /\d+ - /.test(v.display));
  if(v.path==="/simulation/"+page && ready){checkPolicy(v);return v}
  await sleep(480);
 }
 throw Error("HOLD_SPA_ROUTE_"+page);
}
async function categorySelect(projectID){
 const v=await read();need(v.path==="/simulation/projects","NOT_PROJECTS_UI");
 const target=category[projectID];
 const has=await evaluate(function(id){return [...document.querySelectorAll("div.box")].some(x=>(x.innerText||"").startsWith(id+" - "))},[projectID]);
 if(!has){
  await clickUI("category",target);
  const v2=await read();need(v2.path==="/simulation/projects","CATEGORY_SWITCH_LOST_ROUTE");
 }
 const ok=await evaluate(function(id){const a=[...document.querySelectorAll("div.box")].filter(x=>(x.innerText||"").startsWith(id+" - "));return a.length===1},[projectID]);
 need(ok,"EXACT_PROJECT_NOT_VISIBLE_"+projectID);
}
async function runClick(verb,id,expected,stopRecording=false){
 await categorySelect(id);
 const before=await read();
 matchesNew(before,expected);
 await clickUI(verb,id);
 let v=null;
 for(let retry=0;retry<7;retry++){
  v=await read();
  if(v.changedProjects.length===expected+(verb==="Start"?1:-1))break;
  await sleep(250);
 }
 matchesNew(v,expected+(verb==="Start"?1:-1));
 if(stopRecording)console.log("RESTORED_PROJECT="+id);
 active=active.filter(x=>x!==id);
 if(verb==="Start")active.push(id);
}
async function validateBaseline(tag){
 let a=await navigate("summary");matchesNew(a,0);
 const summary=capture(tag+"_summary",a);
 const score=numberRow(a.display,"SmartCity index");
 need(score.p0===51.96&&score.p1===52.48,"BASELINE_SCORE_"+tag);
 a=await navigate("finance");matchesNew(a,0);
 const finance=capture(tag+"_finance",a);
 const expense=numberRow(a.display,"For projects");
 const net=numberRow(a.display,"Period net efficiency");
 const borrow=numberRow(a.display,"Borrowing");
 need(expense.p1===0&&net.p1===1051111&&borrow.p1===0,"BASELINE_FINANCE_"+tag);
 return {tag,summary,finance,score,expense,net,borrow,
  returnedToOriginalDecisions:true};
}
async function doTrial(t){
 console.log("START_TRIAL_"+t.label);
 for(let i=0;i<t.ids.length;i++)await runClick("Start",t.ids[i],i);
 let a=await navigate("summary");matchesNew(a,4);
 const sum=capture("TRIAL_"+t.label+"_summary",a);
 const score=numberRow(a.display,"SmartCity index");
 need(score.p1===Number(t.index),"INDEX_TRIAL_"+t.label+"_"+score.p1);
 a=await navigate("finance");matchesNew(a,4);
 const fin=capture("TRIAL_"+t.label+"_finance",a);
 const expense=numberRow(a.display,"For projects");
 const net=numberRow(a.display,"Period net efficiency");
 const borrow=numberRow(a.display,"Borrowing");
 need(expense.p1===t.projectCash&&net.p1===t.netCash&&borrow.p1===0,
  "CASH_OR_LOAN_TRIAL_"+t.label+":"+JSON.stringify({expense,net,borrow}));
 const evidence={label:t.label,projectIDs:t.ids,score,expense,net,borrow,
  projectKeys:[...a.changedProjects].sort(),
  summary:sum,finance:fin,saved:false};
 console.log("OBSERVED_TRIAL_"+t.label+":"+JSON.stringify({index:score.p1,projectExpense:expense.p1,periodNet:net.p1,loan:borrow.p1}));
 await navigate("projects");
 for(let i=t.ids.length-1;i>=0;i--)await runClick("Cancel",t.ids[i],i+1,true);
 const back=await validateBaseline("AFTER_"+t.label+"_ROLLBACK");
 console.log("TRIAL_"+t.label+"_ROLLBACK_BASELINE_PASS");
 return {...evidence,rollback:back};
}
async function safeCleanup(){
 if(active.length===0)return;
 console.error("BEST_EFFORT_ROLLBACK_PROJECTS="+active.join(","));
 try{
  let s=await read();
  if(s.path!=="/simulation/projects")await navigate("projects");
  for(let i=active.length-1;i>=0;i--){
   const id=active[i];if(!uniqueNew.includes(id))continue;
   try{
    await categorySelect(id);
    await clickUI("Cancel",id);
    console.error("CLEANUP_CANCELLED="+id);
   }catch(error){console.error("CLEANUP_FAILED="+id+":"+error.message)}
  }
  active=[];
  s=await read();
  console.error("CLEANUP_OBSERVED_NEW_COUNT="+s.changedProjects.length);
 }catch(error){console.error("CLEANUP_UNVERIFIED="+error.message)}
}
(async()=>{
 await new Promise((ok,fail)=>{ws.addEventListener("open",ok,{once:true});ws.addEventListener("error",fail,{once:true})});
 let result={schema:"ECOSIM_R258_B_FOLLOWUP_TO_LIVE_A_UNSAVED_UI_TRIAL_V1",
  created_utc:new Date().toISOString(),team:"Jutalom a nap végén",market:"I",period:"1/5",
  owner_scope:"TEMPORARY_START_CANCEL_PROJECTS_ONLY",
  game_save_actions:0,next_period_actions:0,direct_game_API_calls:0};
 try{
  initial=await read();
  need(initial.path==="/simulation/projects","WRONG_INITIAL_ROUTE");
  // The first failed attempt did one UI Start #4, then halted on
  // string "1" vs numeric 1 (NO SAVE). Recover precisely that one
  // identified temporary start, verifying the original project map.
  if(initial.changedProjects.length===1 &&
     initial.changedProjects[0]==="circularEconomy" &&
     initial.projectValues.circularEconomy===1){
    console.log("R258_RESTORE_PREVIOUS_SINGLE_UNSAVED_START_4");
    await categorySelect(4);
    await clickUI("Cancel",4);
    await sleep(380);
    initial=await read();
    records.push({action:"RECOVER_CANCEL_TEMPORARY_4",at:new Date().toISOString()});
  }
  need(initial.changedProjects.length===0,"NONZERO_NEW_START_AT_PREFLIGHT");
  need(initial.projectKeys.length===35&&initial.originalRunning.length===6,"INIT_INVENTORY");
  console.log("BASELINE_PROJECTS_0_ORIGINAL_6_PASS");
  result.initial=await validateBaseline("START");
  await navigate("projects");
  // A was independently observed in the earlier run; that run
  // restored all four temp projects but hit a transient box-model error.
  // B MUST start from a freshly checked original score, finance and 0 starts.
  result.A_not_repeated={status:"EARLIER_THIS_TURN_UI_OBSERVED",
    score:53.28,projectExpense:305200,periodNet:768280,loan:0,
    rollback_project_count_verified:0};
  result.B=await doTrial(groups[1]);
  result.final=await read();
  matchesNew(result.final,0);
  result.finalBaselineMatches=true;
  result.finished_utc=new Date().toISOString();
  result.records=records;
  fs.writeFileSync(FILE,JSON.stringify(result,null,2)+"\n",{mode:0o600});
  console.log("R258_B_AFTER_A_RESTORE_ROLLBACK_PASS="+FILE);
 }catch(error){
  console.error("R258_HOLD="+error.message);
  await safeCleanup();
  result.status="HOLD";
  result.error=error.message;
  result.final_utc=new Date().toISOString();
  result.records=records;
  const holdFile=path.join(DIR,"R258_HOLD_INCIDENT_PRIVATE.json");
  if(!fs.existsSync(holdFile))fs.writeFileSync(holdFile,JSON.stringify(result,null,2)+"\n",{mode:0o600});
  process.exitCode=2;
 }finally{
  ws.close();
 }
})().catch(e=>{console.error("TOP_HOLD",e.message);process.exitCode=2;ws.close()});
