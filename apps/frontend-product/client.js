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
export async function api(path, body, method=body===undefined?'GET':'POST') {
  const response=await fetch('/api/'+path,{method,headers:{'Content-Type':'application/json',...(token?{Authorization:'Bearer '+token}:{})},...(body===undefined?{}:{body:JSON.stringify(body)})});
  let value; try {value=await response.json();} catch {throw new Error('The server returned an unreadable response.');}
  if(!response.ok) throw new ApiError(response.status,value);
  if(!value || typeof value!=='object') throw new Error('The server returned an invalid response.');
  return value;
}
export async function session() {
  if(!token) {const result=await api('session',{}); if(typeof result.token!=='string') throw new Error('Session unavailable.'); token=result.token;sessionStorage.setItem('minder-product-token',token);}
}
export async function optional(path) {try{return await api(path);}catch(e){if(e.status===404)return null;throw e;}}
export const key=()=>crypto.randomUUID();
export function validateChat(result) {
  const categories=['external_fact','user_reported','calculated_assessment','proposed_action','limitation'];
  if(!Array.isArray(result.statements)||!['available','unavailable'].includes(result.provider?.status)||result.behaviour_policy_version!=='minder-grounding-privacy-v1'||result.action_status!=='no_mutation_requested_or_executed'||result.statements.some(s=>typeof s.text!=='string'||!categories.includes(s.category)||!Array.isArray(s.sources))) throw new Error('The answer could not be validated. Please try again.');
  return result;
}
