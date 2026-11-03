"use strict";
/*
 * R257 authorized read-only CDP live P1 snapshot:
 * Page.navigate on already authenticated game UI routes + Runtime.evaluate
 * of document.body.innerText ONLY under throwOnSideEffect guard.
 * No input events, mouse click, Redux, HTTP API requests, fetch, POST,
 * start/save/cancel/export, or persistent game state changes.
 */
const fs=require("fs"),path=require("path");
const out=path.join(process.env.HOME,"Downloads/ecosim-r257-evening-p1-live-readonly-20261103");
const pages=JSON.parse(fs.readFileSync(path.join(out,"R257_BROWSER_TABS_PRIVATE.json"),"utf8")).filter(p=>p.type==="page");
if(pages.length!==1 || !pages[0].url.startsWith("https://edu.ecosim.hu/dashboard"))
 throw Error("HOLD_SINGLE_OWNER_PAGE");
const ws=new WebSocket(pages[0].webSocketDebuggerUrl);
let next=1;const pending=new Map();
ws.addEventListener("message",e=>{
 let m;try{m=JSON.parse(e.data)}catch{return}
 const x=pending.get(m.id);if(!x)return;
 pending.delete(m.id);x(m);
});
function send(method,params={}){
 return new Promise((resolve,reject)=>{
  const id=next++;
  const timer=setTimeout(()=>{pending.delete(id);reject(Error("HOLD_TIMEOUT_"+method))},15000);
  pending.set(id,m=>{clearTimeout(timer);resolve(m)});
  ws.send(JSON.stringify({id,method,params}));
 });
}
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function guardedText(){
 const ans=await send("Runtime.evaluate",{
  expression:'({pathname:location.pathname, page:document.title, visible:document.body.innerText.slice(0,50000)})',
  returnByValue:true,throwOnSideEffect:true,awaitPromise:false,timeout:8000
 });
 if(ans.error||ans.result?.exceptionDetails)throw Error("HOLD_SIDE_EFFECT_GUARD_OR_RUNTIME");
 const val=ans.result?.result?.value;
 if(!val || typeof val.visible!=="string")throw Error("HOLD_EVAL_INVALID");
 return val;
}
async function main(){
 await new Promise((resolve,reject)=>{
  ws.addEventListener("open",resolve,{once:true});
  ws.addEventListener("error",()=>reject(Error("HOLD_CDP_CONNECTION")),{once:true});
 });
 const visits=[
  ["summary","https://edu.ecosim.hu/simulation/summary"],
  ["finance","https://edu.ecosim.hu/simulation/finance"],
  ["projects","https://edu.ecosim.hu/simulation/projects"],
  ["transport","https://edu.ecosim.hu/simulation/transport"]
 ];
 const results={schema:"ECOSIM_R257_CURRENT_AUTH_READONLY_P1_DOM_TEXT_V1",
   time_utc:new Date().toISOString(),
   mode:"PAGE_NAVIGATION_AND_SIDE_EFFECT_GUARDED_DOM_READ_ONLY",
   game_mutations:0,game_save_clicked:false,project_start_clicked:false,
   pages:[]};
 for(const [label,url] of visits){
  const nav=await send("Page.navigate",{url});
  if(nav.error)throw Error("HOLD_NAV_"+label);
  await sleep(1700);
  let v=await guardedText();
  for(let t=0;t<3;t++){
    if(v.visible.includes("Jutalom a nap végén") &&
       v.visible.includes("Selejtező") &&
       (label!=="summary" || !/XXXX/.test(v.visible)))break;
    await sleep(1200);v=await guardedText();
  }
  if(v.pathname!==new URL(url).pathname)throw Error("HOLD_PAGE_PATH_"+label);
  if(!v.visible.includes("Jutalom a nap végén") ||
     !v.visible.includes("Pool: I") ||
     !v.visible.includes("Selejtező") ||
     !v.visible.includes("Period:"))throw Error("HOLD_WRONG_TEAM_OR_ROUND_"+label);
  results.pages.push({label,pathname:v.pathname,visible:v.visible});
  console.log(JSON.stringify({label,chars:v.visible.length,head:v.visible.slice(0,350)}));
 }
 const file=path.join(out,"R257_LIVE_READONLY_FOUR_PAGES_PRIVATE.json");
 if(fs.existsSync(file))throw Error("HOLD_NO_OVERWRITE");
 fs.writeFileSync(file,JSON.stringify(results,null,2)+"\n",{mode:0o600});
 console.log("R257_LIVE_READONLY_PAGES_CAPTURED=PASS");
 ws.close();
}
main().catch(e=>{console.error(e.message);ws.close();process.exitCode=2;});
