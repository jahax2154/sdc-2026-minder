// F extension of A's committed check_review_retry.cjs: exact retry while locked.
// Explicit response-loss fault injection after a REAL correction commit.
// Synthetic inputs/private local backend only. No provider or successful-response mocks.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {chromium}=require(process.env.MINDER_PLAYWRIGHT_MODULE||'/private/tmp/minder-c-ui-check/node_modules/playwright');
(async()=>{
 const output=process.env.MINDER_BROWSER_OUTPUT_DIR,base=process.env.MINDER_PRODUCT_BASE_URL;
 assert(output&&base,'Explicit isolated base/output required');fs.mkdirSync(output,{recursive:true});
 const browser=await chromium.launch({headless:true}),page=await browser.newPage(),sent=[];
 const initial='First fictional reviewed experience: wrote tests for a school project.';
 const edited='Second fictional reviewed experience: added documentation to a school project.';
 const api=(endpoint,body,method=body===undefined?'GET':'POST')=>page.evaluate(async({endpoint,body,method})=>{
  const r=await fetch('/api/'+endpoint,{method,headers:{'Content-Type':'application/json',Authorization:'Bearer '+sessionStorage.getItem('minder-product-token')},...(body===undefined?{}:{body:JSON.stringify(body)})});
  if(!r.ok)throw new Error('Fictional retry fixture API status '+r.status);return r.json();
 },{endpoint,body,method});
 const settled=()=>page.waitForFunction(()=>!document.querySelector('[data-pending=true]')&&document.querySelector('#view').getAttribute('aria-busy')==='false');
 let committedThenResponseLost=false;
 try{
  await page.goto(base+'/#profile');await page.locator('#save-profile').waitFor();
  await page.locator('#display-name').fill('Fictional uncertain review');await page.locator('#save-profile').click();await page.locator('#documentFile').waitFor();await settled();
  assert.equal((await api('product/documents')).storage.status,'available');
  await page.locator('#documentFile').setInputFiles({name:'fictional-retry.txt',mimeType:'text/plain',buffer:Buffer.from('Fictional unreviewed source. No skill assessment.')});
  await page.locator('#uploadDocument').click();await settled();await page.locator('[id^="extractDocument-"]').click();await page.locator('#documentExperience').waitFor();
  await page.route('**/api/product/intake-correction',async route=>{
   sent.push(route.request().postDataJSON());
   if(sent.length===1){const actual=await route.fetch();assert.equal(actual.status(),200);committedThenResponseLost=true;return route.abort('failed');}
   return route.continue();
  });
  await page.locator('#documentExperience').fill(initial);await page.locator('#applyDocument button').click();
  await page.locator('#error').filter({hasText:/Connection interrupted/}).waitFor();await settled();
  const afterCommit=await api('profile');assert.equal(afterCommit.career_context.experience,initial);
  const editor=page.locator('#documentExperience'),submit=page.locator('#applyDocument button');
  const canResubmit=await editor.count()>0&&await submit.count()>0&&await editor.isEditable()&&await submit.isEnabled();
  assert.equal(canResubmit,false);assert.equal(await editor.evaluate(e=>e.readOnly),true);assert(await page.locator('#reloadDocumentReview').isVisible());
  await submit.click();await settled();assert.equal(sent.length,2);assert.deepEqual(sent[1],sent[0]);
  const afterRetry=await api('profile');
  const mismatch=canResubmit&&sent.length>1&&sent[1].profile.career_context.experience!==edited;assert.equal(afterRetry.version,afterCommit.version);assert.equal(afterRetry.career_context.experience,initial);
  const report={fault_injection:true,provider_calls:0,real_first_commit:committedThenResponseLost,
   editor_and_submit_allowed_changed_text:canResubmit,correction_requests:sent.length,
   exact_retry_same_body_and_key:true,stale_review_replayed:mismatch,original_profile_version_preserved:afterCommit.version===afterRetry.version,
   no_mastery_inference:afterRetry.evidence.length===0};
  fs.writeFileSync(path.join(output,'document-review-retry.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));
  assert.equal(mismatch,false,'Editable reviewed intent must not silently resend the earlier frozen body');
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exit(1);});
