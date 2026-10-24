// Export-only interface access. No account, token, provider or authentication is simulated.
export const authenticated=()=>true;
export const authMode=()=> 'preview';
export const accountName=()=> 'Avery Lim';
export async function initializeAuth(){return true;}
export function clearIdentity(){}
export function mountSignIn(root){root.textContent='Interface preview — live services unavailable. No account is signed in.';}
export async function signOut(){throw new Error('This interface preview has no signed-in account.');}
