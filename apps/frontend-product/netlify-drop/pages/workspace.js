import {profilePage} from './profile.js';
import {careerPage} from './career.js';
import {explorePage} from './explore.js';
export async function workspace(ctx,page,tab='overview'){
 ctx.view.className='page-main product-page';
 if(page==='profile')return profilePage(ctx,tab);
 if(page==='career-match')return careerPage(ctx,page);
 return explorePage(ctx,page);
}
