// Real F document APIs and file controls. Synthetic bytes only; no provider/mocks.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const output=process.env.MINDER_BROWSER_OUTPUT_DIR||'/private/tmp';fs.mkdirSync(output,{recursive:true});
const {chromium}=require(process.env.MINDER_PLAYWRIGHT_MODULE||'/private/tmp/minder-c-ui-check/node_modules/playwright');
(async()=>{
 const browser=await chromium.launch({headless:true}),page=await browser.newPage({viewport:{width:1440,height:1000}}),errors=[],checks={};page.on('pageerror',e=>errors.push(e.message));
 const base=process.env.MINDER_PRODUCT_BASE_URL||'http://127.0.0.1:9106';
 const api=(path,body,method=body===undefined?'GET':'POST')=>page.evaluate(async({path,body,method})=>{const r=await fetch('/api/'+path,{method,headers:{'Content-Type':'application/json',Authorization:'Bearer '+sessionStorage.getItem('minder-product-token')},...(body===undefined?{}:{body:JSON.stringify(body)})});const v=await r.json();if(!r.ok)throw new Error(r.status+':'+v.code);return v;},{path,body,method});
 async function settled(){await page.waitForFunction(()=>!document.querySelector('[data-pending=true]')&&document.querySelector('#view').getAttribute('aria-busy')==='false');}
 async function click(selector,path){const waiting=page.waitForResponse(r=>r.url().endsWith('/api/'+path)&&r.request().method()==='POST');await page.locator(selector).click();assert.equal((await waiting).status(),200);await settled();}
 async function upload(name,type,buffer){await page.locator('#documentFile').setInputFiles({name,mimeType:type,buffer});await click('#uploadDocument','product/document-upload');}
 try{
  await page.goto(base+'/#profile');await page.locator('#save-profile').waitFor();await page.locator('#display-name').fill('Fictional Document Test');await page.locator('#save-profile').click();await page.locator('#documentFile').waitFor();await settled();
  let library=await api('product/documents');assert.equal(library.documents.length,0);
  if(library.storage.status!=='available'){assert(await page.locator('#uploadDocument').isDisabled());console.log(JSON.stringify({storage_unavailable_visible:true,upload_disabled:true}));return;}
  const initial=await api('profile');const txt=Buffer.from('Fictional document test: contributed to a class software project. No assessed mastery.');
  await upload('fictional-<review>.txt','text/plain',txt);library=await api('product/documents');assert.equal(library.documents.length,1);assert.deepEqual(await api('profile'),initial);assert.equal(await page.locator('#documentList img').count(),0);checks.upload_without_profile_apply=true;
  const downloaded=page.waitForEvent('download');await page.locator('[id^="downloadDocument-"]').click();const download=await downloaded;await download.saveAs(path.join(output,'minder-f-document-download.txt'));assert.deepEqual(fs.readFileSync(path.join(output,'minder-f-document-download.txt')),txt);checks.attachment_bytes_exact=true;
  await click('[id^="extractDocument-"]','product/document-extract');await page.locator('#documentExperience').fill('Corrected fictional document: wrote test cases for a class project.');await click('#applyDocument button','product/intake-correction');const applied=await api('profile');assert.match(applied.career_context.experience,/Corrected fictional document/);assert.equal(applied.evidence.length,0);checks.explicit_review_no_mastery=true;
  await upload('fictional.pdf','application/pdf',Buffer.from('%PDF-1.4\n%%EOF\n'));const pdfCard=page.locator('article').filter({has:page.getByRole('heading',{name:'fictional.pdf',exact:true})}).last();await pdfCard.locator('[id^="extractDocument-"]').click();await page.locator('#documentReview').filter({hasText:/Text extraction unavailable/}).waitFor();assert.deepEqual(await api('profile'),applied);assert.equal(await page.locator('iframe,embed,object').count(),0);checks.pdf_stored_extraction_unavailable=true;
  const txtCard=page.locator('article').filter({has:page.getByRole('heading',{name:'fictional-<review>.txt',exact:true})}).last();await txtCard.locator('[id^="deleteDocument-"]').click();await settled();library=await api('product/documents');assert.equal(library.documents.length,1);assert.deepEqual(await api('profile'),applied);checks.delete_preserves_applied_profile=true;
  await page.locator('[id^="deleteDocument-"]').click();await settled();assert.equal((await api('product/documents')).documents.length,0);checks.delete_library_empty=true;
  await page.reload();await page.locator('#documentFile').waitFor();await settled();assert.equal((await api('profile')).career_context.experience,applied.career_context.experience);checks.refresh_persistence=true;
  await page.locator('#documentFile').setInputFiles({name:'oversize.txt',mimeType:'text/plain',buffer:Buffer.alloc(library.limits.max_file_bytes+1,65)});await page.locator('#uploadDocument').click();await page.locator('#error').filter({hasText:/exceeds/}).waitFor();assert.equal((await api('product/documents')).documents.length,0);checks.size_limit_visible=true;
  await page.setViewportSize({width:390,height:844});await page.reload();await page.locator('#documentFile').waitFor();await settled();assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);checks.mobile_documents=true;
  await page.screenshot({path:path.join(output,'minder-f-documents-mobile.png'),fullPage:true});assert.deepEqual(errors,[]);checks.page_errors=errors;console.log(JSON.stringify(checks,null,2));fs.writeFileSync(path.join(output,'minder-f-documents.json'),JSON.stringify(checks,null,2));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1);});
