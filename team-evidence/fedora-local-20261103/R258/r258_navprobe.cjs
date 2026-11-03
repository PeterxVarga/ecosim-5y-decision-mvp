"use strict";
const fs=require("fs"),path=require("path");
const dir=path.join(process.env.HOME,"Downloads/ecosim-r258-sequential-A-B-ui-trial-20261103");
const tab=JSON.parse(fs.readFileSync(path.join(dir,"R258_INITIAL_TABS_PRIVATE.json"))).find(x=>x.type==="page");
const ws=new WebSocket(tab.webSocketDebuggerUrl),pending=new Map();let seq=0;
ws.onmessage=e=>{let r;try{r=JSON.parse(e.data)}catch{return}const f=pending.get(r.id);if(f){pending.delete(r.id);f(r)}};
function send(method,params={}){return new Promise((resolve,reject)=>{let id=++seq,t=setTimeout(()=>reject(Error("CDP_TIMEOUT")),15000);pending.set(id,x=>{clearTimeout(t);resolve(x)});ws.send(JSON.stringify({id,method,params}))})}
function probe(){return {links:[...document.querySelectorAll('a')].map(x=>({text:x.innerText.slice(0,80),href:x.getAttribute('href'),outer:x.outerHTML.slice(0,250)})).filter(x=>/summary|projects|finances|finance/i.test(x.text+' '+x.href)).slice(0,50),category:[...document.querySelectorAll('button[title]')].filter(x=>["Economic Development","Sports and Culture","Transport","Environment"].includes(x.title)).map(x=>({title:x.title,rect:{x:x.getBoundingClientRect().x,y:x.getBoundingClientRect().y,width:x.getBoundingClientRect().width,height:x.getBoundingClientRect().height}})),vw:innerWidth,vh:innerHeight}}
(async()=>{await new Promise((ok,fail)=>{ws.addEventListener('open',ok,{once:true});ws.addEventListener('error',fail,{once:true})});const r=await send('Runtime.evaluate',{expression:'('+probe.toString()+')()',returnByValue:true,throwOnSideEffect:true,awaitPromise:false,timeout:8500});if(r.error||r.result?.exceptionDetails)throw Error("HOLD_GUARD");console.log(JSON.stringify(r.result.result.value));ws.close()})().catch(e=>{console.error(e.stack);ws.close();process.exitCode=2});
