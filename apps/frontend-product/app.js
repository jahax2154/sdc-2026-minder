import {session,optional} from './client.js';
import {card,esc,showError} from './ui.js';
import {hydrateIcons,svg} from './icons.js';
import {minder,clearConversation} from './pages/minder.js';
import {mindbots} from './pages/mindbots.js';
const view=document.querySelector('#view');
const ctx={view,profile:null,selectedRole:sessionStorage.getItem('minder-product-role')||'',render,refreshProfile:async()=>{ctx.profile=await optional('profile');}};
let generation=0,rendering=false,queued=false;
const labels={overview:'Overview',profile:'My profile',minder:'Minder Chat',mindbots:'MindBot','career-match':'Career Match',tasks:'Tasks',progress:'Progress',roadmap:'Roadmap & Skills',news:'News & Trends',future:'Future Explorer'};
async function render(){
  if(rendering){queued=true;return;}rendering=true;
  const current=++generation;document.querySelector('#error').hidden=true;
  const page=location.hash.slice(1)||'minder';view.setAttribute('aria-busy','true');delete view.dataset.rendered;document.querySelector('#pageTitle').textContent=labels[page]||'Minder';
  document.querySelectorAll('.nav-link').forEach(a=>{a.classList.toggle('active',a.hash==='#'+page);a.setAttribute('aria-current',a.hash==='#'+page?'page':'false');});
  view.className='page-main product-page';view.innerHTML='<p role="status">Loading your workspace…</p>';
  try {
    await ctx.refreshProfile();if(current!==generation)return;
    document.querySelector('.account-name').textContent=ctx.profile?.career_context?.display_name||'Your workspace';
    if(page==='minder')await minder(ctx);else if(page==='mindbots')await mindbots(ctx);
    else {const pages=await import('./pages/workspace.js');if(current!==generation)return;await pages.workspace(ctx,page);}
    hydrateIcons(view);
  } catch(e) {view.innerHTML=card('Unable to load this view','<p>You can refresh or open another page. Your saved records are unchanged.</p><button id="retryView">Try again</button>');document.querySelector('#retryView').onclick=render;showError(e);}
  finally{view.setAttribute('aria-busy','false');view.dataset.rendered=page;rendering=false;if(queued){queued=false;await render();}}
}
const menu=document.createElement('button');menu.className='icon-button mobile-menu';menu.ariaLabel='Open navigation';menu.innerHTML=svg('grid');document.querySelector('.breadcrumb').prepend(menu);menu.onclick=()=>document.querySelector('.sidebar').classList.toggle('mobile-open');
const search=document.querySelector('#globalSearch');search.placeholder='Find a career role…';search.onkeydown=e=>{if(e.key==='Enter'){sessionStorage.setItem('minder-product-search',search.value);if(location.hash==='#career-match')render();else location.hash='career-match';}};
document.querySelector('#globalNewChat').onclick=()=>{clearConversation();location.hash='minder';render();};
document.querySelector('#accountMenu').onclick=()=>{location.hash='profile';};
window.addEventListener('minder-refresh',render);
window.addEventListener('hashchange',()=>{document.querySelector('.sidebar').classList.remove('mobile-open');render();});
document.addEventListener('keydown',e=>{if(e.key==='Escape')document.querySelector('.sidebar').classList.remove('mobile-open');});
let toastTimer;window.addEventListener('minder-saved',event=>{const toast=document.querySelector('#appToast');toast.textContent=event.detail;toast.classList.add('show');clearTimeout(toastTimer);toastTimer=setTimeout(()=>toast.classList.remove('show'),3500);});
hydrateIcons();
try{await session();await render();}catch(e){showError(e);}
