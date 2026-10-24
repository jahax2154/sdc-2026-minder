import {api as requestApi,optional,key,RequestError} from '../client.js';
import {card,esc,bind,showError} from '../ui.js';
// Keep only retry receipts across refresh; file bytes stay in memory during upload.
const receiptKey='minder-product-document-deletes';
function receipts(){try{return JSON.parse(sessionStorage.getItem(receiptKey)||'{}');}catch{return {};}}
function saveReceipt(id,body){const all=receipts();if(body)all[id]=body;else delete all[id];sessionStorage.setItem(receiptKey,JSON.stringify(all));}
const bytesLabel=n=>n<1024?n+' bytes':(n/1024).toFixed(0)+' KiB';
export async function documents(ctx,root){
  const api=async(path,body,method=body===undefined?'GET':'POST')=>{const result=await requestApi(path,body,method,{signal:ctx.signal});if(!ctx.isCurrent())throw new RequestError('request_cancelled');return result;};
  const library=await optional('product/documents',{signal:ctx.signal});if(!ctx.isCurrent())return;
  if(!library){root.innerHTML=card('CV & resume','<p>The private document library is not available yet. You can still enter your profile and review TXT intake below.</p>');return;}
  const enabled=library.storage.status==='available',limit=library.limits;
  root.innerHTML=card('CV & resume',`<p>Upload your CV or resume as a PDF or UTF-8 TXT file. Uploading does not change your profile.</p><small>${library.usage.file_count} of ${limit.max_files} files · ${bytesLabel(library.usage.stored_or_reserved_bytes)} of ${bytesLabel(limit.max_user_bytes)} used · ${bytesLabel(limit.max_file_bytes)} maximum per file.</small><p>${enabled?'Local development storage is available. Durable hosted storage has not been verified.':'Document storage is unavailable. Manual profile entry and direct TXT intake remain available.'}</p><form id="documentUpload"><label>File purpose<select id="documentPurpose"><option value="cv">CV</option><option value="resume">Resume</option></select></label><label>PDF or TXT file<input id="documentFile" type="file" accept=".pdf,.txt,application/pdf,text/plain" ${enabled?'':'disabled'} required></label><button id="uploadDocument" type="submit" ${enabled?'':'disabled'}>Upload file</button></form><div id="documentUploadStatus" role="status"></div><div id="documentList"></div><div id="documentReview"></div><p class="secondary">Deleting a file removes its linked drafts. Profile entries you already reviewed and saved remain. ${library.extraction?.pdf_status==='supported_text_only'?'Text-based PDF and TXT extraction require your review; scanned PDFs need manual entry.':'PDF text extraction is unavailable in this runtime; TXT extraction requires your review.'}</p>`);
  let uploadBody=null;
  document.querySelector('#documentFile').onchange=()=>{uploadBody=null;};document.querySelector('#documentPurpose').onchange=()=>{uploadBody=null;};
  bind('documentUpload',async()=>{
    if(!uploadBody){
      const file=document.querySelector('#documentFile').files[0];if(!file)throw new Error('Choose a PDF or TXT file.');
      if(file.size>limit.max_file_bytes)throw new Error('This file exceeds the '+bytesLabel(limit.max_file_bytes)+' limit.');
      if(!file.size)throw new Error('Choose a nonempty file.');
      const suffix=file.name.split('.').at(-1).toLowerCase();if(!['pdf','txt'].includes(suffix))throw new Error('Only PDF or UTF-8 TXT files are supported.');
      const bytes=new Uint8Array(await file.arrayBuffer());let binary='';for(let i=0;i<bytes.length;i+=8192)binary+=String.fromCharCode(...bytes.subarray(i,i+8192));
      uploadBody={purpose:document.querySelector('#documentPurpose').value,filename:file.name,content_type:suffix==='pdf'?'application/pdf':'text/plain',content_base64:btoa(binary),idempotency_key:key()};
    }
    try{await api('product/document-upload',uploadBody);uploadBody=null;await ctx.render();}
    catch(e){document.querySelector('#documentUploadStatus').textContent='Upload was not confirmed. Refresh the list before retrying; choosing another file starts a new upload.';if([413,415,422].includes(e.status))uploadBody=null;throw e;}
  });
  const list=document.querySelector('#documentList');
  list.innerHTML=library.documents.length?library.documents.map((d,i)=>card(d.filename||'File pending deletion',`<p>${esc(d.content_type||'')} · ${bytesLabel(d.size_bytes||0)} · ${esc(d.purpose||'legacy_unclassified')} · ${esc(d.status)} · ${esc(d.extraction_status||'not requested')}</p><small>Uploaded ${esc(d.created_at||'unknown')}</small><button id="downloadDocument-${i}" ${enabled&&d.status==='active'?'':'disabled'}>Download attachment</button><button id="extractDocument-${i}" ${enabled&&d.status==='active'?'':'disabled'}>${d.content_type==='text/plain'||library.extraction?.pdf_status==='supported_text_only'?'Review extracted text':'Check extraction availability'}</button><button class="secondary" id="deleteDocument-${i}" ${enabled?'':'disabled'}>${d.status==='deleting'?'Retry deletion':'Delete file'}</button>`)).join(''):'<p>No files uploaded yet.</p>';
  for(const [i,d] of library.documents.entries()){
    bind('downloadDocument-'+i,async()=>{
      const result=await api('product/document-download',{document_id:d.document_id});
      const binary=atob(result.content_base64),bytes=Uint8Array.from(binary,c=>c.charCodeAt(0));
      const url=URL.createObjectURL(new Blob([bytes],{type:'application/octet-stream'}));
      const anchor=document.createElement('a');anchor.href=url;anchor.download=result.document.filename||'document';anchor.hidden=true;document.body.append(anchor);anchor.click();anchor.remove();setTimeout(()=>URL.revokeObjectURL(url),30000);
    });
    bind('extractDocument-'+i,async()=>{
      const result=await api('product/document-extract',{document_id:d.document_id});
      const review=document.querySelector('#documentReview');
      // Extraction may advance document.version; refresh the list before deleting.
      d.version=result.document.version;
      if(!result.draft||result.extraction.status==='unavailable'){
        review.innerHTML=card('Text extraction unavailable',`<p>${esc(result.extraction?.reason||result.extraction?.code||'This file has no supported extractable text in this runtime.')}</p><p>Enter your context manually in Background. No information was applied.</p>`);return;
      }
      const draft=result.draft;
      if(draft.status==='reviewed'){review.innerHTML=card('Already reviewed','<p>You already reviewed this text. Edit your saved profile fields above if you want to correct them.</p>');return;}
      review.innerHTML=card('Review extracted CV / resume context',`<p>${esc(draft.clarification)}</p><pre class="draft-text">${esc(draft.text)}</pre><form id="applyDocument"><label>Corrected experience<textarea id="documentExperience" maxlength="4000">${esc(draft.text.slice(0,4000))}</textarea></label><button type="submit">Save reviewed context to profile</button></form><p id="documentReviewStatus" role="status"></p><button class="button-outline" id="reloadDocumentReview" type="button" hidden>Reload saved profile before editing</button><p>This records your corrected self-report. It does not assess skills or certify mastery.</p>`);
      let exactBody=null;
      bind('applyDocument',async()=>{
        exactBody??={draft_id:draft.id,expected_profile_version:ctx.profile.version,profile:{career_context:{experience:document.querySelector('#documentExperience').value}},idempotency_key:key()};
        const editor=document.querySelector('#documentExperience'),status=document.querySelector('#documentReviewStatus'),reload=document.querySelector('#reloadDocumentReview');
        editor.readOnly=true;
        try{await api('product/intake-correction',exactBody);await ctx.render();}
        catch(e){
          if([413,415,422].includes(e.status)){exactBody=null;editor.readOnly=false;status.textContent='The review was rejected. Correct your text before sending again.';}
          else{status.textContent='This exact review was submitted; its outcome is not confirmed. The text is locked so a retry cannot silently send a different review. Retry the same review or reload the saved profile before editing.';document.querySelector('#applyDocument button').textContent='Retry this exact review';reload.hidden=false;reload.onclick=()=>ctx.render();}
          throw e;
        }
      });
    });
    bind('deleteDocument-'+i,async()=>{
      const body=receipts()[d.document_id]||{document_id:d.document_id,expected_version:d.version,idempotency_key:key()};saveReceipt(d.document_id,body);
      try{await api('product/document-delete',body);saveReceipt(d.document_id,null);await ctx.render();}
      catch(e){if(e.status===409){saveReceipt(d.document_id,null);await ctx.render();}throw e;}
    });
  }
}
