// Real initial onboarding and real saved-state/LLM journey. No seeded Profile/plan.
// Credentials stay in the private persistent browser profile, never in reports.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {chromium}=require('/private/tmp/minder-c-ui-check/node_modules/playwright');
const base=process.env.MINDER_PRODUCT_BASE_URL||'http://127.0.0.1:9111';
const output=process.env.MINDER_BROWSER_OUTPUT_DIR;assert(output);
const mode=process.env.MINDER_FUNCTIONAL_MODE||'initial';
const modelGap=Number(process.env.MINDER_ACCEPTANCE_MODEL_GAP_MS||0);assert(Number.isFinite(modelGap)&&modelGap>=0&&modelGap<=120000);
fs.mkdirSync(output,{recursive:true});
const ROLE='onet:15-1252.00';
(async()=>{
 const browser=await chromium.launchPersistentContext(path.join(output,'browser'),{headless:true,viewport:{width:1440,height:1000}});
 const page=browser.pages()[0],errors=[],requests=[],turns=[];let turnRequests=0,lastModelAt=0;
 page.setDefaultTimeout(20000);
 page.on('pageerror',e=>errors.push(e.message));
 page.on('request',r=>{if(r.url().endsWith('/api/product/conversation-turn')){turnRequests++;lastModelAt=Date.now();}});
 page.on('response',async r=>{if(!r.url().startsWith(base+'/api/'))return;requests.push({method:r.request().method(),path:new URL(r.url()).pathname,status:r.status()});if(r.url().endsWith('/api/product/conversation-turn')){const result=await r.json().catch(()=>null);turns.push(result);}});
 const report={base,mode,started_at:new Date().toISOString(),steps:[],page_errors:errors};
 function save(){fs.writeFileSync(path.join(output,mode+'.json'),JSON.stringify({...report,requests,provider_requests:turnRequests},null,2));}
 async function api(endpoint,body,method=body===undefined?'GET':'POST'){
  return page.evaluate(async({endpoint,body,method})=>{const r=await fetch('/api/'+endpoint,{method,headers:{'Content-Type':'application/json',Authorization:'Bearer '+sessionStorage.getItem('minder-product-token')},...(body===undefined?{}:{body:JSON.stringify(body)})});const value=await r.json();if(!r.ok)throw Error(endpoint+' HTTP '+r.status);return value;},{endpoint,body,method});
 }
 async function go(route){await page.evaluate(route=>location.hash=route,route);await page.waitForFunction(route=>{const e=document.querySelector('#view');return e?.dataset.route===route&&e.dataset.rendered===route.split('/')[0];},route);}
 async function step(name,fn){try{const detail=await fn();report.steps.push({name,status:'pass',detail});}catch(e){report.steps.push({name,status:'fail',error:e.message.slice(0,600)});await page.screenshot({path:path.join(output,name.replace(/[^a-z0-9]/gi,'-')+'-failure.png'),fullPage:true}).catch(()=>{});}save();}
 async function paceModel(){const wait=Math.max(0,modelGap-(Date.now()-lastModelAt));if(lastModelAt&&wait){report.acceptance_pacing_ms=modelGap;report.acceptance_waits_ms??=[];report.acceptance_waits_ms.push(wait);save();await page.waitForTimeout(wait);}}
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
   await step('ordinary confidence and project notes stay separate from anchored ability',async()=>{
    await go('profile/skills');const before=await api('profile');await page.click('#addProfileSkill');await page.locator('#skillForm [name=name]').fill('Fictional Python practice');await page.locator('#skillForm [name=level]').selectOption('Learning');await page.locator('#skillForm [type=submit]').click();await page.getByText('Fictional Python practice',{exact:true}).waitFor();
    await go('profile/record');await page.locator('#recordForm-projects [name=title]').fill('Fictional bus-delay notebook');await page.locator('#recordForm-projects [name=description]').fill('Fictional unreviewed student project description; no independent proficiency assessment.');await page.locator('#recordForm-projects [type=submit]').click();await page.getByText('Fictional bus-delay notebook',{exact:true}).waitFor();
    const after=await api('profile');assert.deepEqual(after.evidence.filter(e=>e.method_id==='minder-anchored-evidence-v1'),before.evidence.filter(e=>e.method_id==='minder-anchored-evidence-v1'));assert.equal(after.evidence.filter(e=>e.method_id==='explicit-user-statement').length,2);return {confidence_claim:true,project_note:true,anchored_evidence_unchanged:true};
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
    await page.fill('#documentExperience','Fictional reviewed CV context: student Python bus-delay notebook; six hours weekly available for practice.');
    let reviewRequests=0;await page.route('**/api/product/intake-correction',async route=>{reviewRequests++;if(reviewRequests===1){const response=await route.fetch();assert.equal(response.status(),200);return route.abort('failed');}return route.continue();});
    await page.locator('#applyDocument button').click();await page.getByRole('button',{name:'Retry this exact review',exact:true}).waitFor();assert.equal(await page.locator('#documentExperience').getAttribute('readonly'),'');const committed=await api('profile');await page.getByRole('button',{name:'Retry this exact review',exact:true}).click();await page.locator('#downloadDocument-0').waitFor();assert.equal((await api('profile')).version,committed.version);assert.equal(reviewRequests,2);await page.unroute('**/api/product/intake-correction');
    const download=page.waitForEvent('download');await page.click('#downloadDocument-0');assert.equal((await download).suggestedFilename(),'fictional-functional-cv.txt');
    const profile=await api('profile');assert.match(profile.career_context.experience,/Fictional reviewed CV/);assert.deepEqual(profile.evidence,before.evidence);
    return {upload:true,extract_does_not_mutate_profile:true,explicit_review:true,download:true,skill_evidence_unchanged:true,lost_review_response_controlled:true,exact_retry_same_profile_version:true};
   });
   await step('choose Software Developers through catalogue UI',async()=>{
    await go('careers/matches');await page.fill('#careerQuery','Software Developers');await page.locator('#careerSearch button').click();await page.locator('[data-open-role="'+ROLE+'"]').first().click();await page.locator('#chooseCareer').waitFor();
    const before=await api('profile');await page.getByRole('button',{name:'Not interested',exact:true}).click();await page.waitForFunction(()=>document.querySelector('[data-preference-status]')?.textContent.startsWith('Preference saved.'));const disliked=await api('profile');assert.equal(disliked.preferences.find(p=>p.entity_type==='role'&&p.entity_id===ROLE)?.state,'not_interested');assert.deepEqual(disliked.evidence,before.evidence);
    const history=(await api('action-history')).history.length;assert(await page.getByRole('button',{name:'Not interested',exact:true}).isDisabled());await page.getByRole('button',{name:'Not interested',exact:true}).evaluate(b=>b.click());assert.equal((await api('profile')).version,disliked.version);assert.equal((await api('action-history')).history.length,history);
    await page.getByRole('button',{name:'Reset preference',exact:true}).click();await page.waitForFunction(()=>document.querySelector('[data-preference-status]')?.textContent.startsWith('Preference saved.')&&document.querySelector('[data-career-preference=reset]')?.disabled);assert.equal((await api('profile')).preferences.filter(p=>p.entity_type==='role'&&p.entity_id===ROLE).length,0);
    await page.click('#chooseCareer');await page.waitForURL('**/#my-path/next');await page.locator('[data-generate-roadmap]').waitFor();
    const direction=(await api('product/direction')).direction;assert.equal(direction.role_id,ROLE);assert.equal(direction.plan_id,null);return {role_id:direction.role_id,accepted_plan:null,not_interested_and_reset:true,skill_evidence_unchanged:true};
   });
   await step('real Qwen generation explicit save and activate',async()=>{
    await go('my-path/next');await page.locator('[data-generate-roadmap]').waitFor();await paceModel();const response=page.waitForResponse(r=>r.url().endsWith('/api/product/conversation-turn'),{timeout:55000}),started=Date.now();await page.locator('[data-generate-roadmap]').click();const result=await (await response).json();
    fs.writeFileSync(path.join(output,'generation-receipt.json'),JSON.stringify(result,null,2));assert.equal(result.response.provider.status,'available');assert(result.response.generation?.advice?.stages?.length);
    await page.locator('[data-accept-draft]').waitFor();assert.equal((await api('plans')).plans.length,0);
    await page.locator('[data-accept-draft]').click();await page.locator('[data-activate-draft]').waitFor();const plans=await api('plans');assert.equal(plans.plans.length,1);assert.equal((await api('product/direction')).direction.plan_id,null);
    await page.locator('[data-activate-draft]').click();await page.getByRole('link',{name:'Open My Path',exact:true}).waitFor();await page.getByRole('link',{name:'Open My Path',exact:true}).click();await page.getByRole('link',{name:/Open activity/}).first().waitFor();
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
  await step('Home skill label and shared career navigation refresh',async()=>{
   await go('home');await page.locator('[data-home-tab=skills]').click();const skills=await page.locator('#homeNextContent').innerText();assert(!/onet:element:/.test(skills));assert.match(skills,/Reading Comprehension/);
   const other=(await api('roles',{query:'Accountants and Auditors',limit:1})).roles[0];assert(other);await go('careers/role/'+encodeURIComponent(other.role_id));await page.locator('#chooseCareer').waitFor();assert.equal((await api('product/direction')).direction.role_id,ROLE);
   await go('careers/outlook');assert.match(await page.locator('#careerBody').innerText(),/Software Developers/);await page.reload();await page.locator('#careerBody').waitFor();await page.waitForFunction(()=>document.querySelector('#careerBody')?.textContent.includes('Software Developers'));
   await go('careers/compare');assert.equal(await page.locator('[data-compare="0"]').inputValue(),ROLE);await go('my-path/next');assert.match(await page.locator('#pathBody').innerText(),/Software Developers/);return {home_label:true,browse_does_not_replace_direction:true,outlook_refresh:true,compare_selection:true,path_same_role:true};
  });
  if(mode==='initial'){
   await step('real Minder guidance unseen followup navigation and saved history',async()=>{
    const planBefore=await api('plans');await go('minder');await page.waitForFunction(()=>document.querySelector('#minderInput')&&!document.querySelector('#minderInput').disabled);
    await paceModel();await page.fill('#minderInput','I built a small student notebook about bus delays and have six hours each week. What concrete validation work should I do first? Please leave my saved plan unchanged.');let received=page.waitForResponse(r=>r.url().endsWith('/api/product/conversation-turn'),{timeout:55000});const firstStart=Date.now();await page.locator('#minderComposer').evaluate(f=>f.requestSubmit());const first=await (await received).json();assert.equal(first.response.provider.status,'available');assert.equal(first.response.response_mode,'generated_guidance');await page.waitForFunction(()=>!document.querySelector('#minderInput').disabled&&!document.querySelector('.thinking-row'));const firstMs=Date.now()-firstStart;
    const id=first.conversation.conversation_id;await paceModel();await page.fill('#minderInput','My routes repeat across days. How can I avoid learning the same trip twice, and what should I write down while checking it?');const sent=page.waitForRequest(r=>r.url().endsWith('/api/product/conversation-turn'));await page.locator('#minderComposer').evaluate(f=>f.requestSubmit());await sent;
    let observed=await api('product/conversation',{conversation_id:id});const pendingObserved=observed.pending_turns.length>0;await go('home');const finishBy=Date.now()+55000;
    while(observed.messages.length<4&&Date.now()<finishBy){await page.waitForTimeout(200);observed=await api('product/conversation',{conversation_id:id});}
    assert.equal(observed.messages.length,4);assert.equal(observed.messages[3].response.provider.status,'available');assert.equal(observed.messages[3].response.response_mode,'generated_guidance');const beforeRead=turnRequests;await go('minder/'+encodeURIComponent(id));await page.locator('.answer-text').nth(1).waitFor();await page.reload();await page.locator('.answer-text').nth(1).waitFor();assert.equal(turnRequests,beforeRead);assert.deepEqual(await api('plans'),planBefore);
    await page.locator('#searchMinderHistory').fill('same trip twice');await page.waitForFunction(()=>document.querySelectorAll('#minderHistoryRows .history-row').length===1);assert.equal(await page.locator('#moreMinderHistory').isVisible(),false);await page.screenshot({path:path.join(output,'real-unseen-followup.png'),fullPage:true});
    return {model:first.response.provider.model,first_ms:firstMs,pending_turn_observed_before_navigation:pendingObserved,saved_messages:4,unseen_followup:true,refresh_additional_provider_requests:0,plan_unchanged:true,real_message_content_search:true};
   });
   await step('real Mindbot own channel action persists once',async()=>{
    const profile=await api('profile'),plans=await api('plans'),history=await api('action-history'),singleton=(await api('product/mindbot-conversation')).conversation.conversation_id;
    await go('mindbots');await page.waitForFunction(()=>document.querySelector('#botInput')&&!document.querySelector('#botInput').disabled);await paceModel();await page.fill('#botInput','Please set my study availability to 6 hours per week.');const received=page.waitForResponse(r=>r.url().endsWith('/api/product/conversation-turn'),{timeout:55000});const start=Date.now();await page.locator('#botComposer').evaluate(f=>f.requestSubmit());const result=await (await received).json();assert.equal(result.response.provider.status,'available');assert.equal(result.response.action_status,'applied');await page.waitForFunction(()=>document.querySelector('#botInput')&&!document.querySelector('#botInput').disabled);const after=await api('profile');assert.equal(after.constraints.find(c=>c.scope==='weekly_hours').value,6);assert.deepEqual(after.evidence,profile.evidence);assert.deepEqual(await api('plans'),plans);assert.equal((await api('action-history')).history.length,history.history.length+1);assert.equal((await api('product/mindbot-conversation')).conversation.conversation_id,singleton);const requests=turnRequests;await page.reload();await page.locator('#botThread .answer-text').last().waitFor();assert.equal(turnRequests,requests);assert.equal((await api('action-history')).history.length,history.history.length+1);return {model:result.response.provider.model,elapsed_ms:Date.now()-start,action_status:'applied',one_action:true,same_singleton:true,skill_evidence_and_plan_unchanged:true};
   });
   await step('daily automation visible create pause resume cancel persists',async()=>{
    await go('mindbots/settings');await page.locator('#dailyAutomation').waitFor();await page.locator('#dailyAutomation [name=check_time]').fill('23:59');await page.locator('#dailyAutomation [name=timezone]').fill('Asia/Kuala_Lumpur');await page.locator('#dailyAutomation [type=submit]').click();await page.locator('[data-schedule-state=paused]').waitFor();const active=await api('agent-settings');assert.equal(active.state,'active');assert(active.next_run);
    await page.locator('[data-schedule-state=paused]').click();await page.locator('[data-schedule-state=active]').waitFor();assert.equal((await api('agent-settings')).state,'paused');await page.locator('[data-schedule-state=active]').click();await page.locator('[data-schedule-state=paused]').waitFor();await page.locator('[data-schedule-state=cancelled]').click();await page.getByRole('button',{name:'Create again',exact:true}).waitFor();const cancelled=await api('agent-settings');assert.equal(cancelled.state,'cancelled');assert.equal(cancelled.enabled,false);await page.reload();await page.locator('#dailyAutomation').waitFor();assert.equal((await api('agent-settings')).state,'cancelled');return {create:true,pause:true,resume:true,cancel:true,refresh:true,final_enabled:false,worker_execution_claimed:false};
   });
   await step('private CV deletion keeps reviewed profile',async()=>{
    await go('profile/record');if(await page.locator('[data-record=files]').count())await page.locator('[data-record=files]').click();await page.locator('#deleteDocument-0').waitFor();const before=await api('profile');await page.click('#deleteDocument-0');await page.getByText('No files uploaded yet.',{exact:true}).waitFor();assert.equal((await api('product/documents')).documents.length,0);assert.equal((await api('profile')).version,before.version);return {file_deleted:true,reviewed_profile_kept:true};
   });
  }
  report.final_revision=(await api('health')).runtime_revision;
  report.provider_metadata=turns.map(r=>({turn_status:r?.turn?.status,provider:r?.response?.provider,response_mode:r?.response?.response_mode}));save();
  console.log(JSON.stringify({base,mode,revision:report.backend_revision,steps:report.steps.map(s=>({name:s.name,status:s.status,error:s.error,detail:s.status==='pass'?s.detail:undefined})),compare:report.compare_observation,provider_requests:turnRequests,page_errors:errors},null,2));
  if(report.steps.some(s=>s.status!=='pass')||errors.length)process.exitCode=1;
 }finally{save();await browser.close();}
})().catch(e=>{console.error(e.message);process.exitCode=1;});
