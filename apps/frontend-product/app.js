import {optional} from './client.js';
import {initializeAuth,authenticated,authMode,accountName,mountSignIn,signOut,clearIdentity} from './auth.js';
import {card,esc,showError} from './ui.js';
import {hydrateIcons,svg} from './icons.js';
import {minder,clearConversation,invalidateConversation} from './pages/minder.js';
import {mindbots} from './pages/mindbots.js';
import {careers} from './pages/careers.js';
import {myPath} from './pages/my-path.js';
let view=document.querySelector('#view'),generation=0,routeController=null,activeContext=null,navigationPending=false;
let selectedRole=sessionStorage.getItem('minder-product-role')||'';
const labels={overview:'Overview',profile:'My profile',minder:'Minder Chat',mindbots:'MindBot','career-match':'Career Match',tasks:'Tasks',progress:'Progress',roadmap:'Roadmap & Skills',news:'News & Trends',future:'Future Explorer'};
async function render(){
  if(!authenticated())return showSignIn();
  if(navigationPending)return;const leaving=activeContext;if(leaving?.beforeLeave){navigationPending=true;let allowed;try{allowed=await leaving.beforeLeave();}finally{navigationPending=false;}if(!allowed){window.history.replaceState(null,'',leaving.routeHash);return;}}
  const current=++generation;routeController?.abort();routeController=new AbortController();
  document.querySelectorAll('.sidebar,.topbar,.chat-page .content-col').forEach(n=>n.inert=false);
  const stage=document.createElement('main');stage.id='view';stage.className='page-main product-page';stage.setAttribute('aria-busy','true');view.replaceWith(stage);view=stage;
  const route=location.hash.slice(1)||'minder', [page,...segments]=route.split('/'),tab=segments.join('/');document.querySelector('#globalNewChat').hidden=page!=='minder';document.querySelector('#pageTitle').textContent=({careers:'Careers','my-path':'My Path'}[page]||labels[page]||'Minder');document.querySelector('#error').hidden=true;
  document.querySelectorAll('.nav-link').forEach(a=>{const active=(a.hash||'').split('/')[0]==='#'+page;a.classList.toggle('active',active);a.setAttribute('aria-current',active?'page':'false');});
  const ctx={routeHash:location.hash,view:stage,signal:routeController.signal,profile:null,profileStatus:'loading',profileError:null,render,isCurrent:()=>current===generation&&!ctx.authFailed};
  Object.defineProperty(ctx,'selectedRole',{get:()=>selectedRole,set:value=>{selectedRole=value;sessionStorage.setItem('minder-product-role',value);}});
  ctx.failAuth=error=>{if(current!==generation||ctx.authFailed)return;ctx.authFailed=true;invalidateConversation();ctx.profile=null;routeController.abort();document.querySelector('.account-name').textContent='Your workspace';document.querySelector('#proposalBadge').hidden=true;stage.innerHTML=card('Session unavailable','<p>Your session could not be authorized. No saved workspace information is shown.</p><button id="retryView">Reload workspace</button>');stage.setAttribute('aria-busy','false');stage.dataset.rendered=page;document.querySelector('#retryView').onclick=render;showError(error);};
  if(['careers','my-path'].includes(page)){document.querySelector('#exploreChildren').hidden=false;document.querySelector('#exploreToggle').setAttribute('aria-expanded','true');}document.querySelector('#exploreToggle').classList.toggle('active',['careers','my-path'].includes(page));
  activeContext=ctx;
  ctx.refreshProfile=async()=>{ctx.profileStatus='loading';ctx.profileError=null;try{const profile=await optional('profile',{signal:ctx.signal});if(!ctx.isCurrent())return null;ctx.profile=profile;ctx.profileStatus='ready';document.querySelector('.account-name').textContent=profile?.career_context?.display_name||accountName()||'Your workspace';return profile;}catch(e){if(!ctx.isCurrent()||e.code==='request_cancelled')return null;ctx.profileError=e;ctx.profileStatus='error';if([401,403].includes(e.status))ctx.failAuth(e);return null;}finally{if(ctx.isCurrent())ctx.onProfileLoaded?.();}};
  ctx.profileReady=ctx.refreshProfile();
  stage.innerHTML='<p role="status">Loading your workspace…</p>';
  try{
    if(page==='minder')await minder(ctx,decodeURIComponent(tab));else if(page==='mindbots')await mindbots(ctx);
    else{await ctx.profileReady;if(!ctx.isCurrent())return;if(ctx.profileError)throw ctx.profileError;if(page==='careers'||page==='career-match'){await careers(ctx,tab||'matches');}else if(page==='my-path'||['roadmap','tasks','progress'].includes(page)){await myPath(ctx,tab||({roadmap:'roadmap',tasks:'next',progress:'progress'}[page])||'next');}else{const pages=await import('./pages/workspace.js');if(ctx.isCurrent())await pages.workspace(ctx,page,tab);}}
    if(ctx.isCurrent())hydrateIcons(stage);
  }catch(e){if(!ctx.isCurrent()||e.code==='request_cancelled')return;stage.innerHTML=card('Unable to load this view','<p>You can retry this view or open another page.</p><button id="retryView">Try again</button>');document.querySelector('#retryView').onclick=render;showError(e);}
  finally{if(ctx.isCurrent()){stage.setAttribute('aria-busy','false');stage.dataset.rendered=page;}}
}
window.addEventListener('minder-auth-lost',event=>{activeContext?.failAuth(event.detail);clearIdentity();showSignIn('Your session is no longer authorized. Sign in again to continue.');});
window.addEventListener('minder-private-clear',()=>{generation++;routeController?.abort();invalidateConversation();activeContext=null;selectedRole='';window.history.replaceState(null,'','#minder');document.querySelector('#globalNewChat').hidden=true;for(const name of ['minder-product-role','minder-product-search','minder-product-document-deletes'])sessionStorage.removeItem(name);document.querySelector('#proposalBadge').hidden=true;document.querySelector('.account-name').textContent='Your workspace';document.querySelector('#accountOptions')?.setAttribute('hidden','');document.querySelector('#error').hidden=true;document.querySelector('#appToast').classList.remove('show');view.innerHTML='';});
window.addEventListener('minder-auth-changed',()=>start());
window.addEventListener('minder-signed-out',()=>showSignIn('You have signed out.'));
const menu=document.createElement('button');menu.className='icon-button mobile-menu';menu.ariaLabel='Open navigation';menu.setAttribute('aria-controls','workspaceNav');menu.setAttribute('aria-expanded','false');menu.innerHTML=svg('grid');document.querySelector('.breadcrumb').prepend(menu);
const nav=document.querySelector('.sidebar'),tooltip=document.querySelector('#navTooltip');
function setNavigation(open){nav.classList.toggle('mobile-open',open);menu.setAttribute('aria-expanded',String(open));document.querySelector('#navBackdrop').hidden=!open;tooltip.hidden=true;if(open)document.querySelector('#closeNavigation').focus();}
menu.onclick=()=>setNavigation(!nav.classList.contains('mobile-open'));
document.querySelector('#closeNavigation').onclick=()=>{setNavigation(false);menu.focus();};document.querySelector('#navBackdrop').onclick=()=>{setNavigation(false);menu.focus();};
for(const control of nav.querySelectorAll('.nav-link,#globalNewChat,#accountMenu')){
 const label=control.getAttribute('aria-label')||control.querySelector('span:nth-child(2)')?.textContent.trim()||'New conversation';control.setAttribute('aria-label',label);control.dataset.navLabel=label;
 function showLabel(){if(nav.classList.contains('mobile-open')||matchMedia('(max-width:730px)').matches)return;const rect=control.getBoundingClientRect();tooltip.textContent=label;tooltip.style.left=(rect.right+12)+'px';tooltip.style.top=Math.max(8,Math.min(innerHeight-44,rect.top+(rect.height-30)/2))+'px';tooltip.hidden=false;control.setAttribute('aria-describedby','navTooltip');}
 control.addEventListener('mouseenter',showLabel);control.addEventListener('focus',showLabel);for(const type of ['mouseleave','blur'])control.addEventListener(type,()=>{tooltip.hidden=true;control.removeAttribute('aria-describedby');});
}
document.querySelector('#exploreToggle').onclick=()=>{const toggle=document.querySelector('#exploreToggle'),children=document.querySelector('#exploreChildren');children.hidden=!children.hidden;toggle.setAttribute('aria-expanded',String(!children.hidden));};
const search=document.querySelector('#globalSearch');search.placeholder='Find a career role…';search.onkeydown=e=>{if(e.key==='Enter'){sessionStorage.setItem('minder-product-search',search.value);if(location.hash==='#careers/matches')render();else location.hash='careers/matches';}};
document.querySelector('#globalNewChat').onclick=()=>{if(clearConversation()===false)return;setNavigation(false);if(location.hash==='#minder')render();else location.hash='minder';};
const accountOptions=document.createElement('div');accountOptions.id='accountOptions';accountOptions.className='account-options';accountOptions.hidden=true;accountOptions.innerHTML='<a class="button-outline" href="#profile">My profile</a><button type="button" class="button-outline" id="signOut">Sign out</button>';document.body.append(accountOptions);
document.querySelector('#accountMenu').onclick=()=>{accountOptions.hidden=!accountOptions.hidden;};
accountOptions.querySelector('a').onclick=()=>{accountOptions.hidden=true;};
document.querySelector('#signOut').onclick=async event=>{const button=event.currentTarget;button.disabled=true;try{await signOut();}catch(e){showSignIn('Your private workspace is cleared. The sign-out service could not confirm logout; retry sign-out.');showError(e);}finally{button.disabled=false;}};
document.addEventListener('keydown',event=>{if(event.key==='Escape')accountOptions.hidden=true;});
window.addEventListener('minder-refresh',render);
window.addEventListener('hashchange',()=>{setNavigation(false);if(authenticated())render();});
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&nav.classList.contains('mobile-open')){setNavigation(false);menu.focus();}});
let toastTimer;window.addEventListener('minder-saved',event=>{const toast=document.querySelector('#appToast');toast.textContent=event.detail;toast.classList.add('show');clearTimeout(toastTimer);toastTimer=setTimeout(()=>toast.classList.remove('show'),3500);});
hydrateIcons();
let authStarting=false;
function showSignIn(message='Sign in to your private Minder workspace.'){
 view.innerHTML=`<section class="auth-gate"><h1>Welcome to Minder</h1><p>${esc(message)}</p><div id="managedSignIn"></div><button type="button" class="button-outline" id="retrySignIn">${authMode()==='local'?'Open local demonstration':'Retry sign-in service'}</button></section>`;
 document.querySelector('#retrySignIn').onclick=start;
 if(authMode()==='managed'){try{mountSignIn(document.querySelector('#managedSignIn'));}catch(e){document.querySelector('#managedSignIn').textContent=e.message;}}
}
async function start(){
 if(authStarting)return;authStarting=true;view.innerHTML=card('Opening your workspace','<p role="status">Connecting…</p>');
 try{const ready=await initializeAuth();if(!ready){showSignIn();return;}document.querySelector('.account-sub').textContent=authMode()==='local'?'Local demonstration':'Private account';await render();}
 catch(e){showSignIn(e.message);showError(e);}finally{authStarting=false;}
}
await start();
