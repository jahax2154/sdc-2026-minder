// Actual Chromium tab zoom, not CSS zoom/device-scale emulation.
const {chromium,assert,fs,base,output}=require('./final_ux_support.cjs');
(async()=>{
 const extension=output+'/zoom-extension';fs.mkdirSync(extension,{recursive:true});
 fs.writeFileSync(extension+'/manifest.json',JSON.stringify({manifest_version:3,name:'Local Minder zoom acceptance',version:'1.0',permissions:['tabs'],background:{service_worker:'background.js'}}));
 fs.writeFileSync(extension+'/background.js','chrome.runtime.onInstalled.addListener(()=>{});');
 const context=await chromium.launchPersistentContext(output+'/zoom-profile',{channel:'chromium',headless:true,args:[`--disable-extensions-except=${extension}`,`--load-extension=${extension}`],viewport:{width:1280,height:720}});
 try{
  const worker=context.serviceWorkers()[0]||await context.waitForEvent('serviceworker'),page=context.pages()[0];
  await page.goto(base+'/#profile');await page.waitForSelector('#setupNext');
  const zoom=factor=>worker.evaluate(async({base,factor})=>{const tabs=await chrome.tabs.query({url:base+'/*'});await chrome.tabs.setZoom(tabs[0].id,factor);return chrome.tabs.getZoom(tabs[0].id);},{base,factor});
  await zoom(1);await page.waitForFunction(()=>innerWidth===1280);const before=await page.evaluate(()=>({width:innerWidth,dpr:devicePixelRatio}));
  assert.equal(await zoom(2),2);await page.waitForFunction(()=>innerWidth===640);const after=await page.evaluate(()=>({width:innerWidth,dpr:devicePixelRatio}));
  async function bottom(selector){await page.locator('#view').hover();await page.mouse.wheel(0,10000);await page.waitForTimeout(120);const rect=await page.locator(selector).boundingBox();assert(rect&&rect.y>=0&&rect.y+rect.height<=await page.evaluate(()=>innerHeight));}
  await bottom('#setupNext');await page.screenshot({path:output+'/ux6-real-200pct-profile.png'});
  await page.locator('[data-choice=studying]').click();await bottom('#setupNext');await page.click('#setupNext');await page.locator('[data-choice=fit]').click();await bottom('#setupNext');await page.click('#setupNext');await page.locator('#setup-context').fill('Fictional zoom acceptance studies');await bottom('#setupNext');await page.click('#setupNext');await bottom('#skipOptional');await page.click('#skipOptional');await bottom('#setupNext');await page.click('#setupNext');await page.waitForURL('**/#profile/overview');await page.waitForSelector('.profile-tabs');
  const rows=[];
  for(const route of ['home','profile/overview','careers/matches','careers/compare','careers/outlook','my-path/skills','my-path/next','my-path/progress','my-path/roadmap']){
   await page.evaluate(route=>location.hash=route,route);await page.waitForSelector(`#view[data-route="${route}"][data-rendered="${route.split('/')[0]}"]`);
   assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await page.locator('#view').hover();await page.mouse.wheel(0,10000);await page.waitForTimeout(80);await page.locator('#view').focus();await page.keyboard.press('Control+End');
   rows.push(await page.locator('#view').evaluate(el=>({route:el.dataset.route,height:el.clientHeight,scroll:el.scrollHeight,top:el.scrollTop,overflow:getComputedStyle(el).overflow})));assert(await page.locator('#view').evaluate(e=>e.scrollHeight-e.clientHeight-e.scrollTop<3));
  }
  fs.writeFileSync(output+'/ux6-real-zoom.json',JSON.stringify({browser_zoom:2,before,after,profile_all_bottom_controls:true,rows},null,2));console.log('PASS actual browser zoom200%; full Profile bottom-button journey; Home/Profile/Careers/My Path wheel+keyboard end access');
 }finally{await context.close();}
})().catch(error=>{console.error(error);process.exit(1);});
