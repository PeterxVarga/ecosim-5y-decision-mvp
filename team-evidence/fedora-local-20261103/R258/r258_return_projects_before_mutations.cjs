"use strict";
// Only allowed while no Start has occurred; reload the original projects view.
const fs=require("fs"),path=require("path");
const d=path.join(process.env.HOME,"Downloads/ecosim-r258-sequential-A-B-ui-trial-20261103");
if(fs.existsSync(path.join(d,"R258_SEQUENTIAL_LIVE_UI_TRIAL_PRIVATE.json")))throw Error("HOLD_TRIAL_ALREADY_DONE");
const p=JSON.parse(fs.readFileSync(path.join(d,"R258_INITIAL_TABS_PRIVATE.json"))).find(x=>x.type==="page");
const ws=new WebSocket(p.webSocketDebuggerUrl),pend=new Map();let i=0;
ws.onmessage=e=>{let m;try{m=JSON.parse(e.data)}catch{return}let x=pend.get(m.id);if(x){pend.delete(m.id);x(m)}};
function send(method,params={}){return new Promise((yes,no)=>{let k=++i,t=setTimeout(()=>no(Error("HOLD_TIMEOUT")),15000);pend.set(k,m=>{clearTimeout(t);yes(m)});ws.send(JSON.stringify({id:k,method,params}))})}
(async()=>{await new Promise((yes,no)=>{ws.addEventListener("open",yes,{once:true});ws.addEventListener("error",no,{once:true})});
const a=await send("Page.navigate",{url:"https://edu.ecosim.hu/simulation/projects"});
if(a.error)throw Error("HOLD_NAV");
await new Promise(r=>setTimeout(r,1500));
const b=await send("Runtime.evaluate",{expression:'({path:location.pathname,head:document.body.innerText.slice(0,450)})',throwOnSideEffect:true,returnByValue:true,awaitPromise:false,timeout:8500});
if(b.error||b.result?.exceptionDetails||b.result?.result?.value?.path!=="/simulation/projects")throw Error("HOLD_RELOAD");
console.log("R258_PRETRIAL_RETURNED_TO_PROJECTS=PASS");ws.close();
})().catch(e=>{console.error(e.message);ws.close();process.exitCode=2});
