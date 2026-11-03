"use strict";
const fs=require("fs"),path=require("path");const d=path.join(process.env.HOME,"Downloads/ecosim-r258-sequential-A-B-ui-trial-20261103");const tab=JSON.parse(fs.readFileSync(path.join(d,"R258_INITIAL_TABS_PRIVATE.json"))).find(x=>x.type==="page");if(!tab)throw Error("HOLD_NO_TAB");const ws=new WebSocket(tab.webSocketDebuggerUrl),pending=new Map();let seq=0;
ws.onmessage=e=>{let x;try{x=JSON.parse(e.data)}catch{return}let y=pending.get(x.id);if(y){pending.delete(x.id);y(x)}};
const send=(method,params={})=>new Promise((resolve,reject)=>{const id=++seq,t=setTimeout(()=>reject(Error("HOLD_CDP_TIMEOUT")),14000);pending.set(id,x=>{clearTimeout(t);resolve(x)});ws.send(JSON.stringify({id,method,params}))});
function probe(){
 const targets=["4 - ","13 - "];
 const all=[...document.querySelectorAll('button[title="Start"]')];
 const data=all.map((b,i)=>{
  const ancestors=[];let p=b;
  for(let depth=0;depth<11&&p;depth++,p=p.parentElement){
   const text=(p.innerText||'');
   ancestors.push({depth,tag:p.tagName,cls:p.className,chars:text.length,start:text.slice(0,115),countStart:(text.match(/\bStart\b/g)||[]).length});
  }
  const match=ancestors.find(a=>targets.some(t=>a.start.startsWith(t))&&a.countStart===1);
  return {i,match:match||null,ancestors:i<2?ancestors:undefined};
 });
 return {path:location.pathname,starts:all.length,buttons:data.slice(0,25)};
}
(async()=>{await new Promise((resolve,reject)=>{ws.addEventListener("open",resolve,{once:true});ws.addEventListener("error",reject,{once:true})});const r=await send("Runtime.evaluate",{expression:"("+probe.toString()+")()",throwOnSideEffect:true,returnByValue:true,awaitPromise:false,timeout:8500});if(r.error||r.result?.exceptionDetails)throw Error("HOLD_GUARD");const v=r.result?.result?.value;console.log(JSON.stringify(v).slice(0,17500));ws.close()})().catch(e=>{console.error(e.message);ws.close();process.exitCode=2});
