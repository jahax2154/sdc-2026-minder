// Extend F's committed real-intake runner in memory; never edit its files/assertions.
// Authentication stays inside live browser contexts. No session/storage export.
const fs=require('node:fs'),path=require('node:path'),Module=require('node:module'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'../../../..');
const output=process.env.MINDER_BROWSER_OUTPUT_DIR;assert(output);fs.mkdirSync(output,{recursive:true});
const base=process.env.MINDER_PRODUCT_BASE_URL||'http://127.0.0.1:9111';
const trace={base,started_at:new Date().toISOString(),cross_chat:[],market:[],persistence:null};
const write=()=>fs.writeFileSync(path.join(output,'combined.json'),JSON.stringify(trace,null,2));
async function route(page,hash){await page.evaluate(hash=>location.hash=hash,hash);await page.waitForSelector(`#view[data-route="${hash}"][data-rendered="${hash.split('/')[0]}"]`);}
async function send(page,message){await page.waitForFunction(()=>document.querySelector('#minderInput')&&!document.querySelector('#minderInput').disabled);await page.fill('#minderInput',message);const pending=page.waitForResponse(r=>r.url().endsWith('/api/product/conversation-turn'),{timeout:60000});const start=Date.now();await page.locator('#minderComposer').evaluate(f=>f.requestSubmit());const http=await pending,value=await http.json();await page.waitForFunction(()=>document.querySelector('#minderInput')&&!document.querySelector('#minderInput').disabled);return {value,http_status:http.status(),request_path:new URL(http.url()).pathname,request:http.request().postDataJSON(),elapsed_ms:Date.now()-start};}

global.__minderCrossChat=async({page,browser,evidence,api})=>{
 trace.backend_revision=evidence.backend_revision;trace.frontend_revision='0c74362344cc9a85044072b0b59085309f9744cf';
 const active=(await api(page,'product/direction')).direction,initial=(await api(page,'plans')).plans.find(p=>p.plan_id===active.plan_id);
 const task=initial.tasks.find(t=>t.state==='proposed');assert(task);
 const botBefore=await api(page,'product/mindbot-conversation');
 for(const [index,decision] of [[0,'reject'],[1,'approve']]){
  await route(page,'minder');const before=await api(page,'plans'),audits=(await api(page,'action-history')).history.length;
  const message=`Please reschedule ${task.title} to 2026-12-03T15:00:00+08:00.`;
  const sent=await send(page,message),response=sent.value.response;
  const row={decision,elapsed_ms:sent.elapsed_ms,provider:response.provider,action_status:response.action_status,status:'started'};trace.cross_chat.push(row);write();
  assert.equal(response.provider.status,'available');assert.equal(response.action_status,'approval_required');assert.equal(new URL(page.url()).hash.split('/')[0],'#minder');
  assert.deepEqual(await api(page,'plans'),before);
  const event=(await api(page,'product/minder-handoffs')).events.find(e=>e.event_id===response.diagnostics.handoff.event_id);assert(event);assert.equal(event.status,'pending');assert.equal(event.source_message_id,sent.value.messages[0].message_id);
  const bot=await api(page,'product/mindbot-conversation');assert.equal(bot.conversation.conversation_id,botBefore.conversation.conversation_id);assert.equal(bot.messages.filter(m=>m.message_id===event.mindbot_message_id).length,1);
  const replay=await api(page,'product/conversation-turn',sent.request);assert.deepEqual(replay.response,response);assert.equal((await api(page,'product/mindbot-conversation')).messages.length,bot.messages.length);
  await route(page,'mindbots');await page.locator('#openActivity').click();await page.locator('#botProposals[data-state=ready]').waitFor();
  const selected=page.locator('#botProposals').getByRole('button',{name:decision==='approve'?'Approve this exact change':'Reject',exact:true});assert.equal(await selected.count(),1);
  const receipt=page.waitForResponse(r=>r.url().endsWith('/api/proposal-decision'));await selected.click();const http=await receipt,result=await http.json();assert.equal(http.status(),200);await page.waitForFunction(()=>document.querySelector('#botProposals')?.dataset.state==='ready');
  const saved=await api(page,'plans'),after=(await api(page,'action-history')).history.length;
  if(decision==='reject'){assert.equal(result.target_changed,false);assert.deepEqual(saved,before);assert.equal(after,audits);}
  else{assert.equal(after,audits+1);const updated=saved.plans.find(p=>p.plan_id===active.plan_id).tasks.find(t=>t.task_id===task.task_id);assert.equal(updated.scheduled_at,'2026-12-03T15:00:00+08:00');assert.equal(updated.state,'scheduled');const again=await api(page,'proposal-decision',http.request().postDataJSON());assert.deepEqual(again,result);assert.deepEqual(await api(page,'plans'),saved);assert.equal((await api(page,'action-history')).history.length,after);}
  const final=(await api(page,'product/minder-handoffs')).events.find(e=>e.event_id===event.event_id);assert.equal(final.status,decision==='approve'?'approved':'rejected');
  if(decision==='approve'){
   await route(page,'my-path/task/'+encodeURIComponent(task.task_id));await page.waitForSelector('.canonical-task-controls');
   assert((await page.locator('.canonical-task-controls').innerText()).includes('Current schedule: 2026-12-03T15:00:00+08:00'));
   await page.reload();await page.waitForSelector('.canonical-task-controls');assert((await page.locator('.canonical-task-controls').innerText()).includes('Current schedule: 2026-12-03T15:00:00+08:00'));
   row.explore_saved_schedule_visible_after_refresh=true;
  }
  row.status='passed';row.event_id=event.event_id;row.one_corresponding_message=true;row.exact_turn_replay_no_duplicate=true;row.target_changed=decision==='approve';row.saved_outcome=result;write();
 }
 trace.primary={plan_id:active.plan_id,profile_evidence_count:(await api(page,'profile')).evidence.length,progress:await api(page,'product/progress'),bot_conversation_id:botBefore.conversation.conversation_id,mindbot_messages:(await api(page,'product/mindbot-conversation')).messages.length};write();
};

global.__minderMarketAndRestart=async({browser,page,evidence,api})=>{
 trace.backend_revision??=evidence.backend_revision;trace.frontend_revision='0c74362344cc9a85044072b0b59085309f9744cf';
 const market=await browser.newPage({viewport:{width:1440,height:1000}});market.setDefaultTimeout(20000);
 const cases=['What are the market trends right now?', 'How is the software engineering job market now?', "What's the most relevant skills now to become a software engineer?"];const chosen=Number(process.env.MINDER_MARKET_CASE||0);const questions=chosen?cases.slice(chosen-1,chosen):cases;
 try{
  await market.goto(base+'/#minder');await market.waitForFunction(()=>document.querySelector('#minderInput')&&!document.querySelector('#minderInput').disabled);
  assert.equal((await api(market,'plans')).plans.length,0);
  for(let index=0;index<questions.length;index++){
   const question=questions[index];let row={question,status:'started'};trace.market.push(row);write();
   try{
    if(index)await market.waitForTimeout(2000);
    const sent=await send(market,question),response=sent.value.response;row.http_status=sent.http_status;row.request_path=sent.request_path;row.elapsed_ms=sent.elapsed_ms;row.response=response;
    const displayed=await market.locator('#minderThread .assistant-answer').last().innerText();row.displayed_answer=displayed;
    const retrieval=response.diagnostics?.retrieval;assert(retrieval);assert.equal(retrieval.stored_dataset_used,false);assert(retrieval.discovery.length);assert(retrieval.fetched_pages.length);
    assert.equal((await api(market,'plans')).plans.length,0);
    const reply=market.locator('#minderThread .assistant-answer').last();await reply.locator('details').evaluateAll(ds=>ds.forEach(d=>d.open=true));
    const links=await reply.locator('.source a').evaluateAll(as=>as.map(a=>a.href));row.rendered_source_links=links;assert(links.length);assert(response.sources.every(s=>links.includes(s.uri)));
    const titles=await reply.locator('.source summary').allTextContents();row.rendered_source_titles=titles;assert(response.sources.every(s=>titles.includes(s.title)));
    row.status=response.provider.status==='available'?'answered':'blocked';
    row.data_limit=retrieval.mode!=='search_and_fetch'?'No eligible search-discovered page was fetched; predefined official context is explicit.':'Global professional context is not proof of Malaysian role demand.';
    if(response.provider.status==='available'){
     assert(response.answer.length>100);assert(response.statements.length||response.answer.includes('Practical advice'));
     assert(displayed.includes(response.answer.split('\n')[0]));
     if(question===cases[0]){assert(/unemployment|participation|labour force|employed persons/i.test(response.answer));assert(/2026|August|Aug/i.test(response.answer));}
     if(question===cases[1]){assert(/software/i.test(response.answer));assert(/backend|frontend|full.stack|modernis|applications|systems/i.test(response.answer));}
     if(question===cases[2])assert(/programming|testing|validation|requirements|version control|HTML|JavaScript|debug/i.test(response.answer));
     row.direct_question_relevance_assertions_passed=true;
    }
    await market.screenshot({path:path.join(output,`market-${index+1}.png`),fullPage:true});
   }catch(error){row.status='failed';row.error=error.message;}
   write();
  }
  // No profile was created for any general-market question.
  const missingProfile=await market.evaluate(async()=>{const r=await fetch('/api/profile',{headers:{Authorization:'Bearer '+sessionStorage.getItem('minder-product-token')}});return r.status;});assert.equal(missingProfile,404);trace.market_profile_created=false;
  await market.reload();await market.waitForFunction(()=>document.querySelector('#minderInput')&&!document.querySelector('#minderInput').disabled);trace.market_history_survives_refresh=await market.locator('#minderThread .assistant-answer').count()===questions.length;write();
  if(trace.primary){
   fs.writeFileSync(path.join(output,'ready-for-restart.json'),JSON.stringify({backend_revision:trace.backend_revision,primary_plan:trace.primary.plan_id}));
   const until=Date.now()+180000;while(!fs.existsSync(path.join(output,'restart-done.json'))&&Date.now()<until)await page.waitForTimeout(200);
   assert(fs.existsSync(path.join(output,'restart-done.json')),'A-only restart was not signalled');
   await route(page,'my-path/progress');await page.reload();await page.waitForSelector('#pathBody');const progress=await api(page,'product/progress');assert.equal(progress.plan_id,trace.primary.plan_id);assert.equal(progress.completed_count,trace.primary.progress.completed_count);
   assert.equal((await api(page,'product/mindbot-conversation')).conversation.conversation_id,trace.primary.bot_conversation_id);assert.equal((await api(page,'product/mindbot-conversation')).messages.length,trace.primary.mindbot_messages);
   const events=(await api(page,'product/minder-handoffs')).events;assert(events.some(e=>e.status==='approved'));assert(events.some(e=>e.status==='rejected'));
   await market.reload();await market.waitForFunction(()=>document.querySelector('#minderInput')&&!document.querySelector('#minderInput').disabled);assert.equal(await market.locator('#minderThread .assistant-answer').count(),questions.length);
   trace.persistence={status:'passed',backend_revision:(await api(page,'health')).runtime_revision,same_plan:true,same_progress:true,same_singleton_and_notice_count:true,approved_rejected_proposals_retained:true,unprofiled_market_history_retained:true};
  }
 }catch(error){trace.additional_failure=error.message;}finally{trace.market_answer_gate=trace.market.length===questions.length&&trace.market.every(r=>r.status==='answered'&&r.direct_question_relevance_assertions_passed)&&!trace.additional_failure?'passed':'failed';write();await market.close();}
};

const filename=path.join(root,'apps/frontend-product/tests/starter_journey.cjs');let source=fs.readFileSync(filename,'utf8');
const marker='evidence.requests=requests;record();console.log(JSON.stringify(evidence,null,2));';assert(source.includes(marker));
source=source.replace(marker,'evidence.requests=requests;record();await global.__minderCrossChat({page,browser,evidence,api});console.log(JSON.stringify(evidence,null,2));');
const closing='finally{await browser.close();}';assert(source.includes(closing));source=source.replace(closing,'finally{await global.__minderMarketAndRestart({browser,page,evidence,api});await browser.close();}');
if(process.env.MINDER_MARKET_ONLY==='1'){
 (async()=>{const {chromium}=require(process.env.MINDER_PLAYWRIGHT_MODULE);const browser=await chromium.launch({headless:true});const page=await browser.newPage();
 const api=async(p,endpoint,body,method)=>p.evaluate(async({endpoint,body,method})=>{const response=await fetch('/api/'+endpoint,{method:method||(body?'POST':'GET'),headers:{Authorization:'Bearer '+sessionStorage.getItem('minder-product-token'),'Content-Type':'application/json'},body:body?JSON.stringify(body):undefined});const value=await response.json();if(!response.ok)throw new Error(endpoint+': '+response.status);return value;},{endpoint,body,method});
 try{await page.goto(base+'/#minder');await page.waitForSelector('#minderInput');const health=await api(page,'health');await global.__minderMarketAndRestart({browser,page,evidence:{backend_revision:health.runtime_revision},api});}finally{await browser.close();if(trace.market_answer_gate!=='passed')process.exitCode=2;}})().catch(error=>{trace.failure=error.message;write();process.exitCode=1;});
}else{const compiled=new Module(filename,module);compiled.filename=filename;compiled.paths=Module._nodeModulePaths(path.dirname(filename));compiled._compile(source,filename);}
