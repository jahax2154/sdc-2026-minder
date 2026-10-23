// Reuses the reviewed assessment/intake presentation from C/A acceptance UI.
// Rendered within the approved product shell and source design tokens.
import {api,optional,key} from '../client.js';
import {card,esc,bind,showError,facts,source,safeURL} from '../ui.js';

export async function profilePage(ctx,page){
const view=ctx.view;let profile=ctx.profile,selectedRole=ctx.selectedRole;
const append=html=>view.insertAdjacentHTML('beforeend',html);
const title=(heading,lead)=>{view.innerHTML=`<h1>${esc(heading)}</h1><p class="lead">${esc(lead)}</p>`;};
async function getProfile(){profile=await optional('profile');ctx.profile=profile;}
async function render(){ctx.selectedRole=selectedRole;sessionStorage.setItem('minder-product-role',selectedRole);await ctx.render();}
const selectedLabel=()=>selectedRole||'Choose a role in Career Match';
function needProfile(){if(profile)return false;append(card('Start with your profile','<p>A partial profile is enough to start. No employment history is required.</p><a href="#profile">Open My profile →</a>'));return true;}
const readableTime=value=>value&&!Number.isNaN(Date.parse(value))?new Date(value).toLocaleString():value??'Unknown';
function exploreTabs(page){append(`<nav class="tabs" aria-label="Explore areas">${[['career-match','Career Match'],['roadmap','Roadmap & Skills'],['tasks','Tasks'],['progress','Progress'],['news','News & Trends'],['future','Future Explorer']].map(([id,label])=>`<a class="button-outline ${id===page?'active':''}" href="#${id}">${label}</a>`).join('')}</nav>`);}
async function profileView() {
  title('A picture of you.', 'Keep explicit claims separate from demonstrated capability. Unknown information can stay unknown.');
  append(card('Profile & availability', `<label>Display name<input id="display-name" maxlength="120" value="${esc(profile?.career_context?.display_name || '')}"></label><label>Education<textarea id="education" maxlength="4000">${esc(profile?.career_context?.education || '')}</textarea></label><label>Experience<textarea id="experience" maxlength="4000">${esc(profile?.career_context?.experience || '')}</textarea></label><label>Goals<textarea id="goals" maxlength="4000">${esc(profile?.career_context?.goals || '')}</textarea></label><label>Timezone<input id="tz" value="${esc(profile?.timezone || 'Asia/Kuala_Lumpur')}"></label><label>Weekly study hours (optional)<input id="hours" type="number" min="0" max="168" value="${esc(profile?.constraints.find(c=>c.scope==='weekly_hours')?.value ?? '')}"></label><button id="save-profile">Save profile</button>`));
  bind('save-profile', async () => {
    const p = profile ? structuredClone(profile) : {profile_id:'new',profile_group_id:'new',version:'new',synthetic:false,evidence:[],preferences:[],current_fields:[],constraints:[],timezone:'Asia/Kuala_Lumpur'};
    p.timezone = document.querySelector('#tz').value;
    p.career_context=Object.fromEntries(['display_name','education','experience','goals'].map(k=>[k,document.getElementById(k==='display_name'?'display-name':k).value]));
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
  append(card('CV or conversation intake', '<p>UTF-8 .txt files up to 64 KiB. Extracted information stays a draft until you review and explicitly save a structured statement.</p><label>UTF-8 text file<input id="cv" type="file" accept=".txt,text/plain"></label><button id="read-cv">Read text</button><div id="draft"></div>'));
  bind('read-cv', async () => {
    const file = document.querySelector('#cv').files[0];
    if(!file) throw new Error('Choose a text file.');
    if(file.size > 65536) throw new Error('Text file exceeds 64 KiB.');
    const result = await api('intake',{text:await file.text(),filename:file.name,channel:'cv',content_type:'text/plain'});
    document.querySelector('#draft').innerHTML=`<p>${esc(result.clarification)}</p><pre class="draft-text">${esc(result.text)}</pre><p>Review the context below. This saves your corrected self-report, without inferring skill mastery.</p><label>Corrected experience<textarea id="reviewed-experience" maxlength="4000">${esc(result.text.slice(0,4000))}</textarea></label><button id="save-intake">Save reviewed context</button>`;
    const correctionKey=key();bind('save-intake',async()=>{await api('product/intake-correction',{draft_id:result.id,expected_profile_version:profile.version,profile:{career_context:{experience:document.querySelector('#reviewed-experience').value}},idempotency_key:correctionKey});await render();});
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
  const ref=await optional('assessment-reference');
  if(!ref){append(card('Assessment references unavailable','<p>Your saved profile is available. You can record self-reported evidence below while assessment references are unavailable.</p>'));return;}
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


await profileView();
}
