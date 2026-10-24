import {api,key} from './client.js';
export function validateHistory(value,channel){
 if(!value||typeof value.conversation?.conversation_id!=='string'||value.conversation.channel!==channel||!Array.isArray(value.messages)||value.messages.some(m=>!m||typeof m.message_id!=='string'||!Number.isInteger(m.sequence)||!['user','assistant'].includes(m.role)||typeof m.content!=='string'))throw new Error('Saved conversation could not be validated.');return value;
}
export async function history(channel,id,options={}){
 let page=channel==='mindbot'?await api('product/mindbot-conversation',undefined,'GET',options):await api('product/conversation',{conversation_id:id},'POST',options);
 validateHistory(page,channel);const messages=[...page.messages];
 while(page.has_more){const next=await api('product/conversation',{conversation_id:page.conversation.conversation_id,after_sequence:page.next_after_sequence,limit:100},'POST',options);validateHistory(next,channel);if(next.next_after_sequence<=page.next_after_sequence)throw new Error('Conversation pagination could not be validated.');messages.push(...next.messages);page=next;}
 return {...page,messages};
}
export async function listConversations(options={}){const result=await api('product/conversations',undefined,'GET',options);if(!Array.isArray(result.conversations)||result.conversations.some(c=>c.channel!=='minder'||typeof c.conversation_id!=='string'))throw new Error('Saved conversations could not be validated.');return result.conversations;}
export const createConversation=body=>api('product/conversations',body||{idempotency_key:key()});
export const deleteConversation=body=>api('product/conversation',body,'DELETE');
export async function sendTurn(body,options={}){const result=await api('product/conversation-turn',body,'POST',options);if(!result.conversation||!['completed','failed','processing','uncertain'].includes(result.turn?.status)||!Array.isArray(result.messages))throw new Error('The conversation outcome could not be validated. Reload saved history before sending another request.');return result;}
