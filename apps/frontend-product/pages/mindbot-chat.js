import {key} from '../client.js';
import {history,sendTurn} from '../conversations.js';
import {messageMarkup} from '../chat-renderer.js';
import {esc} from '../ui.js';
import {bindDraftReviews} from '../plan-drafts.js';
let draft='';
window.addEventListener('minder-private-clear',()=>{draft='';});
export async function mindbotChat(ctx){
 const root=ctx.view,form=root.querySelector('#botComposer'),input=root.querySelector('#botInput'),welcome=root.querySelector('#botWelcome'),scroll=root.querySelector('#botScroll');
 welcome.insertAdjacentHTML('beforebegin','<div class="chat-history-status" id="botConversationStatus" role="status"></div><div class="chat-thread" id="botThread" aria-live="polite"></div>');
 form.insertAdjacentHTML('afterend','<button type="button" class="button-outline hide" id="stopBotWaiting">Stop waiting</button>');
 const thread=root.querySelector('#botThread'),status=root.querySelector('#botConversationStatus'),stop=root.querySelector('#stopBotWaiting');
 let conversation=null,messages=[],pending=null,uncertain=null,loading=true;
 input.value=ctx.botDraft||draft;input.oninput=()=>draft=input.value;
 const valid=()=>ctx.isCurrent();
 function paint(toEnd=false){if(!valid())return;const top=scroll.scrollTop,nearEnd=scroll.scrollHeight-scroll.clientHeight-top<70;thread.innerHTML=messageMarkup(messages)+(pending&&!pending.receiptRetry&&messages.at(-1)?.content!==pending.message?`<div class="user-message">${esc(pending.message)}</div>`:'')+(pending?'<div class="thinking-row" role="status"><span class="spinner"></span><span>Working…</span></div>':'');bindDraftReviews(ctx,thread);welcome.classList.toggle('hide',messages.length>0||!!ctx.botHasActivity);input.disabled=loading||!!pending;input.readOnly=!!uncertain;root.querySelectorAll('[data-bot-prompt]').forEach(b=>b.disabled=loading||!!pending||!!uncertain);form.querySelector('[type=submit]').disabled=loading||!!pending;stop.classList.toggle('hide',!pending);scroll.scrollTop=toEnd||nearEnd?scroll.scrollHeight:top;}
 async function reload(){loading=true;paint();status.textContent='Loading your Mindbot history…';try{const saved=await history('mindbot',null,{signal:ctx.signal});if(!valid())return;conversation=saved.conversation;messages=saved.messages;status.textContent=saved.pending_turns.length?'An earlier request is processing or uncertain. Refresh history before another instruction.':'';if(uncertain){status.textContent='Saved history refreshed. Retrieve the exact request outcome before another instruction.';addRetry();}}catch(e){if(!valid()||e.code==='request_cancelled')return;status.innerHTML=`${esc(e.message)} <button class="button-outline" id="retryBotConversation">Retry history</button>`;status.querySelector('#retryBotConversation').onclick=reload;}finally{if(valid()){if(uncertain&&!status.querySelector('[data-bot-exact-retry]'))addRetry();loading=false;paint();}}}
 async function send(message,exact=null){
  if(pending||loading||!message.trim())return;
  if(!conversation){status.textContent='Load your saved history before sending.';return;}
  if(uncertain&&!exact){status.textContent='This earlier request has an uncertain outcome. Refresh history or retry the exact request before sending a new instruction.';addRetry();return;}
  const request={controller:new AbortController(),message:message.trim(),receiptRetry:!!exact};pending=request;draft='';input.value='';paint(true);status.textContent='';
  const abort=()=>request.controller.abort();ctx.signal.addEventListener('abort',abort,{once:true});
  let body=exact;
  try{
   await ctx.profileReady;if(!valid())return;if(ctx.profileError)throw new Error('Saved profile context could not be loaded. Retry it before sending.');
   body??={conversation_id:conversation.conversation_id,message:message.trim(),idempotency_key:key(),expected_profile_version:ctx.profile?.version??null};
   const result=await sendTurn(body,{signal:request.controller.signal});if(!valid())return;uncertain=null;
   const saved=await history('mindbot',null,{signal:request.controller.signal});if(!valid())return;messages=saved.messages;
   status.textContent=['processing','uncertain'].includes(result.turn.status)?'The server has not confirmed a final outcome. Refresh history; this instruction was not replayed.':result.turn.status==='failed'?'This request failed. Review its saved result before sending a new question.':'';
   await ctx.refreshProfile();await ctx.onBotResult?.(result);
  }catch(e){if(!valid())return;if(e.status===409){await ctx.refreshProfile();if(!valid())return;}input.value=message;draft=message;status.textContent=e.message+' The request was not automatically retried.';if(body&&(!e.status||e.status>=500)){uncertain=body;addRetry();}else if(e.status)uncertain=null;}
  finally{ctx.signal.removeEventListener('abort',abort);if(pending===request)pending=null;paint();}
 }
 function addRetry(){const button=document.createElement('button');button.type='button';button.className='button-outline';button.textContent='Retry exact request';button.dataset.botExactRetry='true';button.onclick=()=>{if(uncertain)send(uncertain.message,uncertain);};status.append(' ',button);}
 form.onsubmit=event=>{event.preventDefault();send(input.value);};
 input.onkeydown=event=>{if(event.key==='Enter'&&!event.shiftKey){event.preventDefault();form.requestSubmit();}};
 stop.onclick=()=>pending?.controller.abort();
 root.querySelectorAll('[data-bot-prompt]').forEach(b=>b.onclick=()=>{input.value=b.dataset.botPrompt;draft=input.value;input.focus();});
 const refresh=document.createElement('button');refresh.type='button';refresh.className='button-outline';refresh.textContent='Refresh history';refresh.onclick=()=>{if(!pending)reload();};root.querySelector('.agent-tools').prepend(refresh);
 paint();await reload();
}
