// Retain a valid sibling-panel frame while a replacement read is pending.
export function beginPanelRefresh(ctx,body,samePanel){
 const view=ctx.view,focused=document.activeElement,focusId=body.contains(focused)?focused.id:null,selection=focusId&&typeof focused.selectionStart==='number'?[focused.selectionStart,focused.selectionEnd]:null,top=view.scrollTop;
 const status=document.createElement('span');status.className='panel-loading';status.role='status';status.textContent='Updating…';body.before(status);body.setAttribute('aria-busy','true');body.inert=true;
 view.querySelectorAll('.panel-refresh-error').forEach(el=>el.remove());
 const observer=new MutationObserver(()=>{body.inert=false;body.setAttribute('aria-busy','false');if(!ctx.panelFailed)body.dataset.ready='true';status.remove();observer.disconnect();if(samePanel){view.scrollTop=top;if(focusId&&(document.activeElement===document.body||document.activeElement===focused)){const next=body.querySelector('#'+CSS.escape(focusId));if(next){next.focus({preventScroll:true});if(selection)next.setSelectionRange?.(...selection);}}}});
 observer.observe(body,{childList:true});ctx.signal.addEventListener('abort',()=>{status.remove();observer.disconnect();},{once:true});
}
