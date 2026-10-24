// Actual route/assets/console/keyboard smoke; no provider or fixtures.
const assert=require('node:assert/strict');
const {chromium}=require(process.env.MINDER_PLAYWRIGHT_MODULE||'/private/tmp/minder-c-ui-check/node_modules/playwright');
(async()=>{
 const browser=await chromium.launch({headless:true}),page=await browser.newPage(),errors=[],failures=[];
 page.on('pageerror',e=>errors.push(e.message));
 page.on('console',m=>{if(m.type()==='error'&&!(m.location().url.includes('/api/')&&/status of (404|409)/.test(m.text())))errors.push(m.text());});
 page.on('response',r=>{if(r.status()>=400&&!r.url().includes('/api/'))failures.push({status:r.status(),url:new URL(r.url()).pathname});});
 const base=process.env.MINDER_PRODUCT_BASE_URL||'http://127.0.0.1:9106';
 try{
  for(const width of [1440,390])for(const route of ['minder','mindbots','profile','overview','career-match','roadmap','tasks','progress','news','future']){
   await page.setViewportSize({width,height:844});await page.goto(base+'/#'+route);await page.locator('#view[data-rendered="'+route+'"][aria-busy="false"]').waitFor();
   assert.equal(await page.locator('#error').isVisible(),false,route);assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,route);
  }
  await page.goto(base+'/#minder');await page.locator('#minderInput').waitFor();await page.locator('#minderInput').focus();await page.keyboard.type('Keyboard-only question');assert.equal(await page.locator('#minderInput').inputValue(),'Keyboard-only question');
  await page.locator('.mobile-menu').click();await page.keyboard.press('Escape');assert.equal(await page.locator('.sidebar').isVisible(),false);
  assert.deepEqual(errors,[]);assert.deepEqual(failures,[]);console.log(JSON.stringify({routes_desktop_and_mobile:20,keyboard_navigation:true,unexpected_console_errors:errors,failed_assets:failures}));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1);});
