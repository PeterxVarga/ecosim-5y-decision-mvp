"use strict";
const fs=require("fs"),path=require("path");
const d=path.join(process.env.HOME,"Downloads/ecosim-r258-sequential-A-B-ui-trial-20261103");
const tab=JSON.parse(fs.readFileSync(path.join(d,"R258_INITIAL_TABS_PRIVATE.json"))).find(x=>x.type==="page");
const ws=new WebSocket(tab.webSocketDebuggerUrl),p=new Map();let seq=0;
ws.onmessage=e=>{let m;try{m=JSON.parse(e.data)}catch{return}if(p.has(m.id)){const cb=p.get(m.id);p.delete(m.id);cb(m)}};
const send=(method,params)=>new Promise((yes,no)=>{const id=++seq,t=setTimeout(()=>{p.delete(id);no(Error("TIMEOUT"))},9000);p.set(id,r=>{clearTimeout(t);yes(r)});ws.send(JSON.stringify({id,method,params}))});
(async()=>{
 await new Promise((yes,no)=>{ws.addEventListener('open',yes,{once:true});ws.addEventListener('error',no,{once:true})});
 const probes=[
  ["body",'document.body.innerText.slice(0,80)'],
  ["root",'!!document.querySelector("#root")'],
  ["fiberKeys",'Object.keys(document.querySelector("#root")).filter(x=>x.startsWith("__reactFiber$")||x.startsWith("__reactContainer$")).length'],
  ["Set", '(()=>{const s=new Set();s.add(1);return s.size})()'],
  ["firstTree",'(()=>{const r=document.querySelector("#root"); const k=Object.keys(r).find(x=>x.startsWith("__reactContainer$")||x.startsWith("__reactFiber$")); const f=r._reactRootContainer?._internalRoot?.current||r[k];return !!f;})()'],
  ["firstProps",'(()=>{const r=document.querySelector("#root"); const k=Object.keys(r).find(x=>x.startsWith("__reactContainer$")||x.startsWith("__reactFiber$")); const f=r._reactRootContainer?._internalRoot?.current||r[k];return Object.keys(f.memoizedProps||{}).slice(0,15);})()'],
  ["newObject",'(()=>{const x={},a=[1,2];for(const k of a)x["a"+k]=k;return x})()'],
  ["spread",'(()=>{const x={a:1,b:2};return {...x}})()'],
  ["DOMandSet",'(()=>{const s=new Set(),r=document.querySelector("#root");s.add(r);return {n:s.size,text:document.body.innerText.slice(0,60)}})()'],
  ["elementFromPoint",'document.elementFromPoint(60,160)?.tagName'],
  ["closest",'document.elementFromPoint(60,160)?.closest("a")?.getAttribute("href")'],
  ["selector",'[...document.querySelectorAll("a[href]")].filter(x=>x.getAttribute("href")==="/simulation/summary").length'],
  ["getBoundingClientRect",'[...document.querySelectorAll("a[href]")].filter(x=>x.getAttribute("href")==="/simulation/summary")[0]?.getBoundingClientRect().x'],
  ["hitRect",'(()=>{const exact=[...document.querySelectorAll("a[href]")].filter(x=>x.getAttribute("href")==="/simulation/summary")[0]; const r=exact.getBoundingClientRect(); const x=r.x+r.width/2,y=r.y+r.height/2; return !!document.elementFromPoint(x,y)?.closest("a")===!!exact; })()'],
  ["fiberWalk",'(()=>{const r=document.querySelector("#root"); const k=Object.keys(r).find(x=>x.startsWith("__reactContainer$")||x.startsWith("__reactFiber$")); const f=r._reactRootContainer?._internalRoot?.current||r[k];const seen=new Set(),stack=[f];let n=0;while(stack.length&&n<40000){const v=stack.pop();if(!v||seen.has(v))continue;seen.add(v);n++;if(v.memoizedProps?.decisionSetup&&v.memoizedProps?.teams)return {n,found:1};if(v.child)stack.push(v.child);if(v.sibling)stack.push(v.sibling)}return {n,found:0}})()']
 ];
 for(const [name,expression] of probes){
  const q=await send('Runtime.evaluate',{expression,throwOnSideEffect:true,returnByValue:true,awaitPromise:false,timeout:8000});
  console.log(name, q.error?JSON.stringify(q.error): q.result?.exceptionDetails?.exception?.description || JSON.stringify(q.result?.result?.value).slice(0,300));
 }
 ws.close();
})().catch(e=>{console.error(e.stack);ws.close();process.exitCode=2});
