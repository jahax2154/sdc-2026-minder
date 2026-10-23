import {card,esc} from '../ui.js';
export async function workspace(ctx,page){ctx.view.className='page-main product-page';ctx.view.innerHTML=`<h1>${esc(page)}</h1>${card('Connecting your workspace','<p>The shared frontend is ready. Profile and Explore screens are being connected to the delivered API capabilities.</p><a href="#minder">Open Minder →</a>')}`;}
