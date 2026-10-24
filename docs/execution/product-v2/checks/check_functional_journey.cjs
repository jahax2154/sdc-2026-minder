// Real initial onboarding and real saved-state/LLM journey. No seeded Profile/plan.
// Credentials stay in the private persistent browser profile, never in reports.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {chromium}=require('/private/tmp/minder-c-ui-check/node_modules/playwright');
const base=process.env.MINDER_PRODUCT_BASE_URL||'http://127.0.0.1:9111';
const output=process.env.MINDER_BROWSER_OUTPUT_DIR;assert(output);
const mode=process.env.MINDER_FUNCTIONAL_MODE||'initial';
fs.mkdirSync(output,{recursive:true});
const ROLE='onet:15-1252.00';
(async()=>{
 const browser=await chromium.launchPersistentContext(path.join(output,'browser'),{headless:true,viewport:{width:1440,height:1000}});
 const page=browser.pages()[0],errors=[],requests=[],turns=[];
 page.setDefaultTimeout(20000);
 page.on('pageerror',e=>errors.push(e.message));
 page.on('response',async r=>{if(!r.url().startsWith(base+'/api/'))return;requests.push({method:r.request().method(),path:new URL(r.url()).pathname,status:r.status()});if(r.url().endsWith('/api/product/conversation-turn')){const result=await r.json().catch(()=>null);turns.push(result);}});
 const report={base,mode,started_at:new Date().toISOString(),steps:[],page_errors:errors};
 function save(){fs.writeFileSync(path.join(output,mode+'.json'),JSON.stringify({...report,requests,provider_requests:turns.length},null,2));}
 async function api(endpoint,body,method=body===undefined?'GET':'POST'){
  return page.evaluate(async({endpoint,body,method})=>{const r=await fetch('/api/'+endpoint,{method,headers:{'Content-Type':'application/json',Authorization:'Bearer '+sessionStorage.getItem('minder-product-token')},...(body===undefined?{}:{body:JSON.stringify(body)})});const value=await r.json();if(!r.ok)throw Error(endpoint+' HTTP '+r.status);return value;},{endpoint,body,method});
 }
 async function go(route){await page.evaluate(route=>location.hash=route,route);await page.waitForFunction(route=>{const e=document.querySelector('#view');return e?.dataset.route===route&&e.dataset.rendered===route.split('/')[0];},route);}
 async function step(name,fn){try{const detail=await fn();report.steps.push({name,status:'pass',detail});}catch(e){report.steps.push({name,status:'fail',error:e.message.slice(0,600)});await page.screenshot({path:path.join(output,name.replace(/[^a-z0-9]/gi,'-')+'-failure.png'),fullPage:true}).catch(()=>{});}save();}
 try{
  await page.goto(base+'/#home');await page.locator('#homeProfile').waitFor();report.backend_revision=(await api('health')).runtime_revision;
  if(mode==='initial'){
   await step('actual fresh onboarding',async()=>{
    assert.equal((await api('plans')).plans.length,0);
    await go('profile');await page.locator('#setupNext').waitFor();
    await page.locator('[data-choice=studying]').click();await page.click('#setupNext');
    await page.locator('[data-choice=fit]').click();await page.click('#setupNext');
    await page.locator('#setup-context').fill('Fictional computer-science student exploring software work; a small bus-delay notebook project.');
    await page.locator('#setup-education').selectOption('Undergraduate degree');await page.locator('#setup-institution').fill('Fictional acceptance institute');
    await page.click('#setupNext');await page.click('#skipOptional');await page.click('#setupNext');await page.waitForURL('**/#profile/overview');await page.locator('.profile-tabs').waitFor();
    const profile=await api('profile');assert.equal(profile.evidence.length,0);assert.equal((await api('plans')).plans.length,0);
    return {ui_created:true,anchored_skills:0,optional_step_skipped:true,plans:0};
   });
   await step('incomplete profile asks focused missing evidence',async()=>{
    await go('careers/matches');const response=page.waitForResponse(r=>r.url().endsWith('/api/product/views/career-match'));await page.click('#findMatches');const result=await (await response).json();await page.locator('#refreshMatches').waitFor();
    const recommendation=result.data.recommendation;assert.equal(recommendation.coverage.assessed,0);assert(recommendation.targeted_questions.length);
    return {coverage:recommendation.coverage,targeted_questions:recommendation.targeted_questions,rendered:await page.locator('#careerMatches').innerText()};
   });
   await step('three source anchored self reports entered through UI',async()=>{
    await go('profile/skills');const ref=await api('assessment-reference'),role=await api('role-requirements',{role_id:ROLE});
    const ids=[...new Set(role.role.requirements.filter(e=>e.unit==='onet:LV'&&e.state==='known'&&ref.skills[e.subject_id]).map(e=>e.subject_id))].slice(0,3);
    const added=[];
    for(const id of ids){
     await page.locator('#anchoredEvidence').evaluate(e=>e.open=true);await page.locator('#assessed-skill').waitFor();await page.selectOption('#assessed-skill',id);
     const value=String(ref.skills[id].anchors[0].value);await page.selectOption('#assessed-level',value);await page.fill('#assessment-statement','Fictional unreviewed acceptance self-report: I practised '+ref.skills[id].label+' in a student project at the selected source activity level.');
     const response=page.waitForResponse(r=>r.request().method()==='PUT'&&r.url().endsWith('/api/profile'));await page.click('#save-assessment');assert.equal((await response).status(),200);await page.waitForFunction(()=>document.querySelector('#anchoredEvidence')&&!document.querySelector('#assessed-skill'));
     added.push({label:ref.skills[id].label,value});
    }
    assert.equal((await api('profile')).evidence.filter(e=>e.method_id===ref.skill_method_id).length,3);return {added,verified_competence:false};
   });
   await step('matching from actual newly entered evidence',async()=>{
    await go('careers/matches');const response=page.waitForResponse(r=>r.url().endsWith('/api/product/views/career-match'));const start=Date.now();await page.locator('#findMatches,#refreshMatches').first().click();const result=await (await response).json();await page.locator('#refreshMatches').waitFor();assert(result.data.recommendation.coverage.assessed>0);
    return {elapsed_ms:Date.now()-start,coverage:result.data.recommendation.coverage,ranking_groups:result.data.recommendation.ranking_groups.map(g=>({id:g.group_id,count:g.role_ids.length})),options:result.data.recommendation.options.length};
   });
   await step('CV upload extract review download through UI',async()=>{
    await go('profile/record');
    if(await page.locator('[data-record=files]').count())await page.locator('[data-record=files]').click();
    else await page.getByRole('button',{name:/CV.*resume/i}).click();
    await page.locator('#documentFile').waitFor();await page.setInputFiles('#documentFile',{name:'fictional-functional-cv.txt',mimeType:'text/plain',buffer:Buffer.from('Fictional acceptance CV. I built a small Python notebook to explore bus delays. This is self-report, not verified competence.')});
    await page.click('#uploadDocument');await page.locator('#extractDocument-0').waitFor();const before=await api('profile');
    await page.click('#extractDocument-0');await page.locator('#documentExperience').waitFor();assert.equal((await api('profile')).version,before.version);
    await page.fill('#documentExperience','Fictional reviewed CV context: student Python bus-delay notebook; six hours weekly available for practice.');await page.locator('#applyDocument button').click();await page.locator('#downloadDocument-0').waitFor();
    const download=page.waitForEvent('download');await page.click('#downloadDocument-0');assert.equal((await download).suggestedFilename(),'fictional-functional-cv.txt');
    const profile=await api('profile');assert.match(profile.career_context.experience,/Fictional reviewed CV/);assert.deepEqual(profile.evidence,before.evidence);
    return {upload:true,extract_does_not_mutate_profile:true,explicit_review:true,download:true,skill_evidence_unchanged:true};
   });
   await step('choose Software Developers through catalogue UI',async()=>{
    await go('careers/matches');await page.fill('#careerQuery','Software Developers');await page.locator('#careerSearch button').click();await page.locator('[data-open-role="'+ROLE+'"]').first().click();await page.locator('#chooseCareer').waitFor();await page.click('#chooseCareer');await page.waitForURL('**/#my-path/next');await page.locator('[data-generate-roadmap]').waitFor();
    const direction=(await api('product/direction')).direction;assert.equal(direction.role_id,ROLE);assert.equal(direction.plan_id,null);return {role_id:direction.role_id,accepted_plan:null};
   });
   await step('real Qwen generation explicit save and activate',async()=>{
    await go('my-path/next');await page.locator('[data-generate-roadmap]').waitFor();const response=page.waitForResponse(r=>r.url().endsWith('/api/product/conversation-turn'),{timeout:55000}),started=Date.now();await page.locator('[data-generate-roadmap]').click();const result=await (await response).json();
    fs.writeFileSync(path.join(output,'generation-receipt.json'),JSON.stringify(result,null,2));assert.equal(result.response.provider.status,'available');assert(result.response.generation?.advice?.stages?.length);
    await page.locator('[data-accept-draft]').waitFor();assert.equal((await api('plans')).plans.length,0);
    await page.locator('[data-accept-draft]').click();await page.locator('[data-activate-draft]').waitFor();const plans=await api('plans');assert.equal(plans.plans.length,1);assert.equal((await api('product/direction')).direction.plan_id,null);
    await page.locator('[data-activate-draft]').click();await page.getByRole('link',{name:'Open My Path',exact:true}).waitFor();
    return {elapsed_ms:Date.now()-started,model:result.response.provider.model,draft_stages:result.response.generation.advice.stages.length,accepted_tasks:plans.plans[0].tasks.length,explicit_save_and_activation:true};
   });
  }
  await step('scoped backend reads retain saved career when ID omitted',async()=>{
   const direction=(await api('product/direction')).direction,req=await api('role-requirements',{}),evidence=await api('role-evidence',{});assert.equal(req.role_selection.role_id,direction.role_id);assert.equal(evidence.role_selection.role_id,direction.role_id);return {role:req.role.label,selection_source:req.role_selection.source,source_records:req.display.source_record_count,display_skills:req.display.skill_count,forecast_status:evidence.forecast?.status,forecast_error:evidence.forecast_error};
  });
  await step('Compare source labels and distinct measures visible',async()=>{
   await go('careers/compare');const text=await page.locator('#careerBody').innerText();report.compare_observation={raw_subject_ids:/onet:element:/.test(text),has_sourced_labels:/Reading Comprehension/.test(text),has_importance:/Occupational importance/.test(text),has_activity:/Occupational activity level/.test(text)};
   assert(!report.compare_observation.raw_subject_ids);assert(report.compare_observation.has_sourced_labels);assert(report.compare_observation.has_importance&&report.compare_observation.has_activity);return report.compare_observation;
  });
  await step('four My Path tabs use same accepted plan and distinct content',async()=>{
   const before=await api('plans'),active=(await api('product/direction')).direction.plan_id;assert(active);const texts={};
   for(const tab of ['next','roadmap','skills','progress']){await go('my-path/'+tab);texts[tab]=await page.locator('#pathBody').innerText();assert.equal((await api('product/direction')).direction.plan_id,active);}
   assert.equal(new Set(Object.values(texts)).size,4);assert.deepEqual(await api('plans'),before);
   assert.match(texts.skills,/Reading Comprehension/);assert(!/onet:element:/.test(texts.skills));return {same_plan:true,distinct_tabs:4,no_regeneration:true};
  });
  await step('task completion updates actual progress without replacing roadmap',async()=>{
   const beforePlans=await api('plans'),direction=(await api('product/direction')).direction,plan=beforePlans.plans.find(p=>p.plan_id===direction.plan_id);assert(plan);
   const progressBefore=await api('product/progress');await go('my-path/next');await page.getByRole('link',{name:/Open activity/}).first().click();await page.locator('#completeActivity').waitFor();assert.match(await page.locator('#completeActivity').innerText(),/Mark activity complete/);await page.click('#completeActivity');await page.getByRole('button',{name:'Undo completion',exact:true}).waitFor();
   await go('my-path/progress');const after=await api('product/progress'),afterPlans=await api('plans'),saved=afterPlans.plans.find(p=>p.plan_id===plan.plan_id);assert.equal(after.completed_count,progressBefore.completed_count+1);assert.equal(afterPlans.plans.length,beforePlans.plans.length);assert.deepEqual(saved.tasks.map(t=>[t.task_id,t.title,t.description]),plan.tasks.map(t=>[t.task_id,t.title,t.description]));await page.reload();await page.locator('#pathBody').waitFor();assert.equal((await api('product/progress')).completed_count,after.completed_count);
   return {before:progressBefore.completed_count,after:after.completed_count,eligible:after.eligible_count,same_plan:true,same_task_definitions:true,refresh_persisted:true};
  });
  await step('Home canonical progress and next task',async()=>{
   await go('home');const overview=(await api('product/views/overview')).data;assert(overview.direction?.role_id===ROLE);await page.locator('[data-home-tab=progress]').click();const progress=await api('product/progress');assert.match(await page.locator('#homeNextContent').innerText(),new RegExp(progress.completed_count+' of '+progress.eligible_count));return {completed:progress.completed_count,eligible:progress.eligible_count,next_task:overview.next_task?.task_id||null};
  });
  report.final_revision=(await api('health')).runtime_revision;
  report.provider_metadata=turns.map(r=>({turn_status:r?.turn?.status,provider:r?.response?.provider,response_mode:r?.response?.response_mode}));save();
  console.log(JSON.stringify({base,mode,revision:report.backend_revision,steps:report.steps.map(s=>({name:s.name,status:s.status,error:s.error,detail:s.status==='pass'?s.detail:undefined})),compare:report.compare_observation,provider_requests:turns.length,page_errors:errors},null,2));
 }finally{save();await browser.close();}
})().catch(e=>{console.error(e.message);process.exitCode=1;});
