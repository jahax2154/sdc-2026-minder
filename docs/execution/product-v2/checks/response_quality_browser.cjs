// One real request through the existing F UI. No profile, model or network fixtures.
const {chromium,assert,fs,api,base,output}=require('../../../../apps/frontend-product/tests/final_ux_support.cjs');
(async()=>{
 const browser=await chromium.launch({headless:true});const page=await browser.newPage({viewport:{width:1440,height:1000}});
 const report={question:'What are the market trends in Malaysia right now?',base,started_at:new Date().toISOString(),status:'started'};
 const save=()=>fs.writeFileSync(output+'/response-quality.json',JSON.stringify(report,null,2));
 try{
  await page.goto(base+'/#minder');await page.waitForFunction(()=>document.querySelector('#minderInput')&&!document.querySelector('#minderInput').disabled);
  report.backend_revision=(await api(page,'health')).runtime_revision;assert.equal((await api(page,'plans')).plans.length,0);
  await page.fill('#minderInput',report.question);
  const pending=page.waitForResponse(r=>r.url().endsWith('/api/product/conversation-turn'),{timeout:60000});const started=Date.now();
  await page.locator('#minderComposer').evaluate(form=>form.requestSubmit());const http=await pending;report.http_status=http.status();report.request_path=new URL(http.url()).pathname;
  report.response=(await http.json()).response;report.elapsed_ms=Date.now()-started;save();
  await page.waitForFunction(()=>document.querySelector('#minderInput')&&!document.querySelector('#minderInput').disabled);
  const answer=page.locator('#minderThread .assistant-answer').last(),main=answer.locator('.answer-text');report.main_answer=await main.innerText();
  const details=answer.locator('details.response-details').filter({has:page.locator('summary',{hasText:'Sources and supporting context'})});
  assert.equal(await details.count(),1);assert.equal(await details.getAttribute('open'),null);
  assert.equal(report.response.provider.status,'available');assert(report.response.statements.length>0);
  assert(!/Source method:|Explanation checks:|unsupported detail was omitted/i.test(report.main_answer));
  assert(/\[1(?:,|\])/.test(report.main_answer));assert(/2026/.test(report.main_answer));assert(!/^(?:Latest .*snapshot|I (?:retrieved|checked)|Source method)/i.test(report.main_answer));
  await page.screenshot({path:output+'/main-answer.png',fullPage:true});
  await details.locator(':scope > summary').click();report.sources_section=await details.innerText();
  assert(report.sources_section.includes('Source method:'));assert(report.sources_section.includes('Explanation checks:'));
  const links=await details.locator('.source a').evaluateAll(nodes=>nodes.map(n=>n.href));report.source_links=links;assert(report.response.sources.every(s=>links.includes(s.uri)));
  assert(report.sources_section.includes('[1] '));await page.screenshot({path:output+'/expanded-sources.png',fullPage:true});
  assert.equal((await api(page,'plans')).plans.length,0);
  report.profile_status=await page.evaluate(async()=>{const r=await fetch('/api/profile',{headers:{Authorization:'Bearer '+sessionStorage.getItem('minder-product-token')}});return r.status;});assert.equal(report.profile_status,404);
  report.status='passed';save();console.log(JSON.stringify({status:report.status,backend_revision:report.backend_revision,elapsed_ms:report.elapsed_ms,main_answer:report.main_answer},null,2));
 }catch(error){report.status='failed';report.error=error.message;save();await page.screenshot({path:output+'/failure.png',fullPage:true}).catch(()=>{});throw error;}
 finally{await browser.close();}
})().catch(error=>{console.error(error.message);process.exitCode=1;});
