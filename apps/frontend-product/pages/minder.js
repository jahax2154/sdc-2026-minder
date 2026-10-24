import {api,validateChat} from '../client.js';
import {esc,facts,showError,bind} from '../ui.js';
import {hydrateIcons,svg} from '../icons.js';
// Display context lasts only in this tab's memory; the backend has no transcript CRUD.
const state={messages:[],draft:'',contextOpen:false,scrollTop:0,pending:null,previousContext:null};
let layoutText=null;
let renderCurrent=null;
function releaseInert(){document.querySelectorAll('.sidebar,.topbar,.chat-page .content-col').forEach(n=>n.inert=false);}
window.addEventListener('hashchange',()=>{if(location.hash!=='#minder')releaseInert();});
export async function minder(ctx) {
  if(!layoutText){const controller=new AbortController(),abort=()=>controller.abort();ctx.signal?.addEventListener('abort',abort,{once:true});const timer=setTimeout(abort,8000);try{const response=await fetch('pages/minder.html',{signal:controller.signal});if(!response.ok)throw new Error('Chat layout unavailable.');layoutText=await response.text();}finally{clearTimeout(timer);ctx.signal?.removeEventListener('abort',abort);}}
  if(ctx.isCurrent&&!ctx.isCurrent())return;ctx.view.innerHTML=layoutText;ctx.view.className='page-main chat-page';ctx.view.dataset.frameReady='true';ctx.view.setAttribute('aria-busy','false');
  const $=s=>ctx.view.querySelector(s),input=$('#minderInput'),thread=$('#minderThread'),panel=$('#minderContext'),toggle=$('#minderContextToggle'),scroll=$('#minderScroll');
  if(ctx.chatDraft){state.draft=ctx.chatDraft;delete ctx.chatDraft;}input.value=state.draft;
  const mounted=()=>ctx.view.querySelector('#minderThread')===thread;
  function contextLayout(focus=false){
    if(!mounted())return;const overlay=innerWidth<=1050&&state.contextOpen;
    panel.classList.toggle('hide',!state.contextOpen);toggle.setAttribute('aria-expanded',String(state.contextOpen));
    panel.setAttribute('role',overlay?'dialog':'complementary');if(overlay)panel.setAttribute('aria-modal','true');else panel.removeAttribute('aria-modal');
    releaseInert();if(overlay)document.querySelectorAll('.sidebar,.topbar,.chat-page .content-col').forEach(n=>n.inert=true);
    if(focus&&state.contextOpen)$('#closeMinderContext').focus();
  }
  function setContext(open){const top=scroll.scrollTop;state.contextOpen=open;contextLayout(open);scroll.scrollTop=top;if(!open)toggle.focus();}
  panel.innerHTML=`<div class="context-heading"><strong>Context</strong><button type="button" class="icon-button" id="closeMinderContext" aria-label="Close Context">${svg('x')}</button></div><div class="rail-card" id="savedChatContext"><div class="rail-heading"><strong>Your context</strong></div><p>${esc(ctx.profile?.career_context?.goals||'No goal reported yet.')}</p><p>${esc(ctx.profile?.timezone||'Timezone not set')}</p><p>${esc(ctx.profile?.evidence?.length??0)} evidence items recorded.</p><a href="#profile">Review profile →</a></div><div class="rail-card"><strong>Keep moving</strong><p><a href="#roadmap">Review roadmap →</a></p><p><a href="#mindbots">Review proposed changes →</a></p></div>`;
  function profileContext(){if(!mounted())return;const target=$('#savedChatContext');target.innerHTML=ctx.profileStatus==='loading'?'<p role="status">Loading saved context…</p>':ctx.profileError?'<strong>Saved context unavailable</strong><p>You can retry loading it.</p><button class="button-outline" id="retryChatContext">Retry context</button>':`<strong>Your context</strong><p>${esc(ctx.profile?.career_context?.goals||'No goal reported yet.')}</p><p>${esc(ctx.profile?.timezone||'Timezone not supplied')}</p><p>${esc(ctx.profile?.evidence?.length??0)} evidence items recorded.</p><a href="#profile">Review profile →</a>`;if($('#retryChatContext'))$('#retryChatContext').onclick=()=>ctx.refreshProfile();}
  ctx.onProfileLoaded=profileContext;profileContext();
  function update(toEnd=false){
    if(!mounted())return;const oldTop=scroll.scrollTop,active=state.messages.length>0;
    $('#minderWelcome').classList.toggle('hide',active);$('#minderActive').classList.toggle('hide',!active);
    thread.innerHTML=state.messages.map((m,i)=>{
      if(m.role==='user')return `<div class="user-message">${esc(m.text)}</div>`;
      if(m.role==='error')return `<article class="assistant-answer request-result" data-result="${esc(m.code||'error')}"><p role="status">${esc(m.text)}</p><button class="button-outline" data-review-question="${i}">Review question to try again</button></article>`;
      const limits=m.result.statements.filter(s=>s.category==='limitation'),content=m.result.statements.filter(s=>s.category!=='limitation');
      return `<article class="assistant-answer" data-response-mode="${esc(m.result.response_mode||'legacy_evidence')}">${m.result.answer?`<p class="answer-text">${esc(m.result.answer)}</p>`:''}${facts(content)}${limits.length?`<div class="reply-limitation">${facts(limits.slice(0,1))}${limits.length>1?`<details><summary>Additional limitations</summary>${facts(limits.slice(1))}</details>`:''}</div>`:''}<details class="response-details"><summary>Response details</summary><p>${m.result.response_mode==='application_guidance'?'Application guidance from verified Minder capabilities. No language-provider call was needed.':m.result.provider.invoked===false&&m.result.provider.code?.startsWith('provider_not_required_for_')?'Verified application or reference response. No language-provider call was needed.':m.result.response_mode==='limited_fallback'?'Language service unavailable; showing limited verified fallback content.':m.result.provider.status==='available'?'Language assistance available; only validated content is shown.':'Language service unavailable; this response is limited to verified fallback content.'}</p></details>${m.result.response_mode==='limited_fallback'?`<button class="button-outline" data-review-question="${i}">Review question to retry explanation</button>`:''}</article>`;
    }).join('')+(state.pending?'<div class="thinking-row" role="status"><span class="spinner"></span><span>Working…</span></div>':'');
    $('#minderComposer button[type=submit]').disabled=!!state.pending;input.disabled=!!state.pending;$('#minderNewSmall').disabled=!!state.pending;
    $('#cancelMinder').classList.toggle('hide',!state.pending);contextLayout();hydrateIcons(ctx.view);
    ctx.view.querySelectorAll('[data-review-question]').forEach(b=>b.onclick=()=>{state.draft=state.messages[Number(b.dataset.reviewQuestion)].question;input.value=state.draft;input.focus();});
    scroll.scrollTop=toEnd?scroll.scrollHeight:oldTop;
  }
  renderCurrent=update;
  async function send(){
    const message=input.value.trim();if(!message||state.pending)return;
    if(message.length>4000)throw new Error('Please keep your question within 4,000 characters.');
    state.messages.push({role:'user',text:message});state.draft='';input.value='';
    const request={controller:new AbortController(),message};state.pending=request;update(true);
    try{await ctx.profileReady;if(request.invalidated)return;if(ctx.profileError)throw new Error('Saved context could not be loaded. Retry context, then review this question.');const result=validateChat(await api('chat',{message,expected_profile_version:ctx.profile?.version??null,...(state.previousContext?{previous_context_id:state.previousContext}:{}),...(ctx.selectedRole?{selected_role_ids:[ctx.selectedRole]}:{})},'POST',{signal:request.controller.signal}));if(request.invalidated)return;state.previousContext=result.conversation_context_id||null;state.messages.push({role:'assistant',question:message,result});}
    catch(e){if(request.invalidated)return;state.messages.push({role:'error',question:message,code:e.code,text:e.message+(e.code==='request_cancelled'?'':' Your question was not automatically retried.')});}
    finally{if(state.pending===request){state.pending=null;renderCurrent?.(true);}}
  }
  bind('minderComposer',send);$('#cancelMinder').onclick=()=>state.pending?.controller.abort();
  input.maxLength=4000;input.addEventListener('input',()=>{state.draft=input.value;input.style.height='auto';input.style.height=Math.min(130,input.scrollHeight)+'px';});
  input.addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();$('#minderComposer').requestSubmit();}});
  scroll.addEventListener('scroll',()=>state.scrollTop=scroll.scrollTop);
  const prompts=['Help me understand a practical preparation path using my saved profile and selected role.','Explain which requirements are supported by my evidence and which are unassessed.','Help me review my current plan and suggest realistic next steps without changing it.','Help me compare career directions using the available evidence and its limits.'];
  ctx.view.querySelectorAll('[data-prompt]').forEach((b,i)=>b.onclick=()=>{state.draft=prompts[i]||b.dataset.prompt;input.value=state.draft;input.focus();});
  toggle.onclick=()=>setContext(!state.contextOpen);$('#closeMinderContext').onclick=()=>setContext(false);
  panel.addEventListener('keydown',e=>{if(e.key==='Escape'){e.preventDefault();e.stopPropagation();setContext(false);}else if(e.key==='Tab'&&innerWidth<=1050){const controls=[...panel.querySelectorAll('button,a[href]')];if(e.shiftKey&&document.activeElement===controls[0]){e.preventDefault();controls.at(-1).focus();}else if(!e.shiftKey&&document.activeElement===controls.at(-1)){e.preventDefault();controls[0].focus();}}});
  window.addEventListener('resize',()=>{if(mounted())contextLayout();},{signal:ctx.signal});
  $('#minderNewSmall').onclick=()=>{if(clearConversation()){input.value='';update();}};$('#minderAdd').onclick=()=>{location.hash='profile';};
  update();scroll.scrollTop=state.scrollTop;
}
export function clearConversation(){if(state.pending)return false;state.messages.length=0;state.draft='';state.contextOpen=false;state.scrollTop=0;state.previousContext=null;releaseInert();return true;}
export function invalidateConversation(){if(state.pending){state.pending.invalidated=true;state.pending.controller.abort();state.pending=null;}clearConversation();}
