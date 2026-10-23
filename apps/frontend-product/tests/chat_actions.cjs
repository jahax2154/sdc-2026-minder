// Actual F server and real provider. Fictional owner; no fetch/provider mocking.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const output=process.env.MINDER_BROWSER_OUTPUT_DIR||'/private/tmp';fs.mkdirSync(output,{recursive:true});
const base=process.env.MINDER_PRODUCT_BASE_URL||'http://127.0.0.1:9106';
const {chromium}=require(process.env.MINDER_PLAYWRIGHT_MODULE||'/private/tmp/minder-c-ui-check/node_modules/playwright');
(async()=>{
 const browser=await chromium.launch({headless:true});
 const page=await browser.newPage({viewport:{width:1440,height:1000}}),errors=[],checks={};
 page.on('pageerror',e=>errors.push(e.message));
 async function api(path,body,method=body===undefined?'GET':'POST'){
  return page.evaluate(async({path,body,method})=>{const r=await fetch('/api/'+path,{method,headers:{'Content-Type':'application/json',Authorization:'Bearer '+sessionStorage.getItem('minder-product-token')},...(body===undefined?{}:{body:JSON.stringify(body)})});const v=await r.json();if(!r.ok)throw new Error(r.status+':'+v.code);return v;},{path,body,method});
 }
 async function ready(hash,selector){await page.goto(base+'/#'+hash);await page.locator(selector).waitFor();}
 try{
  await ready('minder','#minderInput');
  let p=await api('profile',{profile:{synthetic:true,timezone:'Asia/Kuala_Lumpur',career_context:{display_name:'Fictional F Test',goals:'Explore software development'},constraints:[{constraint_id:'hours',scope:'weekly_hours',hard:true,value:5,unit:'hours_per_week',evidence_id:'explicit-user'}]},expected_version:null},'PUT');
  await page.evaluate(()=>sessionStorage.setItem('minder-product-role','onet:15-1252.00'));
  await page.reload();await page.locator('#minderInput').waitFor();
  if(!process.env.MINDER_SKIP_CHAT){
  await page.locator('#minderInput').fill('Explain the available Malaysian source evidence and its limitations.');
  const waiting=page.waitForResponse(r=>r.url().endsWith('/api/chat')&&r.request().method()==='POST',{timeout:90000});
  await page.locator('#minderComposer').evaluate(f=>f.requestSubmit());
  const response=await waiting;assert.equal(response.status(),200);const answer=await response.json();
  await page.locator('.assistant-answer').waitFor();assert(answer.statements.length>0);
  assert.equal(await page.locator('.source').count()>0,answer.statements.some(s=>s.sources.length>0));
  assert(await page.locator('.source').count()>0);
  assert(answer.statements.some(s=>['published_offering_activity','occupation_shortage','sector_context'].includes(s.measurement_type)));
  assert.deepEqual(await api('profile'),p);
  checks.chat={validated_statements:answer.statements.length,sources:await page.locator('.source').count(),provider:answer.provider.status,native_arguments_validated:answer.provider.tool_call?.arguments_validated===true,measurement_types:[...new Set(answer.statements.map(s=>s.measurement_type).filter(Boolean))],no_profile_mutation:true};
  await page.screenshot({path:path.join(output,'minder-f-chat.png'),fullPage:true});
  await page.reload();await page.locator('#minderInput').waitFor();assert.equal(await page.locator('.assistant-answer').count(),0);checks.temporary_history_honest=true;
  }
  function request(after){return {kind:'update_profile',target_id:p.profile_id,expected:p.version,diff:[{path:'/constraints/hours/value',before:5,after}],reason:'Fictional browser review of weekly availability'};}
  const rejected=await api('proposals',{request:request(4)});
  await ready('mindbots','#reject-0');await page.locator('#reject-0').click();await page.getByRole('heading',{name:'Proposed change · rejected',exact:true}).waitFor();assert.deepEqual(await api('profile'),p);checks.rejection_preserves_profile=true;
  const approved=await api('proposals',{request:request(3)});
  await page.reload();await page.locator('[id^="approve-"]').waitFor();await page.locator('[id^="approve-"]').click();await page.getByRole('heading',{name:'Proposed change · applied',exact:true}).waitFor();
  p=await api('profile');assert.equal(p.constraints[0].value,3);assert.equal((await api('action-history')).history.length,1);checks.exact_approval_persists=true;
  // A repeated exact decision must return the original action, never execute twice.
  const again=await api('proposal-decision',{proposal_id:approved.preview.proposal_id,decision:'approve',preview_hash:approved.preview_hash,expected_state_version:approved.preview.request.expected_state_version});
  assert.equal((await api('action-history')).history.length,1);checks.repeat_approval_once=true;
  const stale=await api('proposals',{request:{...request(2),diff:[{path:'/constraints/hours/value',before:3,after:2}]}});
  p=await api('profile',{profile:{career_context:{goals:'Revised fictional goal'}},expected_version:p.version},'PUT');
  await page.reload();await page.locator('[id^="approve-"]').waitFor();await page.locator('[id^="approve-"]').click();await page.locator('#error').filter({hasText:/stale/}).waitFor();assert.equal((await api('profile')).constraints[0].value,3);checks.stale_visible_no_mutation=true;
  await page.locator('[id^="reject-"]').click();await page.waitForTimeout(400);
  await page.locator('#openSchedule').click();
  await page.locator('#dailySettings input[name="enabled"]').check();await page.locator('#dailySettings input[name="check_time"]').fill('09:30');await page.locator('#dailySettings button').click();await page.waitForTimeout(400);assert.equal((await api('agent-settings')).check_time,'09:30');checks.settings_persist=true;
  await page.setViewportSize({width:390,height:844});await ready('minder','#minderInput');assert(await page.locator('.mobile-menu').isVisible());await page.locator('.mobile-menu').click();assert(await page.locator('.sidebar').isVisible());await page.keyboard.press('Escape');assert(!(await page.locator('.sidebar').isVisible()));checks.mobile_navigation=true;
  await page.screenshot({path:path.join(output,'minder-f-mobile.png'),fullPage:true});
  assert.deepEqual(errors,[]);checks.page_errors=errors;
  console.log(JSON.stringify(checks,null,2));fs.writeFileSync(path.join(output,'minder-f-chat-actions.json'),JSON.stringify(checks,null,2));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1);});
