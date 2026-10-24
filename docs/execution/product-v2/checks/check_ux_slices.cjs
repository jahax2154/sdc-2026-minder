// Early A browser integration of committed F UX1/2; no provider invocation.
const assert=require('node:assert/strict'),fs=require('node:fs');
const {chromium}=require('/private/tmp/minder-c-ui-check/node_modules/playwright');
(async()=>{
 const output=process.env.MINDER_BROWSER_OUTPUT_DIR;assert(output);fs.mkdirSync(output,{recursive:true});
 const browser=await chromium.launch(),page=await browser.newPage({viewport:{width:1280,height:720}});
 const errors=[];let documents=0,turns=0;
 page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(r.isNavigationRequest()&&r.frame()===page.mainFrame())documents++;if(r.url().endsWith('/api/product/conversation-turn'))turns++;});
 const ready=()=>page.locator('#view[aria-busy=false]').waitFor();
 try{
  await page.goto('http://127.0.0.1:9111/#minder');await page.locator('#minderInput').waitFor();
  await page.evaluate(async()=>{const r=await fetch('/api/profile',{method:'PUT',headers:{'Content-Type':'application/json',Authorization:'Bearer '+sessionStorage.getItem('minder-product-token')},body:JSON.stringify({profile:{synthetic:true,onboarding:{stage:'studying',objective:'fit',context:'Fictional frontend integration check'}},expected_version:null})});if(!r.ok)throw Error('Synthetic Profile '+r.status);});
  await page.evaluate(()=>window.__uxShell=document.querySelector('.sidebar'));
  const routes=['#profile','#careers/matches','#my-path/next','#minder','#mindbots'];
  for(const route of routes){await page.evaluate(hash=>location.hash=hash,route);await ready();await page.locator('#globalNewChat').waitFor({state:'visible'});assert(await page.evaluate(()=>window.__uxShell===document.querySelector('.sidebar')));assert.equal(await page.locator('.sidebar').evaluate(n=>n.getBoundingClientRect().width),72);}
  await page.evaluate(()=>location.hash='#careers/matches');await ready();await page.locator('#careerCatalogue .career-row').last().waitFor();
  const before=await page.locator('#view').evaluate(n=>({top:n.scrollTop,height:n.clientHeight,content:n.scrollHeight}));assert(before.content>before.height);
  await page.locator('#view').hover();await page.mouse.wheel(0,5000);await page.waitForTimeout(200);
  const after=await page.locator('#view').evaluate(n=>n.scrollTop);assert(after>before.top,'real wheel must scroll overflowing content');
  await page.locator('#careerCatalogue .career-row').last().scrollIntoViewIfNeeded();assert(await page.locator('#careerCatalogue .career-row').last().isVisible());
  await page.evaluate(()=>{window.__uxHeader=document.querySelector('#view .page-heading');window.__uxTabs=document.querySelector('#view .tabs');});
  for(const tab of ['compare','outlook','matches']){await page.evaluate(hash=>location.hash=hash,'#careers/'+tab);await ready();assert(await page.evaluate(()=>window.__uxHeader===document.querySelector('#view .page-heading')&&window.__uxTabs===document.querySelector('#view .tabs')));}
  await page.evaluate(()=>location.hash='#minder');await page.locator('#minderInput').waitFor();await page.locator('#minderInput').fill('Synthetic unsent draft');await page.locator('#globalNewChat').click();await page.locator('#minderInput').waitFor();assert.equal(turns,0);
  assert.equal(documents,1);assert.deepEqual(errors,[]);
  await page.screenshot({path:output+'/minder-desktop.png',fullPage:true});
  const report={base:'http://127.0.0.1:9111',frontend_revision:'2c5d11923acd9860e764d31e704315f2a631c711',viewport:[1280,720],actual_local_backend:true,global_plus_visible_all_tested_modules:true,stable_shell_and_72px_rail:true,actual_wheel_scroll_before:before,actual_scroll_after:after,career_heading_and_tabs_same_nodes:true,document_navigations:documents,provider_turn_requests:turns,page_errors:errors,scope:'Early desktop committed-slice integration; not full UX6/mobile/zoom/Home/customization acceptance.'};
  fs.writeFileSync(output+'/integration.json',JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exit(1);});
