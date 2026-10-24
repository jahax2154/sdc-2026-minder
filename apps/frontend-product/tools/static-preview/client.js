import {profile,roles,plan,direction,progress,requirement,starter,overview,settings,conversation} from './example-data.js';
export class ApiError extends Error{constructor(){super('Interface preview — live services unavailable. This action was not sent or saved.');this.status=503;this.code='static_preview_read_only';}}
export class RequestError extends Error{constructor(code='request_cancelled'){super('Preview navigation cancelled.');this.code=code;}}
export const REQUEST_TIMEOUTS={read:0,write:0,chat:0};
export const key=()=>globalThis.crypto?.randomUUID?.()||'preview-'+Math.random().toString(36).slice(2);
export function clearPrivateRequests(){} export function setCredentialProvider(){} export function endLocalSession(){}
export async function session(){throw new ApiError();}
const copy=value=>structuredClone(value);
const history=channel=>({conversation:channel==='mindbot'?{...conversation,conversation_id:'example-mindbot',channel:'mindbot',title:'Example Mindbot history'}:conversation,messages:channel==='minder'?[{message_id:'example-user-prompt',sequence:1,role:'user',content:'Example prompt: help me plan a small project. Live AI replies are unavailable in this preview.'}]:[],pending_turns:[],has_more:false,next_after_sequence:0});
// Explicit read allowlist. Every write, AI request, upload, login and scheduled action fails closed.
export async function api(path,body,method=body===undefined?'GET':'POST',options={}){
 if(options.signal?.aborted)throw new RequestError();
 let value;
 if(method==='GET'){
  const values={'profile':profile,'product/direction':{direction},'plans':{plans:[plan]},'plan-designs':{designs:[]},'product/progress':progress,'product/generations':{generations:[]},'product/views/overview':{data:overview},'product/bot-preferences':{contract_version:'bot-preferences-v1',configured:true,preferences:{display_name:'My Bot (example)',avatar_id:'nimo-blue',version:'example-bot-v1'}},'agent-settings':settings,'proposals':{proposals:[]},'agents':{notices:[],events:[],deployment_scheduler_verified:false},'action-history':{history:[]},'product/conversations':{conversations:[conversation]},'product/mindbot-conversation':history('mindbot'),'product/documents':{documents:[],storage:{status:'unavailable'},limits:{max_files:3,max_user_bytes:30000000,max_file_bytes:10000000},usage:{file_count:0,stored_or_reserved_bytes:0}},'product/minder-handoffs':{events:[]},'assessment-reference':null};
  if(Object.hasOwn(values,path))value=values[path];else throw new ApiError();
 }else if(method==='POST'){
  if(path==='roles'){const query=String(body?.query||'').toLowerCase(),rows=roles.filter(r=>(r.label+' '+r.role_id).toLowerCase().includes(query));value={roles:rows.slice(body?.offset||0,(body?.offset||0)+(body?.limit||50)),total:rows.length,offset:body?.offset||0,catalogue_order_not_rank:true};}
  else if(path==='role-requirements')value=requirement(body?.role_id);
  else if(path==='role-evidence')value={records:[],passages:[],forecast:null,forecast_error:'forecast_service_unavailable'};
  else if(path==='career-context')value={statements:[],limitations:['Static example — live assessed context unavailable.']};
  else if(path==='product/starter-recommendations')value=starter;
  else if(path==='product/views/career-match')throw new ApiError();
  else if(path==='product/conversations-search'){const rows=conversation.title.toLowerCase().includes(String(body?.query||'').toLowerCase())?[conversation]:[];value={contract_version:'conversation-search-v1',query:body?.query||'',search_scope:'title_and_visible_messages',conversations:rows,offset:0,limit:20,has_more:false,next_offset:null};}
  else if(path==='product/conversation')value=history('minder');
  else throw new ApiError();
 }else throw new ApiError();
 return copy(value);
}
export async function optional(path,options={}){return api(path,undefined,'GET',options);}
export function validateChat(){throw new ApiError();}
