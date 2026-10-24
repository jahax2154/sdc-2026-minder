import {session,optional} from './client.js';
import {card,esc,showError} from './ui.js';
import {hydrateIcons,svg} from './icons.js';
import {minder,clearConversation,invalidateConversation} from './pages/minder.js';
import {mindbots} from './pages/mindbots.js';
import {careers} from './pages/careers.js';
import {myPath} from './pages/my-path.js';
let view=document.querySelector('#view'),generation=0,routeController=null,activeContext=null;
let selectedRole=sessionStorage.getItem('minder-product-role')||'';
const labels={overview:'Overview',profile:'My profile',minder:'Minder Chat',mindbots:'MindBot','career-match':'Career Match',tasks:'Tasks',progress:'Progress',roadmap:'Roadmap & Skills',news:'News & Trends',future:'Future Explorer'};
async function render(){
  const current=++generation;routeController?.abort();routeController=new AbortController();
  document.querySelectorAll('.sidebar,.topbar,.chat-page .content-col').forEach(n=>n.inert=false);
  const stage=document.createElement('main');stage.id='view';stage.className='page-main product-page';stage.setAttribute('aria-busy','true');view.replaceWith(stage);view=stage;
  const route=location.hash.slice(1)||'minder', [page,...segments]=route.split('/'),tab=segments.join('/');document.querySelector('#globalNewChat').hidden=page!=='minder';document.querySelector('#pageTitle').textContent=({careers:'Careers','my-path':'My Path'}[page]||labels[page]||'Minder');document.querySelector('#error').hidden=true;
  document.querySelectorAll('.nav-link').forEach(a=>{const active=(a.hash||'').split('/')[0]==='#'+page;a.classList.toggle('active',active);a.setAttribute('aria-current',active?'page':'false');});
  const ctx={view:stage,signal:routeController.signal,profile:null,profileStatus:'loading',profileError:null,render,isCurrent:()=>current===generation&&!ctx.authFailed};
  Object.defineProperty(ctx,'selectedRole',{get:()=>selectedRole,set:value=>{selectedRole=value;sessionStorage.setItem('minder-product-role',value);}});
  ctx.failAuth=error=>{if(current!==generation||ctx.authFailed)return;ctx.authFailed=true;invalidateConversation();ctx.profile=null;routeController.abort();document.querySelector('.account-name').textContent='Your workspace';document.querySelector('#proposalBadge').hidden=true;stage.innerHTML=card('Session unavailable','<p>Your session could not be authorized. No saved workspace information is shown.</p><button id="retryView">Reload workspace</button>');stage.setAttribute('aria-busy','false');stage.dataset.rendered=page;document.querySelector('#retryView').onclick=render;showError(error);};
  if(['careers','my-path'].includes(page)){document.querySelector('#exploreChildren').hidden=false;document.querySelector('#exploreToggle').setAttribute('aria-expanded','true');}document.querySelector('#exploreToggle').classList.toggle('active',['careers','my-path'].includes(page));
  activeContext=ctx;
  ctx.refreshProfile=async()=>{ctx.profileStatus='loading';ctx.profileError=null;try{const profile=await optional('profile',{signal:ctx.signal});if(!ctx.isCurrent())return null;ctx.profile=profile;ctx.profileStatus='ready';document.querySelector('.account-name').textContent=profile?.career_context?.display_name||'Your workspace';return profile;}catch(e){if(!ctx.isCurrent()||e.code==='request_cancelled')return null;ctx.profileError=e;ctx.profileStatus='error';if([401,403].includes(e.status))ctx.failAuth(e);return null;}finally{if(ctx.isCurrent())ctx.onProfileLoaded?.();}};
  ctx.profileReady=ctx.refreshProfile();
  stage.innerHTML='<p role="status">Loading your workspace…</p>';
  try{
    if(page==='minder')await minder(ctx);else if(page==='mindbots')await mindbots(ctx);
    else{await ctx.profileReady;if(!ctx.isCurrent())return;if(ctx.profileError)throw ctx.profileError;if(page==='careers'||page==='career-match'){await careers(ctx,tab||'matches');}else if(page==='my-path'||['roadmap','tasks','progress'].includes(page)){await myPath(ctx,tab||({roadmap:'roadmap',tasks:'next',progress:'progress'}[page])||'next');}else{const pages=await import('./pages/workspace.js');if(ctx.isCurrent())await pages.workspace(ctx,page);}}
    if(ctx.isCurrent())hydrateIcons(stage);
  }catch(e){if(!ctx.isCurrent()||e.code==='request_cancelled')return;stage.innerHTML=card('Unable to load this view','<p>You can retry this view or open another page.</p><button id="retryView">Try again</button>');document.querySelector('#retryView').onclick=render;showError(e);}
  finally{if(ctx.isCurrent()){stage.setAttribute('aria-busy','false');stage.dataset.rendered=page;}}
}
window.addEventListener('minder-auth-lost',event=>activeContext?.failAuth(event.detail));
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
document.querySelector('#globalNewChat').onclick=()=>{if(clearConversation()===false)return;setNavigation(false);location.hash='minder';render();};
document.querySelector('#accountMenu').onclick=()=>{location.hash='profile';};
window.addEventListener('minder-refresh',render);
window.addEventListener('hashchange',()=>{setNavigation(false);render();});
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&nav.classList.contains('mobile-open')){setNavigation(false);menu.focus();}});
let toastTimer;window.addEventListener('minder-saved',event=>{const toast=document.querySelector('#appToast');toast.textContent=event.detail;toast.classList.add('show');clearTimeout(toastTimer);toastTimer=setTimeout(()=>toast.classList.remove('show'),3500);});
hydrateIcons();
async function start(){view.innerHTML=card('Opening your workspace','<p role="status">Connecting…</p>');try{await session();await render();}catch(e){view.innerHTML=card('Unable to open your workspace','<p>The service could not be reached. You can try again.</p><button id="retrySession">Try again</button>');document.querySelector('#retrySession').onclick=start;showError(e);}}
await start();
