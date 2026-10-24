import {api,session,setCredentialProvider,clearPrivateRequests,endLocalSession} from './client.js';
// Managed login uses the provider's maintained UI; the app never receives passwords.
// Official script integration: https://clerk.com/docs/js-frontend/getting-started/quickstart
let config=null,clerk=null,identity=null,clerkIdentity=null,listener=null;
const event=(name,detail)=>window.dispatchEvent(new CustomEvent(name,{detail}));
export const authenticated=()=>identity!==null;
export const authMode=()=>config?.mode;
export const accountName=()=>clerk?.user?.fullName||clerk?.user?.firstName||'';
export function clearIdentity(){identity=null;clearPrivateRequests();event('minder-private-clear');}
function script(src,key){return new Promise((resolve,reject)=>{const tag=document.createElement('script'),timer=setTimeout(()=>{tag.remove();reject(new Error('The sign-in service took too long to load.'));},12000);tag.src=src;tag.async=true;tag.crossOrigin='anonymous';if(key)tag.setAttribute('data-clerk-publishable-key',key);tag.onload=()=>{clearTimeout(timer);resolve();};tag.onerror=()=>{clearTimeout(timer);tag.remove();reject(new Error('The sign-in service could not be loaded.'));};document.head.append(tag);});}
export async function initializeAuth(){
 config=await api('auth/config',undefined,'GET',{public:true});
 if(!['local','managed'].includes(config.mode)||typeof config.anonymous_session_allowed!=='boolean')throw new Error('The sign-in configuration could not be validated.');
 if(config.mode==='local'&&config.anonymous_session_allowed){await session();const result=await api('auth/session');identity=result.user.id;event('minder-authenticated',{mode:'local'});return true;}
 if(config.mode!=='managed'||config.provider!=='clerk'||config.status!=='configured'||!/^pk_(test|live)_/.test(config.publishable_key||'')){setCredentialProvider(async()=>null);throw new Error('Managed sign-in is not configured. Please retry when the service is available.');}
 if(!clerk){
   const encoded=config.publishable_key.split('_')[2];let domain;try{domain=atob(encoded).replace(/\$$/,'');}catch{throw new Error('The sign-in configuration is invalid.');}
   if(!/^[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?\.[a-z]{2,}$/i.test(domain))throw new Error('The sign-in configuration is invalid.');
   await script(`https://${domain}/npm/@clerk/ui@1/dist/ui.browser.js`);
   await script(`https://${domain}/npm/@clerk/clerk-js@6/dist/clerk.browser.js`,config.publishable_key);
   clerk=window.Clerk;if(!clerk?.load)throw new Error('The sign-in service is unavailable.');
   await clerk.load({ui:{ClerkUI:window.__internal_ClerkUICtor}});
 }
 setCredentialProvider(async()=>clerk.session?.getToken()??null);
 listener?.();
 // Session ID covers switching between sessions for the same user as well.
 clerkIdentity=clerk.session?.id||null;
 listener=clerk.addListener(({session:active})=>{const next=active?.id||null;if(next===clerkIdentity)return;clerkIdentity=next;clearIdentity();event('minder-auth-changed');});
 if(!clerk.session)return false;
 const result=await api('auth/session');if(result.authenticated!==true||typeof result.user?.id!=='string')throw new Error('The signed-in identity could not be verified.');identity=result.user.id;event('minder-authenticated',{mode:'managed'});return true;
}
export function mountSignIn(root){if(!clerk)throw new Error('The sign-in service is unavailable.');clerk.mountSignIn(root,{routing:'hash',afterSignInUrl:location.origin+'/',afterSignUpUrl:location.origin+'/'});}
export async function signOut(){clearIdentity();if(config?.mode==='managed'){if(!clerk)throw new Error('The sign-out service is unavailable.');await clerk.signOut();clerkIdentity=null;}else endLocalSession();event('minder-signed-out');}
