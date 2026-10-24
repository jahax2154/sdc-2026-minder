// Existing anchored assessment controls; secondary to the approved profile presentation.
import {api,optional,key} from '../client.js';
import {card,esc,bind} from '../ui.js';
export async function profileEvidence(ctx,view){
let profile=ctx.profile;const append=html=>view.insertAdjacentHTML('beforeend',html);const render=()=>ctx.render();
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
await assessmentIntake();
}
