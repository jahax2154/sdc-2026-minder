// Real pre-repair browser/API measurements. Only synthetic input/owner; no tokens logged.
const {chromium}=require(process.env.MINDER_PLAYWRIGHT_MODULE||'/private/tmp/minder-c-ui-check/node_modules/playwright');
const fs=require('node:fs');
const base=process.env.MINDER_PRODUCT_BASE_URL||'http://127.0.0.1:9106';
(async()=>{
 const browser=await chromium.launch({headless:true}),page=await browser.newPage({viewport:{width:1440,height:1000}});
 const out={frontend_revision:'29281ec907ef031c1ec07be27c84e25aad69969e',url:base,synthetic:true,samples:[],waterfall:[]},starts=new Map();
 page.on('request',r=>{if(new URL(r.url()).pathname.startsWith('/api/'))starts.set(r,performance.now());});
 page.on('response',r=>{if(starts.has(r.request()))out.waterfall.push({path:new URL(r.url()).pathname,method:r.request().method(),status:r.status(),duration_ms:Math.round(performance.now()-starts.get(r.request()))});});
 const api=(route,body,method=body===undefined?'GET':'POST')=>page.evaluate(async({route,body,method})=>{const r=await fetch('/api/'+route,{method,headers:{'Content-Type':'application/json',Authorization:'Bearer '+sessionStorage.getItem('minder-product-token')},...(body===undefined?{}:{body:JSON.stringify(body)})});return {status:r.status,body:await r.json()};},{route,body,method});
 try{
  await page.goto(base+'/#minder');await page.locator('#minderInput').waitFor();
  await page.locator('#minderInput').fill('How can u help me minder?');await page.locator('#minderComposer').evaluate(f=>f.requestSubmit());
  out.unsaved_profile={chat_requests:out.waterfall.filter(r=>r.path==='/api/chat').length,message:await page.locator('#error').innerText()};
  await api('profile',{profile:{synthetic:true,timezone:'Asia/Kuala_Lumpur',evidence:[],preferences:[],constraints:[],current_fields:[]},expected_version:null},'PUT');
  await page.reload();await page.locator('#minderInput').waitFor();
  for(let i=0;i<2;i++){
   const start=performance.now();await page.locator('#minderInput').fill('How can u help me minder?');
   const waiting=page.waitForResponse(r=>r.url().endsWith('/api/chat')&&r.request().method()==='POST',{timeout:120000});
   await page.locator('#minderComposer').evaluate(f=>f.requestSubmit());
   if(i===1){await page.locator('a[href="#mindbots"]').first().click();}
   const response=await waiting,result=await response.json();
   const sample={case:i?'mindbots_during_chat':'empty_evidence_profile',request:{path:'/api/chat',body:JSON.parse(response.request().postData())},response_status:response.status(),elapsed_ms:Math.round(performance.now()-start),response:{...result,provider:{status:result.provider?.status,reason:result.provider?.reason,tool_call:{arguments_validated:result.provider?.tool_call?.arguments_validated}},response_mode:result.response_mode??null}};
   if(i===1){await page.locator('#openSchedule').waitFor({timeout:120000});sample.mindbots_usable_ms= Math.round(performance.now()-start);}
   else {await page.locator('.assistant-answer').waitFor();sample.rendered_text=await page.locator('.assistant-answer').last().innerText();await page.screenshot({path:'/private/tmp/minder-f-repair-before-chat.png',fullPage:true});}
   out.samples.push(sample);
  }
  for(let i=0;i<2;i++){
   await page.goto(base+'/#minder');await page.locator('#minderInput').waitFor();const start=performance.now();await page.locator('a[href="#mindbots"]').first().click();await page.locator('#openSchedule').waitFor({timeout:120000});out.samples.push({case:i?'mindbots_warm':'mindbots_initial',elapsed_ms:Math.round(performance.now()-start)});
  }
  fs.writeFileSync('docs/execution/product-v2/F/repairs/baseline.json',JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify(out,null,2));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1);});
