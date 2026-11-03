const $=(s)=>document.querySelector(s);
const form=$("#audit-form"),input=$("#issue-url"),demo=$("#demo-btn"),result=$("#result"),message=$("#message"),otari=$("#otari"),localAi=$("#local-ai"),submit=$("#submit");
function setMessage(s,bad=false){message.textContent=s;message.classList.toggle("error",bad)}
function render(data){
 result.hidden=false;
 $("#verdict").textContent=data.decision||"UNKNOWN";
 $("#verdict").style.color=data.decision==="KILL"?"#ff9d9d":data.decision==="HOLD"?"#ffca98":"#9de4c8";
 $("#reward").textContent=typeof data.advertised_amount_usd==="number"? "$"+data.advertised_amount_usd.toLocaleString("en-US"):"Not stated";
 $("#issue-title").textContent=data.title||"Untitled issue";
 for(const [selector,items] of [["#reasons",data.reasons],["#gates",data.gates]]){
  const ul=$(selector);ul.replaceChildren();
  for(const line of items||[]){const li=document.createElement("li");li.textContent=line;ul.appendChild(li);}
 }
 const modelPanel=$("#model-panel");modelPanel.hidden=!data.model_review;
 $("#model-copy").textContent=data.model_review?.summary||"";
 const source=$("#source-link");
 source.href=data.source||"https://github.com";source.textContent=data.demo?"Fictional demo (no external issue)":"Open original GitHub issue ↗";
 if(data.demo){source.removeAttribute("target");source.href="#audit-form"}
 setMessage(data.demo?"Fictional data loaded. No actual payment, issue, or submission.":"Analysis complete. Verify sponsor and existing proposals before taking any paid-work action.");
}
async function evaluate(url,useOtari,useLocalAi){
 submit.disabled=true;result.hidden=true;setMessage("Fetching official GitHub issue and applying independent checks...");
 try{
  const r=await fetch("/api/evaluate",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({url,use_otari:useOtari,use_local_ai:useLocalAi})});
  const body=await r.json();
  if(!r.ok)throw Error(body.error||"Request failed");
  render(body);
 }catch(e){setMessage(e.message||"Research unavailable",true)}
 finally{submit.disabled=false}
}
otari.addEventListener("change",()=>{if(otari.checked)localAi.checked=false});
localAi.addEventListener("change",()=>{if(localAi.checked)otari.checked=false});
form.addEventListener("submit",e=>{e.preventDefault();evaluate(input.value.trim(),otari.checked,localAi.checked)});
demo.addEventListener("click",async()=>{
 result.hidden=true;setMessage("Loading fictional controlled example...");
 try{const r=await fetch("/api/demo");if(!r.ok)throw Error("Demo error");render(await r.json())}
 catch(e){setMessage(e.message,true)}
});
fetch("/api/health").then(r=>r.json()).then(s=>{
 $("#model-status").textContent=s.otari_configured?"OTARI AVAILABLE":"RULES ENGINE READY";
 $("#otari-badge").textContent=s.otari_configured?"configured":"token not configured";
 otari.disabled=!s.otari_configured;
 $("#local-badge").textContent=s.local_ai_enabled?"ready":"server disabled";localAi.disabled=!s.local_ai_enabled;
}).catch(()=>{$("#model-status").textContent="SERVER OFFLINE";$("#otari-badge").textContent="unavailable";otari.disabled=true;localAi.disabled=true;});
