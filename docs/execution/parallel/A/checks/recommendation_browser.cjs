/* A integration acceptance: real UI forms, HTTP, SQLite and A/B source services. */
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {chromium}=require(process.env.MINDER_PLAYWRIGHT_MODULE);
(async()=>{
 const browser=await chromium.launch({headless:true});
 const page=await browser.newPage({viewport:{width:1365,height:1000}}), errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 const report={transport:'real Chromium and HTTP; no route/fetch/provider mocks',synthetic_profile:true,checks:{}};
 const api=(route,body,method=body===undefined?'GET':'POST')=>page.evaluate(async({route,body,method})=>{
  const r=await fetch('/api/'+route,{method,headers:{'Content-Type':'application/json',Authorization:'Bearer '+sessionStorage.getItem('minder-token')},...(body===undefined?{}:{body:JSON.stringify(body)})});
  if(!r.ok)throw new Error('API '+r.status);return r.json();
 },{route,body,method});
 const click=async(selector,route)=>{
  const response=page.waitForResponse(r=>r.url().endsWith('/api/'+route)&&r.request().method()!=='GET');
  await page.locator(selector).click();assert.equal((await response).status(),200);await page.waitForLoadState('networkidle');
 };
 try {
  await page.goto('http://127.0.0.1:9101/#profile');await click('#save-profile','profile');
  let p=await api('profile');p.synthetic=true;await api('profile',{profile:p,expected_version:p.version},'PUT');
  await page.reload();await page.locator('#assessed-skill').waitFor();
  const ref=await api('assessment-reference');
  const before=await api('career-context',{});assert.equal(before.recommendation.coverage.assessed,0);
  assert(before.recommendation.targeted_questions.length>0);
  report.checks.incomplete_profile_requests_focused_input='passed';
  for(const [i,sid] of Object.keys(ref.skills).sort().slice(0,3).entries()) {
   await page.locator('#assessed-skill').selectOption(sid);
   await page.locator('#assessed-level').selectOption(i===0?'2':'4');
   assert((await page.locator('#anchor-description').textContent()).length>10);
   await page.locator('#assessment-statement').fill('Fictional study project: I performed the selected source activity and can describe my contribution.');
   await click('#save-assessment','profile');
   await page.getByText(`${i+1} structured skill observations saved.`,{exact:false}).waitFor();
  }
  p=await api('profile');assert.equal(p.evidence.length,3);assert.equal(p.current_fields.length,0);
  await page.locator('a[href="#explore"]').first().click();await page.locator('#role-query').waitFor();
  const full=await api('career-context',{});report.coverage=full.recommendation.coverage;
  assert.equal(report.coverage.considered_eligible,910);assert.equal(report.coverage.assessed,910);
  assert.equal(report.coverage.current_comparable_ranked,5);assert.equal(report.coverage.personal_only_ranked,905);
  assert.equal(full.recommendation.overall_ranking_complete,false);
  assert(await page.getByRole('heading',{name:'Your recommendation coverage'}).isVisible());
  assert(await page.getByRole('heading',{name:'Exploration without comparable role-level activity'}).isVisible());
  assert.equal(report.coverage.published_offering_comparable_ranked,3);assert.equal(report.coverage.employer_comparable_ranked,2);assert.equal(report.coverage.sector_context_supported,907);
  assert(await page.getByRole('heading',{name:'Published occupation-category comparison'}).isVisible());
  report.checks.fresh_graduate_all_supported_roles_scoped_ranks_no_prior_job_or_ratings='passed';
  await page.locator('#role-query').fill('Software Developers');await click('#search-roles','roles');
  await page.locator('[data-role="onet:15-1252.00"]').click();await page.locator('#not-interested').waitFor();
  await page.getByRole('heading',{name:'Source evidence by measurement'}).waitFor();
  assert.match(await page.locator('#view').textContent(),/19,899 published job offerings/);
  const selected={selected_role_ids:['onet:15-1252.00']};const original=await api('career-context',selected);
  await click('#show-trace','role-evidence');assert.match(await page.locator('#trace-result').textContent(),/personal current|personal_and|personal and published|personal-current-evidence-v2/);
  report.checks.typed_source_units_and_owner_scoped_trace_visible='passed';
  await click('#not-interested','direct-action');let marked=await api('profile');
  const reduced=await api('career-context',selected);
  assert(Math.abs(original.recommendation.options[0].personal_score-reduced.recommendation.options[0].personal_score-5)<1e-6);
  assert.deepEqual(original.assessment_details[0].components[0],reduced.assessment_details[0].components[0]);
  await page.locator('#not-interested').click();await page.waitForLoadState('networkidle');assert.deepEqual(await api('profile'),marked);
  await click('#reset-preference','direct-action');const reset=await api('career-context',selected);
  assert.equal(reset.recommendation.options[0].personal_score,original.recommendation.options[0].personal_score);
  assert.deepEqual((await api('profile')).evidence,p.evidence);
  report.checks.not_interested_lowers_preference_only_idempotent_and_reset_restores='passed';
  await page.locator('a[href="#profile"]').first().click();await page.locator('#save-industry').waitFor();
  const role=(await api('role-requirements',{role_id:'onet:15-1252.00'})).role;
  await page.locator('#context-industry').selectOption(role.industry_mappings[0].target_id);
  await page.locator('#industry-history').selectOption('want_to_leave');
  await page.locator('#industry-background').selectOption('1');
  await page.locator('#background-statement').fill('Fictional sustained hands-on domain experience; this does not assign skill ability.');
  await page.locator('#industry-interest').selectOption('not_interested');await click('#save-industry','profile');
  const switched=await api('career-context',{});assert.equal(switched.recommendation.candidate_ids.length,910);
  const trace=(await api('career-context',selected)).assessment_details[0];
  assert(trace.industry_contributions.some(i=>i.background===1&&i.preference_utility===0));
  assert.deepEqual(trace.components[0],original.assessment_details[0].components[0]);
  report.checks.career_switcher_context_trace_and_other_industries_retained='passed';
  await page.locator('a[href="#explore"]').first().click();await page.locator('#role-query').waitFor();
  await page.setViewportSize({width:390,height:844});await page.waitForLoadState('networkidle');
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth));
  assert.deepEqual(errors,[]);report.checks.mobile_no_overflow_and_no_page_errors='passed';
  await page.screenshot({path:path.join(path.dirname(process.env.MINDER_RECOMMENDATION_EVIDENCE),'recommendation-ui.png'),fullPage:true});
  fs.writeFileSync(process.env.MINDER_RECOMMENDATION_EVIDENCE,JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify(report));
 } finally {await browser.close();}
})().catch(e=>{console.error(e.message);process.exit(1);});
