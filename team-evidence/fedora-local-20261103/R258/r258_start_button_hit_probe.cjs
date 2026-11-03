"use strict";
const fs=require("fs"),path=require("path");const d=path.join(process.env.HOME,"Downloads/ecosim-r258-sequential-A-B-ui-trial-20261103");
const tab=JSON.parse(fs.readFileSync(path.join(d,"R258_INITIAL_TABS_PRIVATE.json"))).find(x=>x.type==="page");
const ws=new WebSocket(tab.webSocketDebuggerUrl),p=new Map();let n=0;
ws.onmessage=e=>{let z;try{z=JSON.parse(e.data)}catch{return}const c=p.get(z.id);if(c){p.delete(z.id);c(z)}};
const send=(method,params={})=>new Promise((yes,no)=>{const id=++n,t=setTimeout(()=>no(Error("HOLD_TIMEOUT_"+method)),14000);p.set(id,x=>{clearTimeout(t);yes(x)});ws.send(JSON.stringify({id,method,params}))});
(async()=>{await new Promise((ok,no)=>{ws.addEventListener("open",ok,{once:true});ws.addEventListener("error",no,{once:true})});
 const e=await send("Runtime.evaluate",{expression:'[...document.querySelectorAll("div.box")].filter(x=>(x.innerText||"").startsWith("4 - "))[0]?.querySelector(\'button[title="Start"]\')',throwOnSideEffect:true,returnByValue:false,timeout:8500});
 const objectId=e.result?.result?.objectId; if(!objectId)throw Error('NO_ANCHOR');
 let a=await send("DOM.scrollIntoViewIfNeeded",{objectId});console.log("scroll",JSON.stringify(a).slice(0,1000));
 await new Promise(r=>setTimeout(r,850));a=await send("DOM.getBoxModel",{objectId});const q=a.result.model.content,x=(q[0]+q[4])/2,y=(q[1]+q[5])/2;console.log("coords",x,y);
 const hit=await send("DOM.getNodeForLocation",{x:Math.floor(x),y:Math.floor(y),includeUserAgentShadowDOM:true});console.log("hit",JSON.stringify(hit).slice(0,1100));
 if(hit.result?.backendNodeId){
  const desc=await send("DOM.describeNode",{backendNodeId:hit.result.backendNodeId,depth:1});console.log("desc",JSON.stringify(desc).slice(0,1800));
  const html=await send("DOM.getOuterHTML",{backendNodeId:hit.result.backendNodeId});console.log("html",JSON.stringify(html).slice(0,1100));
 }
 const exact=await send("DOM.describeNode",{objectId,depth:1});console.log("exact",JSON.stringify(exact).slice(0,1500));
 ws.close();
})().catch(e=>{console.error(e.stack);ws.close();process.exitCode=2});
