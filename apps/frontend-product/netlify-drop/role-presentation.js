import {api} from './client.js';
import {esc,source} from './ui.js';
let catalogueCache=null;
window.addEventListener('minder-private-clear',()=>{catalogueCache=null;});
export async function roleCatalogue(ctx){
 if(catalogueCache)return catalogueCache;
 const roles=[];let total=Infinity;
 while(roles.length<total){const page=await api('roles',{query:'',offset:roles.length,limit:50},'POST',{signal:ctx.signal});if(!Array.isArray(page.roles)||!Number.isInteger(page.total)||(!page.roles.length&&roles.length<page.total))throw new Error('The career catalogue could not be read. Retry this section.');roles.push(...page.roles);total=page.total;}
 if(ctx.isCurrent())catalogueCache=roles;return roles;
}
export function validateRole(value){
 const d=value?.display;
 if(!value?.role?.role_id||d?.version!=='role-display-v1'||d.role_id!==value.role.role_id||!Array.isArray(d.skills)||d.skills.some(s=>!s.subject_id||!Array.isArray(s.measurements)||!s.personal_evidence))throw new Error('Career skill information could not be validated. Retry this section.');return value;
}
export const skillLabel=s=>s.label_status==='available'&&s.label?s.label:'Skill name unavailable';
export function measurements(skill){return skill.measurements.map(m=>`<div class="role-measure"><strong>${esc(m.label)}: ${m.availability==='available'?esc(typeof m.value==='object'?JSON.stringify(m.value):m.value):'Unavailable'}</strong><p>${esc(m.explanation)}</p>${source({...m.source,title:m.source.title||'O*NET occupational reference'})}</div>`).join('')||'<p>No occupational measurements supplied.</p>';}
const personalLabels={not_assessed:'Not assessed',recorded_unassessed:'Notes recorded · unassessed',anchored_evidence_recorded:'Anchored evidence recorded',needs_clarification:'Evidence needs clarification'};
export function personalEvidence(skill){const p=skill.personal_evidence;return `<div class="personal-evidence"><strong>Your evidence: ${esc(personalLabels[p.status]||'Status unavailable')}</strong><p>${esc(p.explanation)}</p><small>${esc(p.recorded_count)} supporting records · ${esc(p.anchored_count)} anchored records</small></div>`;}
export function skillsTable(value){validateRole(value);return `<p>${esc(value.display.explanation)}</p><div class="comparison-wrap" tabindex="0" aria-label="Scrollable skill evidence"><table class="skills-table"><thead><tr><th scope="col">Skill</th><th scope="col">Occupational reference</th><th scope="col">Your evidence</th></tr></thead><tbody>${value.display.skills.map(s=>`<tr data-subject-id="${esc(s.subject_id)}"><th scope="row">${esc(skillLabel(s))}${s.label_source?source({...s.label_source,title:'Skill name source · O*NET'}):''}</th><td>${measurements(s)}</td><td>${personalEvidence(s)}<a class="text-link" href="#profile/skills">Review skill evidence</a></td></tr>`).join('')}</tbody></table></div><p class="fine-note">${esc(value.display.measurement_rule)}</p>`;}
const period=p=>p?.label||[p?.start,p?.end].filter(Boolean).join(' – ')||'Not supplied';
const missingLabels={insufficient_history:'Not enough historical observations',no_role_mapping:'No supported mapping for this career',unsupported_geography:'Geography is not supported',forecast_not_available:'A forecast is not available'};
export function forecastMarkup(evidence){
 const f=evidence.forecast;
 if(evidence.forecast_error)return '<h3>Future evidence could not be loaded</h3><p>Current observations remain available. Retry this outlook to load the forecast status.</p>';
 if(!f)return '<h3>Future evidence unavailable</h3><p>No forecast result was supplied for this career.</p>';
 if(f.kind!=='forecast'||f.entity_type!=='role'||f.entity_id!==evidence.role.role_id)throw new Error('Forecast scope could not be validated.');
 return `<h3>${f.status==='available'?'Source forecast':'Future evidence unavailable'}</h3><p>${esc(f.explanation)}</p><p>Target period: ${esc(period(f.target_period))}</p><p>Scope: ${esc(f.geography)} · ${esc(f.measurement.replaceAll('_',' '))}</p>${f.status==='available'&&f.value!==null?`<p>${esc(f.value)} ${esc(f.unit)}</p>`:''}${f.missing_reasons?.length?`<ul>${f.missing_reasons.map(reason=>`<li>${esc(missingLabels[reason]||reason.replaceAll('_',' '))}</li>`).join('')}</ul>`:''}<small>Published: ${esc(f.published_at||'Date unknown')} · Available: ${esc(f.available_at||'Date unknown')} · Issued: ${esc(f.issued_at)}</small><p>Current observations alone do not establish a future trend.</p>`;
}
