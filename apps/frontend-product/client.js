// Same-origin only. The private session credential never enters URLs or logs.
let token = sessionStorage.getItem('minder-product-token');
export class ApiError extends Error {
  constructor(status, value) {
    super(status === 409 ? 'This saved state changed. Refresh and review before trying again.' :
      status === 401 ? 'Your session is no longer available. Start a new session.' :
      status === 404 ? 'This information is not available yet.' :
      status === 422 ? 'Check your entries. The change could not be accepted.' :
      status === 429 ? 'The service is busy. Try again later.' : 'The request could not be completed.');
    this.status=status; this.code=value.code; this.requestId=value.request_id;
  }
}
export const REQUEST_TIMEOUTS={read:12000,write:30000,chat:90000};
export class RequestError extends Error {
  constructor(code){super(code==='request_cancelled'?'Stopped waiting. Server processing may still finish.':code==='request_timeout'?'The request took too long. Review saved state before retrying.':'Connection interrupted. Review saved state before retrying.');this.code=code;}
}
export async function api(path, body, method=body===undefined?'GET':'POST', options={}) {
  const controller=new AbortController();let timedOut=false;
  const abort=()=>controller.abort();
  if(options.signal?.aborted)abort();else options.signal?.addEventListener('abort',abort,{once:true});
  const timeoutMs=options.timeoutMs??(path==='chat'?REQUEST_TIMEOUTS.chat:method==='GET'?REQUEST_TIMEOUTS.read:REQUEST_TIMEOUTS.write);
  const timer=setTimeout(()=>{timedOut=true;controller.abort();},timeoutMs);
  try {
    const response=await fetch('/api/'+path,{method,signal:controller.signal,headers:{'Content-Type':'application/json',...(token?{Authorization:'Bearer '+token}:{})},...(body===undefined?{}:{body:JSON.stringify(body)})});
    let value;try{value=await response.json();}catch(e){if(controller.signal.aborted)throw e;throw new Error('The server returned an unreadable response.');}
    if(!response.ok)throw new ApiError(response.status,value);
    if(!value||typeof value!=='object')throw new Error('The server returned an invalid response.');
    const writes=['direct-action','proposal-decision','undo','plans','agent-settings','product/direction','product/tasks','product/task-action','product/resource-state','product/resource-to-plan','product/intake-correction','product/document-upload','product/document-delete'];
    if(method==='PUT'||(method==='POST'&&writes.includes(path)))window.dispatchEvent(new CustomEvent('minder-saved',{detail:path==='product/document-delete'?'File deleted.':value.status==='rejected'?'Proposal rejected.':'Changes saved.'}));
    return value;
  }catch(e){if(controller.signal.aborted)throw new RequestError(timedOut?'request_timeout':'request_cancelled');if(e instanceof TypeError)throw new RequestError('connection_interrupted');throw e;}
  finally{clearTimeout(timer);options.signal?.removeEventListener('abort',abort);}
}
export async function session() {
  if(!token) {const result=await api('session',{}); if(typeof result.token!=='string') throw new Error('Session unavailable.'); token=result.token;sessionStorage.setItem('minder-product-token',token);}
}
export async function optional(path) {try{return await api(path);}catch(e){if(e.status===404)return null;throw e;}}
export const key=()=>crypto.randomUUID();
export function validateChat(result) {
  const categories=['external_fact','user_reported','calculated_assessment','proposed_action','limitation'];
  const strings=arr=>Array.isArray(arr)&&arr.every(x=>typeof x==='string');
  const validSource=s=>s&&['source_id','uri','sha256','version','geography','available_at','evidence_type'].every(k=>typeof s[k]==='string');
  if(!result||!['integration_mode','context_version','profile_version'].every(k=>typeof result[k]==='string')||!Array.isArray(result.statements)||!['available','unavailable'].includes(result.provider?.status)||result.behaviour_policy_version!=='minder-grounding-privacy-v1'||result.action_status!=='no_mutation_requested_or_executed'||result.statements.some(s=>!s||typeof s.id!=='string'||typeof s.text!=='string'||!strings(s.evidence_ids)||!categories.includes(s.category)||!Array.isArray(s.sources)||!s.sources.every(validSource))) throw new Error('The answer could not be validated. Please try again.');
  return result;
}
