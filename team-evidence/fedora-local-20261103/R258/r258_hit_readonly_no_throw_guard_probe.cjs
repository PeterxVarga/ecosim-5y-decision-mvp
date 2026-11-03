"use strict";
const fs=require("fs"),path=require("path");
const d=path.join(process.env.HOME,"Downloads/ecosim-r258-sequential-A-B-ui-trial-20261103");
const tab=JSON.parse(fs.readFileSync(path.join(d,"R258_INITIAL_TABS_PRIVATE.json"))).find(x=>x.type==="page");
const ws=new WebSocket(tab.webSocketDebuggerUrl),p=new Map();let n=0;
ws.onmessage=e=>{let q;try{q=JSON.parse(e.data)}catch{return}let cb=p.get(q.id);if(cb){p.delete(q.id);cb(q)}};
function send(method,params={}){return new Promise((ok,err)=>{let i=++n,t=setTimeout(()=>err(Error("HOLD_TIMEOUT")),14000);p.set(i,q=>{clearTimeout(t);ok(q)});ws.send(JSON.stringify({id:i,method,params}))})}
(async()=>{await new Promise((ok,err)=>{ws.addEventListener("open",ok,{once:true});ws.addEventListener("error",err,{once:true})});
 const expression='(()=>{const x=345.99827575683594,y=425.295166015625;const e=document.elementFromPoint(x,y);return {path:location.pathname,element:e?.outerHTML.slice(0,500),button:e?.closest("button")?.outerHTML.slice(0,500),x,y}})()';
 const r=await send("Runtime.evaluate",{expression,returnByValue:true,awaitPromise:false,timeout:8500});
 if(r.error||r.result?.exceptionDetails)throw Error("HOLD_READONLY_HIT");
 console.log(JSON.stringify(r.result?.result?.value));ws.close()
})().catch(e=>{console.error(e.stack);ws.close();process.exitCode=2});
