import {api} from './client.js';
import {BOT_AVATARS} from './bot-avatars.js';
export function validateIdentity(value){const p=value?.preferences;if(value?.contract_version!=='bot-preferences-v1'||typeof value.configured!=='boolean'||!p||typeof p.display_name!=='string'||!p.display_name.trim()||[...p.display_name].length>40||!BOT_AVATARS.some(a=>a.id===p.avatar_id)||!(p.version===null||typeof p.version==='string'))throw new Error('Saved Mindbot identity could not be validated.');return value;}
export const readIdentity=options=>api('product/bot-preferences',undefined,'GET',options).then(validateIdentity);
export const avatarPath=id=>BOT_AVATARS.find(a=>a.id===id)?.path||'assets/nimo-blue.png';
export async function saveIdentity(body,options){const result=validateIdentity(await api('product/bot-preferences',body,'PUT',options));window.dispatchEvent(new CustomEvent('minder-bot-preferences-saved',{detail:result}));return result;}
