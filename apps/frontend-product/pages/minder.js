import {api,validateChat} from '../client.js';
import {esc,facts,showError,bind} from '../ui.js';
import {hydrateIcons} from '../icons.js';
// Transient, memory-only display history. There is no backend transcript endpoint.
const messages=[];
let pending=false;
export async function minder(ctx) {
  const response=await fetch('pages/minder.html');if(!response.ok)throw new Error('Chat layout unavailable.');
  ctx.view.innerHTML=await response.text();ctx.view.className='page-main chat-page';
  const $=s=>ctx.view.querySelector(s), input=$('#minderInput');
  if(ctx.chatDraft){input.value=ctx.chatDraft;delete ctx.chatDraft;}
  function update() {
    const active=messages.length>0;$('#minderWelcome').classList.toggle('hide',active);$('#minderActive').classList.toggle('hide',!active);
    $('#minderThread').innerHTML=messages.map(m=>m.role==='user'?`<div class="user-message">${esc(m.text)}</div>`:m.role==='error'?`<article class="assistant-answer"><p>${esc(m.text)}</p></article>`:`<article class="assistant-answer"><p class="secondary">${m.result.provider.status==='available'?'Language-assisted answer':'Language service unavailable · saved evidence and limitations'}</p>${facts(m.result.statements)}</article>`).join('')+(pending?'<div class="thinking-row" role="status"><span class="spinner"></span>Checking saved evidence…</div>':'');
    $('#minderComposer button[type=submit]').disabled=pending;
    if(active&&innerWidth>1200)$('#minderContext').classList.remove('hide');
    $('#minderContext').innerHTML=`<div class="rail-card"><div class="rail-heading"><strong>Your context</strong></div><p>${esc(ctx.profile?.career_context?.goals||'No goal reported yet.')}</p><p>${esc(ctx.profile?.timezone||'Timezone not set')}</p><p>${esc(ctx.profile?.evidence?.length??0)} evidence items recorded.</p><a href="#profile">Review profile →</a></div><div class="rail-card"><strong>Keep moving</strong><p><a href="#roadmap">Review roadmap →</a></p><p><a href="#mindbots">Review proposed changes →</a></p></div>`;
    $('#minderScroll').scrollTop=$('#minderScroll').scrollHeight;hydrateIcons(ctx.view);
  }
  async function send() {
    const message=input.value.trim();if(!message||pending)return;
    if(!ctx.profile) {showError(new Error('Save a partial profile first so Minder can use its current context. Open My profile.'));return;}
    if(message.length>4000)throw new Error('Please keep your question within 4,000 characters.');
    messages.push({role:'user',text:message});input.value='';pending=true;update();
    try {
      const result=validateChat(await api('chat',{message,expected_profile_version:ctx.profile.version,...(ctx.selectedRole?{selected_role_ids:[ctx.selectedRole]}:{})}));
      messages.push({role:'assistant',result});
    }catch(e){messages.push({role:'error',text:e.message+' Your question was not automatically retried.'});if(e.status===409)await ctx.refreshProfile();}
    finally{pending=false;if(ctx.view.querySelector('#minderThread'))update();}
  }
  bind('minderComposer',send);
  input.maxLength=4000;input.addEventListener('input',()=>{input.style.height='auto';input.style.height=Math.min(130,input.scrollHeight)+'px';});
  input.addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();$('#minderComposer').requestSubmit();}});
  ctx.view.querySelectorAll('[data-prompt]').forEach(b=>b.onclick=()=>{input.value=b.dataset.prompt;input.focus();});
  $('#minderContextToggle').onclick=()=>$('#minderContext').classList.toggle('hide');
  $('#minderNewSmall').onclick=()=>{if(pending)return;messages.length=0;update();};
  $('#minderAdd').onclick=()=>{location.hash='profile';};
  update();
}
export function clearConversation(){if(!pending)messages.length=0;}
