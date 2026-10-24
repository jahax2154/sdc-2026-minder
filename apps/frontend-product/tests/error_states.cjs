// Explicitly intercepted error/envelope fixtures. Not live-provider evidence.
const assert=require('node:assert/strict');
const {chromium}=require(process.env.MINDER_PLAYWRIGHT_MODULE||'/private/tmp/minder-c-ui-check/node_modules/playwright');
(async()=>{
 const browser=await chromium.launch({headless:true});const page=await browser.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
 try{
  await page.goto((process.env.MINDER_PRODUCT_BASE_URL||'http://127.0.0.1:9106')+'/#minder');await page.locator('#minderInput').waitFor();
  await page.evaluate(async()=>{const r=await fetch('/api/profile',{method:'PUT',headers:{'Content-Type':'application/json',Authorization:'Bearer '+sessionStorage.getItem('minder-product-token')},body:JSON.stringify({profile:{synthetic:true,timezone:'Asia/Kuala_Lumpur'},expected_version:null})});if(!r.ok)throw new Error('Fictional profile seed failed');});
  await page.reload();await page.locator('#minderInput').waitFor();let calls=0,mode='500';
  const profile=await page.evaluate(async()=>await (await fetch('/api/profile',{headers:{Authorization:'Bearer '+sessionStorage.getItem('minder-product-token')}})).json());
  await page.route('**/api/chat',async route=>{
   calls++;await new Promise(r=>setTimeout(r,100));
   if(mode==='500')return route.fulfill({status:500,json:{code:'fixture_error',request_id:'fixture'}});
   if(mode==='malformed')return route.fulfill({status:200,json:{statements:[{text:'UNVALIDATED FIXTURE'}],provider:{status:'available'}}});
   return route.fulfill({status:200,json:{statements:[{id:'fixture',evidence_ids:[],category:'limitation',text:'<img src=x onerror="window.injected=true"> Explicit rendering fixture',sources:[{source_id:'fixture-source',uri:'javascript:window.injected=true',sha256:'0'.repeat(64),version:'fixture',geography:'MY',available_at:'2026-10-23T00:00:00Z',evidence_type:'explicit-user'}]}],provider:{status:'unavailable'},integration_mode:'explicit_browser_fixture',context_version:'fixture',profile_version:profile.version,behaviour_policy_version:'minder-grounding-privacy-v1',action_status:'no_mutation_requested_or_executed'}});
  });
  await page.locator('#minderInput').fill('Explicit failure-state fixture');await page.locator('#minderComposer').evaluate(f=>{f.requestSubmit();f.requestSubmit();});await page.locator('.assistant-answer').filter({hasText:/could not/}).waitFor();assert.equal(calls,1);
  mode='malformed';await page.locator('#minderInput').fill('Malformed fixture');await page.locator('#minderComposer').evaluate(f=>f.requestSubmit());await page.locator('.assistant-answer').filter({hasText:/could not be validated/}).waitFor();assert.equal(await page.getByText('UNVALIDATED FIXTURE',{exact:true}).count(),0);
  mode='safe';await page.locator('#minderInput').fill('Escaping fixture');await page.locator('#minderComposer').evaluate(f=>f.requestSubmit());await page.locator('.assistant-answer').filter({hasText:/Explicit rendering fixture/}).waitFor();assert.equal(await page.locator('.assistant-answer img').count(),0);assert.equal(await page.locator('.assistant-answer a[href^="javascript"]').count(),0);assert.equal(await page.evaluate(()=>window.injected===true),false);assert.equal(calls,3);assert.deepEqual(errors,[]);
  console.log(JSON.stringify({fixture_only:true,provider_calls:0,duplicate_pending_blocked:true,server_error_visible:true,malformed_answer_blocked:true,html_escaped:true,unsafe_source_link_blocked:true,page_errors:errors}));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1);});
