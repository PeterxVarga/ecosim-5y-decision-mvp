"use strict";
const fs=require("fs"),path=require("path");
const dir=path.join(process.env.HOME,"Downloads/ecosim-r258-sequential-A-B-ui-trial-20261103");
const tabs=JSON.parse(fs.readFileSync(path.join(dir,"R258_INITIAL_TABS_PRIVATE.json"),"utf8")).filter(t=>t.type==="page");
if(tabs.length!==1)throw Error("HOLD_BROWSER_TABS");
const ws=new WebSocket(tabs[0].webSocketDebuggerUrl),pending=new Map();let seq=0;
ws.onmessage=e=>{let r;try{r=JSON.parse(e.data)}catch{return}const cb=pending.get(r.id);if(cb){pending.delete(r.id);cb(r)}};
function send(method,params){return new Promise((yes,no)=>{let i=++seq,t=setTimeout(()=>{pending.delete(i);no(Error("HOLD_CDP_TIMEOUT"))},13000);pending.set(i,x=>{clearTimeout(t);yes(x)});ws.send(JSON.stringify({id:i,method,params:params||{}}))})}
function inspect(){
 const headings=[...document.querySelectorAll("h1,h2,h3,h4")].map(e=>({tag:e.tagName,text:e.innerText.slice(0,100)})).slice(0,60);
 const buttons=[...document.querySelectorAll("button")].map((b,i)=>({
 i,text:b.innerText.slice(0,110),title:b.getAttribute("title"),disabled:b.disabled,
 outerHTML:b.outerHTML.slice(0,270)})).slice(0,120);
 const text=document.body.innerText.slice(0,14000);
 const markers=["Körforgásos gazdaság mintaprojekt","Informatikai fejlesztés","Közlekedési Múzeum","Vasútfejlesztés","A Népliget megújítása"];
 const anchors=markers.map(m=>({name:m,index:text.indexOf(m),context:text.slice(Math.max(0,text.indexOf(m)-200),text.indexOf(m)+480)}));
 return {url:location.href,title:document.title,text,headings,buttons,anchors};
}
(async()=>{await new Promise((ok,no)=>{ws.addEventListener("open",ok,{once:true});ws.addEventListener("error",no,{once:true})});const a=await send("Runtime.evaluate",{expression:"("+inspect.toString()+")()",returnByValue:true,throwOnSideEffect:true,awaitPromise:false,timeout:9000});if(a.error||a.result?.exceptionDetails)throw Error("HOLD_READ_GUARD");const x=a.result?.result?.value;if(!x)throw Error("HOLD_EMPTY");const f=path.join(dir,"R258_PROJECT_UI_PREFLIGHT_PRIVATE.json");if(fs.existsSync(f))throw Error("HOLD_OVERWRITE");fs.writeFileSync(f,JSON.stringify(x,null,2)+"\n",{mode:0o600});console.log(JSON.stringify({url:x.url,headings:x.headings,buttons:x.buttons,anchors:x.anchors,textHead:x.text.slice(0,2500)}).slice(0,17000));ws.close()})().catch(e=>{console.error(e.stack);ws.close();process.exitCode=2});
