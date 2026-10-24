import {api,key} from '../client.js';
import {history,listConversations,createConversation,deleteConversation,sendTurn} from '../conversations.js';
import {messageMarkup} from '../chat-renderer.js';
import {esc,facts,showError,bind} from '../ui.js';
import {hydrateIcons,svg} from '../icons.js';
// Transcripts are read from the server on every open; this state is presentation only.
const state={messages:[],draft:'',contextOpen:false,scrollTop:0,pending:null,previousContext:null,conversationId:null,uncertainBody:null,loading:false};
let layoutText=null;
let renderCurrent=null;
function releaseInert(){document.querySelectorAll('.sidebar,.topbar,.chat-page .content-col').forEach(n=>n.inert=false);}
window.addEventListener('hashchange',()=>{if(location.hash!=='#minder')releaseInert();});
export async function minder(ctx,conversationId='') {
  state.messages=[];state.pending=null;state.conversationId=conversationId||null;state.uncertainBody=null;state.loading=!!conversationId;
  if(!layoutText){const controller=new AbortController(),abort=()=>controller.abort();ctx.signal?.addEventListener('abort',abort,{once:true});const timer=setTimeout(abort,8000);try{const response=await fetch('pages/minder.html',{signal:controller.signal});if(!response.ok)throw new Error('Chat layout unavailable.');layoutText=await response.text();}finally{clearTimeout(timer);ctx.signal?.removeEventListener('abort',abort);}}
  if(ctx.isCurrent&&!ctx.isCurrent())return;ctx.view.innerHTML=layoutText;ctx.view.className='page-main chat-page';ctx.view.dataset.frameReady='true';ctx.view.setAttribute('aria-busy','false');
  const $=s=>ctx.view.querySelector(s),input=$('#minderInput'),thread=$('#minderThread'),panel=$('#minderContext'),toggle=$('#minderContextToggle'),scroll=$('#minderScroll');
  if(ctx.chatDraft){state.draft=ctx.chatDraft;delete ctx.chatDraft;}input.value=state.draft;
  const mounted=()=>ctx.isCurrent()&&ctx.view.querySelector('#minderThread')===thread;
  const toolbar=document.createElement('div');toolbar.className='chat-history-toolbar';toolbar.innerHTML='<label for="minderConversationList">Saved conversations</label><select id="minderConversationList" aria-label="Saved Minder conversations"><option value="">New conversation</option></select><button type="button" class="button-outline" id="deleteMinderConversation" disabled>Delete</button><button type="button" class="button-outline" id="refreshMinderHistory">Refresh history</button>';ctx.view.querySelector('.content-col').prepend(toolbar);toolbar.insertAdjacentHTML('afterend','<div class="chat-history-status" id="minderHistoryStatus" role="status"></div>');
  $('.composer-caption').textContent='Private conversation saved to your account. Plans and actions need explicit confirmation.';
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
    if(!mounted())return;const oldTop=scroll.scrollTop,active=state.messages.length>0||state.loading||!!state.pending;
    $('#minderWelcome').classList.toggle('hide',active);$('#minderActive').classList.toggle('hide',!active);
    thread.innerHTML=messageMarkup(state.messages)+(state.pending&&state.messages.at(-1)?.content!==state.pending.message?`<div class="user-message">${esc(state.pending.message)}</div>`:'')+(state.pending?'<div class="thinking-row" role="status"><span class="spinner"></span><span>Working…</span></div>':'');
    $('#minderComposer button[type=submit]').disabled=!!state.pending||state.loading;input.disabled=!!state.pending||state.loading;$('#minderNewSmall').disabled=!!state.pending||state.loading;
    $('#cancelMinder').classList.toggle('hide',!state.pending);contextLayout();hydrateIcons(ctx.view);
    ctx.view.querySelectorAll('[data-review-question]').forEach(b=>b.onclick=()=>{state.draft=state.messages[Number(b.dataset.reviewQuestion)].question;input.value=state.draft;input.focus();});
    scroll.scrollTop=toEnd?scroll.scrollHeight:oldTop;
  }
  renderCurrent=update;
  async function loadSaved(){
    if(!mounted())return;state.loading=true;update();$('#minderHistoryStatus').textContent='Loading saved conversations…';
    try{
      const list=await listConversations({signal:ctx.signal});if(!mounted())return;
      $('#minderConversationList').innerHTML='<option value="">New conversation</option>'+list.map(c=>`<option value="${esc(c.conversation_id)}" ${c.conversation_id===state.conversationId?'selected':''}>${esc(c.title)}</option>`).join('');
      if(state.conversationId){const saved=await history('minder',state.conversationId,{signal:ctx.signal});if(!mounted())return;state.messages=saved.messages;if(state.uncertainBody&&saved.messages.some((m,i)=>m.role==='user'&&m.content===state.uncertainBody.message&&saved.messages[i+1]?.role==='assistant'))state.uncertainBody=null;$('#minderHistoryStatus').textContent=saved.pending_turns.length?'An earlier request is processing or uncertain. Refresh saved history before issuing another instruction.':'';}else $('#minderHistoryStatus').textContent='';
      $('#deleteMinderConversation').disabled=!state.conversationId;
    }catch(e){if(mounted()&&e.code!=='request_cancelled'){$('#minderHistoryStatus').textContent=e.message+' Refresh history to try again.';showError(e);}}
    finally{if(mounted()){state.loading=false;update();}}
  }
  let createBody=null,deleteBody=null;
  $('#minderConversationList').onchange=event=>{location.hash=event.target.value?'minder/'+encodeURIComponent(event.target.value):'minder';};
  $('#refreshMinderHistory').onclick=()=>loadSaved();
  $('#deleteMinderConversation').onclick=async event=>{if(state.pending||!state.conversationId)return;if(!confirm('Delete this saved Minder conversation?'))return;const button=event.currentTarget;button.disabled=true;deleteBody??={conversation_id:state.conversationId,idempotency_key:key()};try{await deleteConversation(deleteBody);clearConversation();location.hash='minder';if(mounted())await ctx.render();}catch(e){if(mounted()){showError(e);$('#minderHistoryStatus').textContent='Deletion is not confirmed. Refresh history before another change.';}}finally{if(button.isConnected)button.disabled=false;}};
  async function send(){
    const message=input.value.trim();if(!message||state.pending||state.loading)return;
    if(state.uncertainBody){$('#minderHistoryStatus').textContent='The earlier request outcome is uncertain. Refresh saved history or use Retry exact request below.';return;}
    if(message.length>4000)throw new Error('Please keep your question within 4,000 characters.');
    await submit(message);
  }
  async function submit(message,exactBody=null){
    const request={controller:new AbortController(),message};state.pending=request;state.draft='';input.value='';update(true);
    const abort=()=>{request.invalidated=true;request.controller.abort();};ctx.signal.addEventListener('abort',abort,{once:true});
    try{
      await ctx.profileReady;if(request.invalidated)return;if(ctx.profileError)throw new Error('Saved context could not be loaded. Retry context before sending.');
      if(!state.conversationId){createBody??={idempotency_key:key(),title:message.slice(0,120)};const created=await createConversation(createBody);if(request.invalidated)return;state.conversationId=created.conversation.conversation_id;const option=document.createElement('option');option.value=state.conversationId;option.textContent=created.conversation.title;$('#minderConversationList').append(option);$('#minderConversationList').value=state.conversationId;$('#deleteMinderConversation').disabled=false;window.history.replaceState(null,'','#minder/'+encodeURIComponent(state.conversationId));}
      const body=exactBody||{conversation_id:state.conversationId,message,idempotency_key:key(),expected_profile_version:ctx.profile?.version??null};request.body=body;
      const result=await sendTurn(body,{signal:request.controller.signal});if(request.invalidated)return;
      state.uncertainBody=null;
      if(['processing','uncertain'].includes(result.turn.status)){$('#minderHistoryStatus').textContent='The server has not confirmed a final outcome. Refresh history; this instruction was not replayed.';}
      else $('#minderHistoryStatus').textContent=result.turn.status==='failed'?'This request failed. Review its saved result before sending a new question.':'';
      const saved=await history('minder',state.conversationId,{signal:request.controller.signal});if(request.invalidated)return;state.messages=saved.messages;
      if(result.response?.generation)window.dispatchEvent(new Event('minder-generation-available'));
    }catch(e){if(request.invalidated)return;state.draft=message;input.value=message;
      if(request.body&&(!e.status||e.status>=500))state.uncertainBody=request.body;
      $('#minderHistoryStatus').innerHTML=`${esc(e.message)} Your request was not automatically retried. ${state.uncertainBody?'<button type="button" class="button-outline" id="retryExactMinder">Retry exact request</button>':''}`;
      if($('#retryExactMinder'))$('#retryExactMinder').onclick=()=>{if(!state.pending)submit(state.uncertainBody.message,state.uncertainBody);};
    }finally{ctx.signal.removeEventListener('abort',abort);if(state.pending===request){state.pending=null;if(mounted())update(true);}}
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
  $('#minderNewSmall').onclick=()=>{if(clearConversation()){location.hash='minder';ctx.render();}};$('#minderAdd').onclick=()=>{location.hash='profile';};
  update();scroll.scrollTop=state.scrollTop;await loadSaved();
}
export function clearConversation(){if(state.pending)return false;state.messages.length=0;state.draft='';state.contextOpen=false;state.scrollTop=0;state.previousContext=null;state.conversationId=null;state.uncertainBody=null;state.loading=false;releaseInert();return true;}
export function invalidateConversation(){if(state.pending){state.pending.invalidated=true;state.pending.controller.abort();state.pending=null;}clearConversation();}
