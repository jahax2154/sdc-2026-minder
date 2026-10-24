// Reuses the reviewed assessment/intake presentation from C/A acceptance UI.
// Rendered within the approved product shell and source design tokens.
import {api,optional,key} from '../client.js';
import {card,esc,bind,showError,facts,source,safeURL} from '../ui.js';

export async function careerPage(ctx,page){
const view=ctx.view;let profile=ctx.profile,selectedRole=ctx.selectedRole;
const append=html=>view.insertAdjacentHTML('beforeend',html);
const title=(heading,lead)=>{view.innerHTML=`<h1>${esc(heading)}</h1><p class="lead">${esc(lead)}</p>`;};
async function getProfile(){profile=await optional('profile');ctx.profile=profile;}
async function render(){ctx.selectedRole=selectedRole;sessionStorage.setItem('minder-product-role',selectedRole);await ctx.render();}
const selectedLabel=()=>selectedRole||'Choose a role in Career Match';
function needProfile(){if(profile)return false;append(card('Start with your profile','<p>A partial profile is enough to start. No employment history is required.</p><a href="#profile">Open My profile →</a>'));return true;}
const readableTime=value=>value&&!Number.isNaN(Date.parse(value))?new Date(value).toLocaleString():value??'Unknown';
function exploreTabs(page){append(`<nav class="tabs" aria-label="Explore areas">${[['career-match','Career Match'],['roadmap','Roadmap & Skills'],['tasks','Tasks'],['progress','Progress'],['news','News & Trends'],['future','Future Explorer']].map(([id,label])=>`<a class="button-outline ${id===page?'active':''}" href="#${id}">${label}</a>`).join('')}</nav>`);}
async function careerMatch() {
  const read=await api('product/views/career-match',{});
  const recommendation=read.data.recommendation;
  const coverage=recommendation?.coverage;
  if(coverage) append(card('Your recommendation coverage', `<p>${coverage.assessed} of ${coverage.candidates} eligible candidates assessed · ${coverage.current_comparable_ranked} ranked with comparable current Malaysian evidence · ${coverage.personal_only_ranked} personal-only ranks.</p><p>${coverage.published_offering_comparable_ranked ?? 0} published occupation-category comparisons · ${coverage.employer_comparable_ranked ?? coverage.current_comparable_ranked} employer-feed comparisons · ${coverage.shortage_context_supported ?? coverage.shortage_supported ?? 0} related shortage-group contexts (${coverage.shortage_exact_role_supported ?? 0} exact whole-role designations) · ${coverage.sector_context_supported ?? 0} related sector contexts. Context coverage can overlap; sector totals are not role counts.</p><p>Provisional essential-skill evidence fit. Groups have independent ranks; their display order does not compare opportunities across groups. ${recommendation.overall_ranking_complete?'Current comparison supported for this view.':'Partial coverage: personal-only results are not full recommendation completion.'}</p>`));
  for(const q of recommendation?.targeted_questions || []) append(card('Focused input needed',`<p>${esc(q)}</p><a href="#profile">Add an anchored assessment</a>`));
  for(const group of recommendation?.ranking_groups || []) {
    const options=recommendation.options.filter(o=>o.ranking_group===group.group_id).slice(0,8);
    append(card(group.label || (group.basis==='personal_and_comparable_current'?'Current-evidence comparison':'Personal-only exploration · market comparison unsupported'),`<p>${esc(group.limitation)}</p><small>Showing ${options.length} of ${group.role_ids.length} ranked roles in this group. Explore any other role below.</small>`+options.map(o=>`<p><button class="secondary" data-recommended-role="${esc(o.role_id)}">${esc(o.explanation.split(':')[0])}</button><small>${Math.round(o.evidence_coverage*100)}% of skill criteria assessed · provisional evidence-based comparison</small><span>${esc(o.explanation)}</span></p>`).join('')));
  }
  document.querySelectorAll('[data-recommended-role]').forEach(b=>b.onclick=()=>{selectedRole=b.dataset.recommendedRole;sessionStorage.setItem('minder-product-role',selectedRole);render().catch(showError);});
  append(card('Find a role to explore', '<p>Browse every reference or filter this catalogue view explicitly. Recommendations above consider every supported eligible role.</p><label>Search by title<input id="role-query" placeholder="Software, engineering, accounting…"></label><button id="search-roles">Search</button><button class="secondary" id="clear-roles">Clear filter</button><div id="roles"></div>'));
  async function search(query='') {
    const result=await api('roles',{query,limit:20});
    document.querySelector('#roles').innerHTML=`<p class="muted">${result.total} catalogue references · first ${result.roles.length} in catalogue order, not rank</p>`+result.roles.map(r=>`<p><button class="secondary" data-role="${esc(r.role_id)}">${esc(r.label)}</button><small>${esc(r.role_id)} · ${esc(r.eligibility)}</small></p>`).join('');
    document.querySelectorAll('[data-role]').forEach(b=>b.onclick=()=>{selectedRole=b.dataset.role;sessionStorage.setItem('minder-product-role',selectedRole);render().catch(showError);});
  }
  bind('search-roles',()=>search(document.querySelector('#role-query').value));
  bind('clear-roles',()=>{document.querySelector('#role-query').value='';return search();});await search(sessionStorage.getItem('minder-product-search')||'');sessionStorage.removeItem('minder-product-search');
  const nativeCatalogue=await api('source-market-catalogue');
  append(card('Explore Malaysian source categories',`<p>These are source-native facts, not additional canonical roles or a demand leaderboard. Choosing a category does not change your profile or declare that your role is critical.</p><label>Source category<select id="source-category">${nativeCatalogue.records.map(r=>`<option value="${esc(r.evidence_id)}">${esc(r.entity?.label || r.evidence_id)} · ${esc(r.entity?.code || 'code not supplied')}</option>`).join('')}</select></label><button id="source-context">Inspect source fact</button><div id="source-context-result"></div>`));
  bind('source-context',async()=>{
    const result=await api('source-market-context',{evidence_ids:[document.querySelector('#source-category').value]});
    document.querySelector('#source-context-result').innerHTML=`<p>${esc(result.usage)}</p>`+result.records.map(r=>`<p>${esc((r.occupation || r.sector)?.label || r.evidence_id)}: ${r.value==='listed_in_national_MyCOL'?'Listed source group; nominated-title restrictions remain':esc(typeof r.value==='number'?r.value.toLocaleString():r.value)} · ${esc(r.unit)}</p><small>${esc(r.observation_period.label || (r.observation_period.start+' → '+r.observation_period.end))} · published ${esc(r.published_at || 'not verified')} · available ${esc(r.available_at)}</small><p>${esc(r.limitations.join(' '))}</p>${/^https:\/\//.test(r.source.url)?`<a href="${esc(r.source.url)}" target="_blank" rel="noreferrer">Official source</a>`:''}`).join('');
  });
  if(!selectedRole) return;
  const direction=(await api('product/direction')).direction;
  const requirements=await api('role-requirements',{role_id:selectedRole});
  append(card(requirements.role.label||selectedRole,`<p>${esc(requirements.limitation)}</p><p>Chosen direction: ${esc(direction?.role_id||'None selected')}</p><button id="choose-direction">Choose this direction</button><a href="#roadmap">Prepare a roadmap →</a>`));
  const directionKey=key();bind('choose-direction',async()=>{await api('product/direction',{role_id:selectedRole,expected_version:direction?.version||null,idempotency_key:directionKey},'PUT');await render();});
  const context=await api('career-context',{selected_role_ids:[selectedRole]});
  append(facts(context.statements));
  const sourceEvidence=await api('role-evidence',{role_id:selectedRole});
  const evidenceNames={employer_observation:'Employer observations',published_offering_activity:'Published occupation-category activity',occupation_shortage:'Occupation shortage designation',sector_context:'Related sector context'};
  append(card('Source evidence by measurement',sourceEvidence.records.map(r=>`<section><h4>${esc(evidenceNames[r.measurement_type] || r.measurement_type)}</h4>`+(r.status==='available'?`<p>${r.measurement_type==='occupation_shortage'?'Related source occupation group is listed; see its scope restrictions':esc(Number(r.value).toLocaleString())+' '+esc(r.unit)}</p><small>Source category: ${esc(r.source_entity_id)} · ${esc(r.observation_period.label || (r.observation_period.start+' → '+r.observation_period.end))}</small><p>${esc(r.mapping.scope)}</p><small>${r.ranking_eligibility==='context_only'?'Context only; no role-level allocation or ranking contribution.':r.ranking_eligibility==='shortage_context_adjustment'?'Related-group contextual treatment only; this does not designate this whole role as critical.':'Eligible only within its declared source comparison or dated designation treatment.'}</small>`:'<p>Unavailable or unmapped. Unknown is neither zero demand nor a proven opportunity.</p>')+(r.source && /^https:\/\//.test(r.source.uri)?`<small><a href="${esc(r.source.uri)}" target="_blank" rel="noreferrer">${esc(r.source.source_id)}</a> · published ${esc(r.published_at || 'not verified')} · available ${esc(r.available_at)}</small>`:'')+(r.source_scope?`<small>Source occupation ${esc(r.source_scope.occupation_system)} ${esc(r.source_scope.occupation_version)} ${esc(r.source_scope.occupation_code)}. Applies to every child: ${r.source_scope.applies_to_all_children?'yes':'no'}. Explicit memberships retained: ${esc(r.source_scope.explicit_six_digit_codes.join(', ') || 'not verified for this group')}.</small>`:'')+`<small>Evidence reference ${esc(r.evidence_id)}</small></section>`).join('')));
  const globalOption=recommendation?.options.find(o=>o.role_id===selectedRole);
  if(globalOption?.trace_id) {
    append(card('Recommendation trace',`<p>Inspect the saved-profile policy, comparison scope and source references. Ordinary ranking values stay hidden.</p><button id="show-trace" class="secondary">Show recommendation evidence trace</button><div id="trace-result"></div>`));
    bind('show-trace',async()=>{
      const checked=await api('role-evidence',{role_id:selectedRole,trace_id:globalOption.trace_id,expected_profile_version:profile.version});
      const t=checked.trace;
      document.querySelector('#trace-result').innerHTML=`<p>Policy ${esc(t.policy_version)} · ${esc(t.ranking_basis.replaceAll('_',' '))}</p><small>Profile-versioned trace ${esc(t.trace_id)}</small><p>${t.evidence_ids.length} source references · ${Math.round(t.personal_evidence_coverage*100)}% of skill criteria assessed. Groups remain independent.</p>`;
    });
  }
  const detail=context.assessment_details?.[0];
  if(detail) append(card('Separate personal evidence',`<p>${esc(detail.score_status)} · ${detail.assessment_coverage?.assessed_count ?? 0}/${detail.assessment_coverage?.required_count ?? 0} skill criteria assessed</p>`+detail.components.map(c=>`<p>${esc(c.component_id.replaceAll('_',' '))}: ${c.value===null?'unanswered':'supplied evidence considered'}</p>`).join('')+`<small>Skill evidence: self-report ${detail.evidence_kinds?.self_report?.length || 0}, described demonstrations ${detail.evidence_kinds?.documented_demonstration?.length || 0}, reviewed ${detail.evidence_kinds?.reviewed_assessment?.length || 0}. Industry paths retain separate background and interest values; only the strongest supported path contributes once.</small>`+detail.industry_contributions.map(i=>`<p>${esc(i.industry_id)} · background ${i.background===null?'unknown':'supplied context'} · interest ${i.preference_utility===null?'unanswered':'supplied preference'} ${i.selected_path?'(selected path)':''}</p>`).join('')));
  append(card('Your preference',`<p>Selected: ${esc(selectedRole)} · ${esc(profile.preferences.find(p=>p.entity_type==='role'&&p.entity_id===selectedRole)?.state || 'unanswered')}. Preference does not delete this role.</p><button id="interested">Interested</button><button class="secondary" id="not-interested">Not interested</button><button class="secondary" id="reset-preference">Reset preference</button>`));
  for(const [id,state] of [['interested','interested'],['not-interested','not_interested'],['reset-preference',null]]) bind(id,async()=>{
    const before=profile.preferences.find(p=>p.entity_type==='role'&&p.entity_id===selectedRole)?.state ?? null;
    if(before===state)return;
    await api('direct-action',{request:{kind:'update_profile',target_id:profile.profile_id,expected:profile.version,diff:[{path:'/preferences/role/'+selectedRole,before,after:state}],reason:'Explicit role preference edit'},idempotency_key:key()});await getProfile();await render();
  });
  append(card('Company Explorer · Malaysia', '<p>Separate company evidence from overall role exploration. Coverage is bounded; current vacancy status may be unknown.</p><label>Employer<select id="employer"><option value="bosch">Bosch Group</option><option value="intel">Intel</option></select></label><button id="company">Check selected role</button><div id="company-result"></div>'));
  bind('company',async()=>{
    const response=await api('company-explorer',{employer_id:document.querySelector('#employer').value,role_id:selectedRole});
    const result=response.result || response;
    document.querySelector('#company-result').innerHTML=`<p>${esc(result.explanation)}</p><small>Checked ${esc(readableTime(result.checked_at))} · ${result.status==='requirements_unavailable'?'Company requirements unavailable':'Source-supported role information'}</small>`+(result.official_evidence||[]).map(s=>`<p><a href="${esc(s.uri)}" target="_blank" rel="noreferrer">Official employer source</a> · observed ${esc(readableTime(s.available_at))}</p>`).join('')+(response.other_supported_roles||[]).map(r=>`<p>${esc(r.title)} · ${esc(r.location)}<small>Current vacancy status not verified · retrieved ${esc(readableTime(r.retrieved_at))}</small></p><p>${esc(r.requirement_interpretation)}</p><p>Required: ${esc(r.required.join('; ') || 'Mandatory status not explicit in the source.')}</p><p>Preferred: ${esc(r.preferred.join('; ') || 'Not specified in checked evidence.')}</p><p>Requirement level unspecified: ${esc((r.qualifications_requirement_level_unspecified || []).join('; ') || 'No detailed criteria available.')}</p><small>User competence against these criteria remains unknown; generic occupation context is separate.</small>`).join('');
  });
}



title('Explore your possibilities.','Compare directions with evidence, then decide what you want to pursue.');exploreTabs('career-match');if(!needProfile())await careerMatch();
}
