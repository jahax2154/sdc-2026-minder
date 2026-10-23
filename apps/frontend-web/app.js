const view = document.querySelector('#view');
const error = document.querySelector('#error');
let token = sessionStorage.getItem('minder-token');
let profile = null;
let selectedRole = sessionStorage.getItem('minder-role') || '';
let exploreTab = 'Career Match';
const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const key = () => crypto.randomUUID();

async function api(path, body, method = body === undefined ? 'GET' : 'POST') {
  const response = await fetch('/api/' + path, {method, headers: {
    'Content-Type':'application/json', ...(token ? {Authorization:'Bearer ' + token} : {})},
    ...(body === undefined ? {} : {body:JSON.stringify(body)})});
  const value = await response.json();
  if (!response.ok) throw new Error(value.code === 'stale_state_version' ?
    'This state changed. Refresh and review your change again.' : (value.code || 'Request failed'));
  return value;
}
function bind(id, handler) {
  const el = document.getElementById(id);
  if (el) el.addEventListener('click', async () => {
    const controls=Array.from(view.querySelectorAll('button,input,select,textarea')).map(node=>[node,node.disabled]);
    controls.forEach(([node])=>{node.disabled=true;});error.hidden = true;
    try {await handler();} catch(e) {showError(e);} finally {
      controls.forEach(([node,disabled])=>{if(node.isConnected)node.disabled=disabled;});
    }
  });
}
function showError(e) {error.textContent = e.message; error.hidden = false;}
function append(html) {view.insertAdjacentHTML('beforeend', html);}
function title(heading, lead) {view.innerHTML = `<h1>${esc(heading)}</h1><p class="lead">${esc(lead)}</p>`;}
function card(heading, content) {return `<article class="card"><h3>${esc(heading)}</h3>${content}</article>`;}
const actionName = kind => ({update_profile:'Profile update',change_goal:'Goal update',complete_task:'Activity completed',reschedule_task:'Schedule change',replace_plan:'Plan change'}[kind] || 'Saved change');
const triggerName = kind => ({preferences_changed:'Preference review',constraints_changed:'Availability review',task_completion:'Progress review',daily_check:'Daily review',material_market:'Market evidence review'}[kind] || 'Review');
const readableTime = value => value && !Number.isNaN(Date.parse(value)) ? new Date(value).toLocaleString(undefined,{dateStyle:'medium',timeStyle:'short'}) : (value ?? 'Unknown');
function diffLabel(change) {
  const field=change.path.split('/').at(-1);
  const label=({scheduled_at:'Scheduled time',estimated_hours:'Estimated hours',state:'Activity status',value:'Constraint'})[field] || 'Preference';
  return `<div class="diff">${label}<br>${esc(field==='scheduled_at'?readableTime(change.before):change.before)} → ${esc(field==='scheduled_at'?readableTime(change.after):change.after)}</div>`;
}
function facts(items) {return items.map(f => card(f.kind === 'current' ? 'Current observations' : f.kind === 'forecast' ? 'Next-quarter outlook' : 'Context',
  `<p>${esc(f.text)}</p>${f.period ? `<small>${esc(f.period.start)} → ${esc(f.period.end)}</small>` : ''}` +
  (f.published_at ? `<small>Published ${esc(f.published_at)} · Source population ${esc(f.source_universe_id)}</small>` : '') +
  (f.uncertainty ? `<small>Uncertainty: ${esc(f.uncertainty.method || 'not estimated')} · ${esc(f.uncertainty.lower ?? 'unknown')} to ${esc(f.uncertainty.upper ?? 'unknown')}</small>` : '') +
  (f.sources || []).map(s => /^https?:\/\//.test(s.uri) ? `<small><a href="${esc(s.uri)}" target="_blank" rel="noreferrer">${esc(s.source_id)}</a> · available ${esc(s.available_at)}</small>` : '').join(''))).join('');}
async function getProfile() {
  try {profile = await api('profile');} catch(e) {if(e.message === 'not_found') profile = null; else throw e;}
}
function needProfile() {
  if (profile) return false;
  append(card('Start with your profile', '<p>Save your profile before exploring personalised context.</p><a href="#profile">Open User Profile</a>'));
  return true;
}
function selectedLabel() {return selectedRole || 'Choose a role in Career Match';}

async function overview() {
  title('Find your next direction.', 'Bring your experience, curiosity and constraints together. Explore the evidence, then choose a step that works for you.');
  const plans = profile ? (await api('plans')).plans : [];
  const tasks = plans.flatMap(p => p.tasks);
  append(`<div class="grid">${card('Your profile', `<p>${profile ? `${profile.evidence.length} recorded evidence items` : 'A fresh start. No employment history required.'}</p><a href="#profile">Review profile →</a>`)}${card('Your next steps', `<p>${tasks.filter(t=>t.activity_completion).length} of ${tasks.length} activities complete</p><a href="#explore">Explore roadmap →</a>`)}${card('Evidence, with limits', '<p>Occupational references and a bounded Malaysian employer snapshot are connected. Provisional personal evidence-fit and scoped current-market ranks are available after focused intake. Missing forecasts stay unavailable.</p>')}</div>`);
}

async function profileView() {
  title('A picture of you.', 'Keep explicit claims separate from demonstrated capability. Unknown information can stay unknown.');
  append(card('Profile & availability', `<label>Timezone<input id="tz" value="${esc(profile?.timezone || 'Asia/Kuala_Lumpur')}"></label><label>Weekly study hours (optional)<input id="hours" type="number" min="0" max="168" value="${esc(profile?.constraints.find(c=>c.scope==='weekly_hours')?.value ?? '')}"></label><button id="save-profile">Save profile</button>`));
  bind('save-profile', async () => {
    const p = profile ? structuredClone(profile) : {profile_id:'new',profile_group_id:'new',version:'new',synthetic:false,evidence:[],preferences:[],current_fields:[],constraints:[],timezone:'Asia/Kuala_Lumpur'};
    p.timezone = document.querySelector('#tz').value;
    const hours = document.querySelector('#hours').value;
    p.constraints = p.constraints.filter(c=>c.scope!=='weekly_hours');
    if(hours !== '') p.constraints.push({constraint_id:'user-weekly-hours',scope:'weekly_hours',hard:true,value:Number(hours),unit:'hours_per_week',evidence_id:'explicit-availability'});
    profile = await api('profile', {profile:p,expected_version:profile?.version || null}, 'PUT');
    await render();
  });
  if (!profile) return;
  await assessmentIntake();
  append(card('Add your evidence', `<label>Skill or topic<input id="subject" placeholder="Python, project management, or another skill"></label><label>Your evidence or experience<textarea id="claim" placeholder="Describe a project, experience or qualification. This is saved as your statement."></textarea></label><button id="save-claim">Save my statement</button>`));
  bind('save-claim', async () => {
    const subject = document.querySelector('#subject').value.trim(), claim = document.querySelector('#claim').value.trim();
    if(!subject || !claim) throw new Error('Enter a subject and your evidence.');
    const p = structuredClone(profile), stamp = new Date().toISOString();
    const sha = Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(claim)))).map(x=>x.toString(16).padStart(2,'0')).join('');
    p.evidence.push({evidence_id:key(),subject_id:subject,value:claim,unit:'self_report_text',state:'known',method_id:'explicit-user-statement',provenance:{source_id:'user:'+profile.profile_id,version:stamp,sha256:sha,uri:'urn:minder:explicit-user-statement',geography:'MY',available_at:stamp,evidence_type:'explicit-user'}});
    profile = await api('profile',{profile:p,expected_version:profile.version},'PUT'); await render();
  });
  append(card('CV or conversation intake', '<p>UTF-8 .txt files up to 64 KiB. Extracted information stays a draft until you review and explicitly save a structured statement.</p><input id="cv" type="file" accept=".txt,text/plain"><button id="read-cv">Read text</button><div id="draft"></div>'));
  bind('read-cv', async () => {
    const file = document.querySelector('#cv').files[0];
    if(!file) throw new Error('Choose a text file.');
    if(file.size > 65536) throw new Error('Text file exceeds 64 KiB.');
    const result = await api('intake',{text:await file.text(),filename:file.name,channel:'cv',content_type:'text/plain'});
    document.querySelector('#draft').textContent = result.clarification + '\n\n' + result.text;
  });
  append(card('Recorded evidence', profile.evidence.length ? profile.evidence.map(e=>`<p>${esc(e.subject_id)}: ${esc(e.value ?? 'unknown')}<small>${esc(e.provenance.evidence_type)} · ${esc(e.method_id)}</small></p>`).join('') : '<p>No evidence yet. Missing information is unknown.</p>'));
}

async function assessmentEdit(subject, value, method, kind, statement, unit) {
  if(value !== null && statement.trim().length < 20) throw new Error('Describe the activity and evidence in at least 20 characters.');
  const p=structuredClone(profile), stamp=new Date().toISOString();
  // A new current observation replaces this exact intake item; persisted profile history retains earlier versions.
  p.evidence=p.evidence.filter(e=>!(e.subject_id===subject && e.method_id===method));
  if(value !== null) {
    const sha=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(statement)))).map(x=>x.toString(16).padStart(2,'0')).join('');
    p.evidence.push({evidence_id:key(),subject_id:subject,value,unit,state:'known',method_id:method,
      assessment:{kind,statement,rubric_version:method==='minder-anchored-evidence-v1'?'onet31-essential-anchors-v1':method},
      provenance:{source_id:'user:'+profile.profile_id,version:stamp,sha256:sha,uri:'urn:minder:explicit-assessment',geography:'MY',available_at:stamp,evidence_type:'explicit-user'}});
  }
  return p;
}
async function saveAssessment(...args) {
  const p=await assessmentEdit(...args);
  profile=await api('profile',{profile:p,expected_version:profile.version},'PUT');
}

async function assessmentIntake() {
  const ref=await api('assessment-reference');
  const options=items=>Object.entries(items).map(([id,label])=>`<option value="${esc(id)}">${esc(label)}</option>`).join('');
  const known=profile.evidence.filter(e=>e.method_id===ref.skill_method_id);
  append(card('Assess a few essential skills', `<p>Start with three skills. Choose a source activity level and describe what you did. Study projects count as self-report; prior employment and role ratings are optional. These provisional assessments do not certify competence.</p><p>${known.length} structured skill observations saved. Each role also needs at least 30% of its usable criteria.</p><label>Skill<select id="assessed-skill">${options(Object.fromEntries(Object.entries(ref.skills).map(([id,r])=>[id,r.label])))}</select></label><label>Closest activity level<select id="assessed-level"></select></label><p id="anchor-description"></p><label>Evidence type<select id="evidence-kind"><option value="self_report">Self-report</option><option value="documented_demonstration">Described project or demonstration (unreviewed claim)</option></select></label><label>Activity and evidence<textarea id="assessment-statement" placeholder="Describe the activity, your contribution and evidence supporting this anchor."></textarea></label><button id="save-assessment">Save skill assessment</button><button class="secondary" id="remove-assessment">Clear this skill assessment</button><p><a href="${esc(ref.sources[0].uri)}" target="_blank" rel="noreferrer">O*NET source anchors</a> · US occupational reference, not a Malaysian competence standard.</p>`));
  const updateDescription=()=>{
    const sid=document.querySelector('#assessed-skill').value, value=document.querySelector('#assessed-level').value;
    document.querySelector('#anchor-description').textContent=value===''?'Unanswered: capability stays unknown.':value==='0'?'Explicitly assessed: I cannot yet demonstrate this skill.':ref.skills[sid].anchors.find(a=>String(a.value)===value)?.description || '';
  };
  const updateSkill=()=>{
    const sid=document.querySelector('#assessed-skill').value, old=known.find(e=>e.subject_id===sid);
    document.querySelector('#assessed-level').innerHTML='<option value="">Unanswered</option><option value="0">Not yet able (explicit assessment)</option>'+ref.skills[sid].anchors.map(a=>`<option value="${a.value}">Source activity level ${a.value}</option>`).join('');
    document.querySelector('#assessed-level').value=old?String(old.value):'';
    document.querySelector('#assessment-statement').value=old?.assessment?.statement || '';
    document.querySelector('#evidence-kind').value=old?.assessment?.kind || 'self_report';updateDescription();
  };
  document.querySelector('#assessed-skill').onchange=updateSkill;document.querySelector('#assessed-level').onchange=updateDescription;updateSkill();
  bind('save-assessment',async()=>{
    const value=document.querySelector('#assessed-level').value;
    if(value==='') throw new Error('Choose an activity level or use Clear to remove the assessment.');
    await saveAssessment(document.querySelector('#assessed-skill').value,Number(value),ref.skill_method_id,document.querySelector('#evidence-kind').value,document.querySelector('#assessment-statement').value,'onet:LV');await render();
  });
  bind('remove-assessment',async()=>{await saveAssessment(document.querySelector('#assessed-skill').value,null,ref.skill_method_id,'self_report','','onet:LV');await render();});
  append(card('Industry context & interests (optional)', `<p>Context and interests influence supported paths without excluding other industries. A job title or current industry does not assign skill ability.</p><label>Industry<select id="context-industry">${options(ref.industries)}</select></label><label>Current relationship<select id="industry-history"><option value="unknown">Unknown / not supplied</option><option value="known">Current or prior field</option><option value="want_to_leave">I want to leave this field</option><option value="none_yet">No experience yet</option></select></label><label>Transferable background<select id="industry-background"><option value="">Unanswered / reset</option><option value="0">Explicitly no relevant exposure</option><option value="0.5">Relevant study or project context</option><option value="1">Sustained hands-on domain work</option></select></label><label>Background evidence<textarea id="background-statement" placeholder="Describe domain work or study. This remains separate from skill evidence."></textarea></label><label>Industry interest<select id="industry-interest"><option value="unknown">Unanswered / reset</option><option value="interested">Interested</option><option value="neutral">Neutral</option><option value="not_interested">Not interested</option></select></label><button id="save-industry">Save industry context</button>`));
  const updateIndustry=()=>{
    const iid=document.querySelector('#context-industry').value;
    const old=profile.evidence.find(e=>e.subject_id===iid&&e.method_id==='minder-transferable-background-v1');
    document.querySelector('#industry-history').value=profile.current_fields.find(f=>f.field_id===iid&&f.field_type==='industry')?.state || 'unknown';
    document.querySelector('#industry-background').value=old?String(old.value):'';
    document.querySelector('#background-statement').value=old?.assessment?.statement || '';
    document.querySelector('#industry-interest').value=profile.preferences.find(p=>p.entity_type==='industry'&&p.entity_id===iid)?.state || 'unknown';
  };
  document.querySelector('#context-industry').onchange=updateIndustry;updateIndustry();
  bind('save-industry',async()=>{
    const iid=document.querySelector('#context-industry').value, background=document.querySelector('#industry-background').value;
    const history=document.querySelector('#industry-history').value, interest=document.querySelector('#industry-interest').value;
    const p=await assessmentEdit(iid,background===''?null:Number(background),'minder-transferable-background-v1','transferable_background',document.querySelector('#background-statement').value,'fraction_0_1');
    p.current_fields=p.current_fields.filter(f=>!(f.field_id===iid&&f.field_type==='industry'));
    if(history!=='unknown')p.current_fields.push({field_id:iid,field_type:'industry',state:history,evidence_ids:p.evidence.filter(e=>e.subject_id===iid).map(e=>e.evidence_id)});
    p.preferences=p.preferences.filter(e=>!(e.entity_type==='industry'&&e.entity_id===iid));
    if(interest!=='unknown')p.preferences.push({entity_type:'industry',entity_id:iid,state:interest,authorizing_request_id:key()});
    profile=await api('profile',{profile:p,expected_version:profile.version},'PUT');await render();
  });
  append(card('Work style (optional)', `<p>Stated working preferences influence roles with a sourced style link. They never establish ability.</p><label>Style<select id="work-style">${options(ref.work_styles)}</select></label><label>Your preference<select id="style-value"><option value="">Unanswered / reset</option><option value="1">Prefer</option><option value="0.5">Neutral</option><option value="0">Prefer to avoid</option></select></label><label>Context<textarea id="style-statement" placeholder="Describe the working conditions you prefer."></textarea></label><button id="save-style">Save work-style preference</button>`));
  const updateStyle=()=>{
    const old=profile.evidence.find(e=>e.subject_id===document.querySelector('#work-style').value&&e.method_id==='minder-work-style-preference-v1');
    document.querySelector('#style-value').value=old?String(old.value):'';document.querySelector('#style-statement').value=old?.assessment?.statement || '';
  };document.querySelector('#work-style').onchange=updateStyle;updateStyle();
  bind('save-style',async()=>{const value=document.querySelector('#style-value').value;await saveAssessment(document.querySelector('#work-style').value,value===''?null:Number(value),'minder-work-style-preference-v1','work_style_preference',document.querySelector('#style-statement').value,'fraction_0_1');await render();});
}

async function minder() {
  title('Think it through with Minder.', 'Grounded explanations from your saved profile and selected role. Specific changes use the action controls; conversation alone does not grant edit authority.');
  if(needProfile()) return;
  append(card('Your question', `<p>Role context: ${esc(selectedLabel())}</p><textarea id="message" placeholder="Explain the role requirements and next-quarter outlook."></textarea><button id="ask">Ask Minder</button><button id="stage" class="secondary">Stage this as profile intake</button><div id="reply"></div>`));
  bind('stage',async()=>{const draft=await api('intake',{text:document.querySelector('#message').value,channel:'chat'});document.querySelector('#reply').textContent=draft.clarification;});
  bind('ask', async () => {
    const result = await api('chat',{message:document.querySelector('#message').value,expected_profile_version:profile.version,...(selectedRole ? {selected_role_ids:[selectedRole]} : {})});
    document.querySelector('#reply').innerHTML = `<p class="muted">${result.provider.status==='available'?'Language-assisted selection of saved evidence.':'Language provider unavailable. Showing saved evidence and its limits.'}</p>` + facts(result.statements);
  });
}

async function mindbots() {
  title('A considered nudge.', 'Mindbots can review progress and prepare changes. Every proactive change waits for your approval of its exact preview.');
  if(needProfile()) return;
  let settings = null; try {settings = await api('agent-settings');} catch(e) {if(e.message!=='not_found') throw e;}
  const state = await api('agents'), proposals = (await api('proposals')).proposals;
  append(card('Daily check', `<label>Local check time (${esc(profile.timezone)})<input id="check-time" type="time" value="${esc(settings?.check_time || '08:00')}"></label><label>Daily check<select id="enabled"><option value="false">Off</option><option value="true" ${settings?.enabled?'selected':''}>On</option></select></label><button id="configure">Save daily check</button><p class="muted">Worker must be running. Unattended deployment scheduling has not been verified.</p>`));
  bind('configure',async()=>{await api('agent-settings',{settings:{enabled:document.querySelector('#enabled').value==='true',check_time:document.querySelector('#check-time').value},expected_version:settings?.version || null},'PUT');await render();});
  for(const p of proposals) {
    const id=p.preview.proposal_id, req=p.preview.request;
    append(card('Proposed change · '+p.status, `<p>${esc(req.reason)}</p><p class="muted">Applies to the saved state used in this preview. Changes require a fresh review.</p>`+req.diff.map(diffLabel).join('')+(p.status==='pending'?`<button id="approve-${id}">Approve this exact change</button><button class="secondary" id="reject-${id}">Reject</button>`:'')));
    for(const decision of ['approve','reject']) bind(decision+'-'+id, async()=>{await api('proposal-decision',{proposal_id:id,decision,preview_hash:p.preview_hash,expected_state_version:req.expected_state_version});await render();});
  }
  append(card('Notices',state.notices.map(n=>`<p>${esc(n.summary)}<small>${esc(triggerName(n.trigger))} · ${n.provider_status==='available_candidate_selection'?'Language-assisted review':'Application review; language assistance unavailable'}</small></p>`).join('') || '<p>No notices yet.</p>'));
  const history=(await api('action-history')).history;
  for(const h of history) {
    const a=h.result.action;
    append(card(actionName(a.kind), `<p>${esc(a.reason)} · ${esc(a.execution_status)}</p><small>${esc(readableTime(h.created_at))} · ${a.approval_state==='approved'?'Approved preview':'Your direct instruction'}</small>`+(a.kind!=='complete_task'?`<button class="secondary" id="undo-${a.action_id}">Undo this change</button>`:'')));
    bind('undo-'+a.action_id,async()=>{await api('undo',{action_id:a.action_id,expected_state_version:a.resulting_state_version,idempotency_key:key()});await getProfile();await render();});
  }
}

async function explore() {
  title('Explore your possibilities.', 'Occupational references, current evidence and preparation work stay distinct. Choose a role without committing to a career goal.');
  append(`<div class="tabs">${['Progress','Tasks','Future Explorer','Career Match','Roadmap'].map(t=>`<button class="${t===exploreTab?'active':''}" data-tab="${t}">${t}</button>`).join('')}</div><div id="explore-view"></div>`);
  document.querySelectorAll('[data-tab]').forEach(b=>b.onclick=()=>{exploreTab=b.dataset.tab;render().catch(showError);});
  if(needProfile()) return;
  if(exploreTab==='Career Match') return careerMatch();
  if(exploreTab==='Future Explorer') {
    const result = await api('career-context',selectedRole ? {selected_role_ids:[selectedRole],selected_skill_ids:['source-term:python']} : {});
    append(facts(result.statements)); return;
  }
  const plans=(await api('plans')).plans;
  if(exploreTab==='Roadmap') {
    append(card('A preparation path', `<p>Selected: ${esc(selectedLabel())}</p><button id="preview-plan" ${!selectedRole?'disabled':''}>Preview a preparation path</button><div id="plan-preview"></div>`));
    bind('preview-plan',async()=>{
      const preview=await api('pathway-preview',{role_id:selectedRole});
      document.querySelector('#plan-preview').innerHTML=`<p>${esc(preview.design.limitation)}</p>`+preview.design.activities.map(a=>`<p>${esc(a.description)}<small>${esc(a.authorship)} · effort unknown · resources unverified</small></p>`).join('')+'<p>Optional learning choices below are not automatically mapped to your gaps. Select any you want to keep with this roadmap; duration and total cost remain unknown.</p>'+(preview.design.resource_options || []).map(r=>`<label><input class="resource-choice" type="checkbox" value="${esc(r.resource_id)}"> ${esc(r.title)} · ${esc(r.publisher)}</label><p>${esc(r.prerequisites)} <a href="${esc(r.source.uri)}" target="_blank" rel="noreferrer">Read official source</a></p>`).join('')+'<button id="accept-plan">Create this roadmap</button>';
      const creationKey=key();bind('accept-plan',async()=>{preview.design.selected_resources=Array.from(document.querySelectorAll('.resource-choice:checked')).map(el=>el.value);await api('plans',{plan:preview.plan,design:preview.design,idempotency_key:creationKey});await render();});
    });
  }
  const designs=(await api('plan-designs')).designs;
  for(const plan of plans) {
    const complete=plan.tasks.filter(t=>t.activity_completion).length;
    const design=designs.find(d=>d.plan_id===plan.plan_id)?.design;
    append(card('Your preparation path',`<p>${complete}/${plan.tasks.length} activities complete</p><progress value="${complete}" max="${plan.tasks.length||1}"></progress><small>Activity progress, not certified mastery.</small>`));
    if(design?.selected_resources?.length) append(card('Your selected learning choices',(design.resource_options || []).filter(r=>design.selected_resources.includes(r.resource_id)).map(r=>`<p><a href="${esc(r.source.uri)}" target="_blank" rel="noreferrer">${esc(r.title)}</a><small>${esc(r.publisher)} · effort and total cost unknown · no mastery inferred</small></p>`).join('')));
    if(exploreTab==='Progress') continue;
    for(const t of plan.tasks) {
      const label=design?.activities.find(a=>a.task_id===t.task_id)?.description || t.task_id;
      const blocked=t.prerequisite_task_ids.some(id=>!plan.tasks.find(p=>p.task_id===id)?.activity_completion);
      append(card(label,`<p>${esc(t.state)} · effort ${esc(t.estimated_hours ?? 'unknown')} h · ${esc(t.scheduled_at || 'unscheduled')}</p>`+(t.state!=='completed'&&!t.locked?`<button id="complete-${t.task_id}" ${blocked?'disabled':''}>Mark activity complete</button>${blocked?'<small>Complete the prerequisite activity first.</small>':''}`:'')));
      const completionKey=key();bind('complete-'+t.task_id,async()=>{await api('direct-action',{request:{kind:'complete_task',target_id:plan.plan_id,expected:plan.state_version,diff:[{path:'/tasks/'+t.task_id+'/state',before:t.state,after:'completed'}],reason:'User marked this activity complete'},idempotency_key:completionKey});await render();});
    }
  }
  if(!plans.length) append(card('No roadmap yet','<p>Explore a role and preview a preparation path in Roadmap.</p>'));
}

async function careerMatch() {
  const recommendation=(await api('career-context')).recommendation;
  const coverage=recommendation?.coverage;
  if(coverage) append(card('Your recommendation coverage', `<p>${coverage.assessed} of ${coverage.candidates} eligible candidates assessed · ${coverage.current_comparable_ranked} ranked with comparable current Malaysian evidence · ${coverage.personal_only_ranked} personal-only ranks.</p><p>Provisional essential-skill evidence fit. Groups have independent ranks; their display order does not compare opportunities across groups. ${recommendation.overall_ranking_complete?'Current comparison supported for this view.':'Partial coverage: personal-only results are not full recommendation completion.'}</p>`));
  for(const q of recommendation?.targeted_questions || []) append(card('Focused input needed',`<p>${esc(q)}</p><a href="#profile">Add an anchored assessment</a>`));
  for(const group of recommendation?.ranking_groups || []) {
    const options=recommendation.options.filter(o=>o.ranking_group===group.group_id).slice(0,8);
    append(card(group.basis==='personal_and_comparable_current'?'Current-evidence comparison':'Personal-only exploration · market comparison unsupported',`<p>${esc(group.limitation)}</p><small>Showing ${options.length} of ${group.role_ids.length} ranked roles in this group. Explore any other role below.</small>`+options.map(o=>`<p><button class="secondary" data-recommended-role="${esc(o.role_id)}">#${o.rank} · ${esc(o.explanation.split(':')[0])}</button><small>Personal evidence fit ${Number(o.personal_score).toFixed(1)}/100 · ${Math.round(o.evidence_coverage*100)}% assessed</small>${esc(o.explanation)}</p>`).join('')));
  }
  document.querySelectorAll('[data-recommended-role]').forEach(b=>b.onclick=()=>{selectedRole=b.dataset.recommendedRole;sessionStorage.setItem('minder-role',selectedRole);render().catch(showError);});
  append(card('Find a role to explore', '<p>Browse every reference or filter this catalogue view explicitly. Recommendations above consider every supported eligible role.</p><label>Search by title<input id="role-query" placeholder="Software, engineering, accounting…"></label><button id="search-roles">Search</button><button class="secondary" id="clear-roles">Clear filter</button><div id="roles"></div>'));
  async function search(query='') {
    const result=await api('roles',{query,limit:20});
    document.querySelector('#roles').innerHTML=`<p class="muted">${result.total} catalogue references · first ${result.roles.length} in catalogue order, not rank</p>`+result.roles.map(r=>`<p><button class="secondary" data-role="${esc(r.role_id)}">${esc(r.label)}</button><small>${esc(r.role_id)} · ${esc(r.eligibility)}</small></p>`).join('');
    document.querySelectorAll('[data-role]').forEach(b=>b.onclick=()=>{selectedRole=b.dataset.role;sessionStorage.setItem('minder-role',selectedRole);render().catch(showError);});
  }
  bind('search-roles',()=>search(document.querySelector('#role-query').value));
  bind('clear-roles',()=>{document.querySelector('#role-query').value='';return search();});await search();
  if(!selectedRole) return;
  const context=await api('career-context',{selected_role_ids:[selectedRole]});
  append(facts(context.statements));
  const detail=context.assessment_details?.[0];
  if(detail) append(card('Separate personal evidence',`<p>${esc(detail.score_status)} · ${detail.assessment_coverage?.assessed_count ?? 0}/${detail.assessment_coverage?.required_count ?? 0} skill criteria assessed</p>`+detail.components.map(c=>`<p>${esc(c.component_id.replaceAll('_',' '))}: ${c.value===null?'unanswered':Number(c.value).toFixed(3)} · contribution ${Number(c.contribution_points || 0).toFixed(2)} points</p>`).join('')+`<small>Skill evidence: self-report ${detail.evidence_kinds?.self_report?.length || 0}, described demonstrations ${detail.evidence_kinds?.documented_demonstration?.length || 0}, reviewed ${detail.evidence_kinds?.reviewed_assessment?.length || 0}. Industry paths retain separate background and interest values; only the strongest supported path contributes once.</small>`+detail.industry_contributions.map(i=>`<p>${esc(i.industry_id)} · background ${esc(i.background ?? 'unknown')} · interest ${esc(i.preference_utility ?? 'unknown')} · ${Number(i.adjustment_points || 0).toFixed(1)} points ${i.selected_path?'(selected path)':''}</p>`).join('')));
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

async function render() {
  error.hidden=true;await getProfile();
  const page=location.hash.slice(1)||'overview';
  document.querySelectorAll('nav a').forEach(a=>a.setAttribute('aria-current',a.hash==='#'+page?'page':'false'));
  await ({overview,profile:profileView,minder,mindbots,explore}[page] || overview)();
}
try {
  if(!token) {const session=await api('session',{});token=session.token;sessionStorage.setItem('minder-token',token);}
  const health=await api('health');document.querySelector('#readiness').textContent=health.integration_mode==='local_source_services'?'Local evidence connected':'Evidence integration unavailable';
  await render();window.addEventListener('hashchange',()=>render().catch(showError));
} catch(e) {showError(e);}
