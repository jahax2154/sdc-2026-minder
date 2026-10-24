// Reuses the reviewed assessment/intake presentation from C/A acceptance UI.
// Rendered within the approved product shell and source design tokens.
import {api,optional,key} from '../client.js';
import {card,esc,bind,showError,facts,source,safeURL} from '../ui.js';

export async function explorePage(ctx,page){
const view=ctx.view;let profile=ctx.profile,selectedRole=ctx.selectedRole;
const append=html=>view.insertAdjacentHTML('beforeend',html);
const title=(heading,lead)=>{view.innerHTML=`<h1>${esc(heading)}</h1><p class="lead">${esc(lead)}</p>`;};
async function getProfile(){profile=await optional('profile');ctx.profile=profile;}
async function render(){ctx.selectedRole=selectedRole;sessionStorage.setItem('minder-product-role',selectedRole);await ctx.render();}
const selectedLabel=()=>selectedRole||'Choose a role in Career Match';
function needProfile(){if(profile)return false;append(card('Start with your profile','<p>A partial profile is enough to start. No employment history is required.</p><a href="#profile">Open My profile →</a>'));return true;}
const readableTime=value=>value&&!Number.isNaN(Date.parse(value))?new Date(value).toLocaleString():value??'Unknown';
function exploreTabs(page){append(`<nav class="tabs" aria-label="Explore areas">${[['career-match','Career Match'],['roadmap','Roadmap & Skills'],['tasks','Tasks'],['progress','Progress'],['news','News & Trends'],['future','Future Explorer']].map(([id,label])=>`<a class="button-outline ${id===page?'active':''}" href="#${id}">${label}</a>`).join('')}</nav>`);}
async function plansAndContent(page) {
  const names={overview:'A little every day.',roadmap:'Your roadmap & skills.',tasks:'Your next steps.',progress:'See your activity progress.',news:'News & trends.',future:'Future Explorer.'};
  title(names[page]||'Your workspace.','Choose your direction, keep the evidence visible, and take one practical step.');exploreTabs(page);
  if(needProfile())return;
  if(page==='news')return news();
  if(page==='future'){
    const context=await api('career-context',selectedRole?{selected_role_ids:[selectedRole]}:{});
    append(card('Current observations and next-quarter outlook',facts(context.statements)));
    return;
  }
  const [directionState,planState,progress,designState]=await Promise.all([api('product/direction'),api('plans'),api('product/progress'),api('plan-designs')]);
  const direction=directionState.direction,plans=planState.plans;
  const active=plans.find(p=>p.plan_id===direction?.plan_id);
  if(page==='overview'){
    const overview=await api('product/views/overview');
    append(`<div class="grid">${card('Your direction',`<p>${esc(direction?.role_id||'No direction selected')}</p><a href="#career-match">Explore careers →</a>`)}${card('Next steps',`<p>${active?active.tasks.length+' activities in your active roadmap':'Choose an active roadmap to see your next steps.'}</p><a href="#tasks">Open tasks →</a>`)}${card('Your MindBot',`<p>${overview.data.pending_proposals.length} proposals waiting for review.</p><a href="#mindbots">Review proposals →</a>`)}</div>`);
  }
  if(page==='progress'||page==='overview'){
    append(card('Activity completion',`<p>${progress.completed_count} of ${progress.eligible_count} eligible activities complete</p>${progress.fraction===null?'<p>No active eligible activities yet. Completion percentage is unavailable.</p>':`<progress value="${progress.completed_count}" max="${progress.eligible_count}" aria-label="Activity completion"></progress>`}<p>${esc(progress.denominator)}</p><small>Observed ${esc(progress.observed_at)}. Completed activities do not certify skill mastery or readiness.</small>`));
    if(page==='progress')return;
  }
  if(page==='roadmap'){
    append(card('Your chosen direction',`<p>${esc(direction?.role_id||'No chosen direction yet')}</p><p>Exploring a role does not change your chosen direction.</p><a href="#career-match">Explore and choose a direction →</a>`));
    append(card('Prepare a roadmap',`<p>Exploring: ${esc(selectedRole||direction?.role_id||'Choose a role first')}</p><button id="preview-plan" ${!(selectedRole||direction?.role_id)?'disabled':''}>Preview a preparation path</button><div id="plan-preview"></div>`));
    bind('preview-plan',async()=>{
      const preview=await api('pathway-preview',{role_id:selectedRole||direction.role_id});
      document.querySelector('#plan-preview').innerHTML=`<p>${esc(preview.design.limitation)}</p>`+preview.design.activities.map(a=>`<p>${esc(a.description)}<small>${esc(a.authorship)} · effort unknown</small></p>`).join('')+(preview.design.resource_options||[]).map(r=>`<label><input type="checkbox" class="resource-choice" value="${esc(r.resource_id)}"> ${esc(r.title)} · ${esc(r.publisher)}</label>${source(r.source)}`).join('')+'<p>Learning choices do not certify mastery. Creation preserves prior plans.</p><button id="accept-plan">Create this roadmap</button>';
      const idempotency_key=key();bind('accept-plan',async()=>{
        preview.design.selected_resources=[...document.querySelectorAll('.resource-choice:checked')].map(el=>el.value);
        await api('plans',{plan:preview.plan,design:preview.design,idempotency_key});await render();
      });
    });
    const roadmap=await api('product/views/roadmap');
    append(card('Requirements & unknowns',(roadmap.data.unknowns||[]).map(u=>`<p>${esc(u)}</p>`).join('')+(roadmap.data.requirements||[]).map(r=>`<details><summary>${esc(r.role.label||r.role.role_id)} · occupational reference</summary><p>${esc(r.limitation)}</p>${(r.role.requirements||[]).map(e=>`<p>${esc(e.subject_id)} · ${esc(e.state)}${e.provenance?source(e.provenance):''}</p>`).join('')}</details>`).join('')));
  }
  if(!plans.length){append(card('No roadmap yet','<p>Explore a role, preview a preparation path, then explicitly create it.</p><a href="#career-match">Explore careers →</a>'));return;}
  if(page==='roadmap'||page==='tasks'){
    append(card('Your roadmaps',`<p>Choose the active roadmap used by Progress. Older plans remain saved.</p><label>Active roadmap<select id="active-plan"><option value="">Choose a roadmap</option>${plans.map(p=>`<option value="${esc(p.plan_id)}" ${direction?.plan_id===p.plan_id?'selected':''}>${esc(p.selected_role_id)} · ${p.tasks.length} activities</option>`).join('')}</select></label><button id="activate-plan">Use this roadmap</button>`));
    bind('activate-plan',async()=>{const plan=plans.find(p=>p.plan_id===document.querySelector('#active-plan').value);if(!plan)throw new Error('Choose a roadmap.');await api('product/direction',{role_id:plan.selected_role_id,plan_id:plan.plan_id,expected_version:direction?.version||null,idempotency_key:key()},'PUT');await render();});
    if(!active){append(card('Select an active roadmap','<p>Select your roadmap above. Saved plans remain available without silently changing your direction.</p>'));return;}
    if(page==='tasks')return tasks(active);
    const design=designState.designs.find(d=>d.plan_id===active.plan_id)?.design;
    append(card('Active roadmap',`<p>${esc(active.selected_role_id)}</p>`+active.tasks.map(t=>`<p>${esc(t.title||design?.activities.find(a=>a.task_id===t.task_id)?.description||'Preparation activity')}<small>${esc(t.state)} · effort ${esc(t.estimated_hours??'unknown')} h · ${t.mastery_verified?'Assessed evidence recorded':'Mastery not verified'}</small></p>`).join('')+'<a href="#tasks">Manage activities →</a>'));
    if(design?.selected_resources?.length)append(card('Selected learning choices',(design.resource_options||[]).filter(r=>design.selected_resources.includes(r.resource_id)).map(r=>`<p>${esc(r.title)} · ${esc(r.publisher)}</p>${source(r.source)}`).join('')));
  }
}

async function tasks(plan){
  append(card('Add a task',`<form id="newTask"><label>Task title<input name="title" maxlength="200" required></label><label>Description<textarea name="description" maxlength="4000"></textarea></label><button type="submit">Add task</button></form>`));
  let newTaskBody=null;
  bind('newTask',async()=>{const f=document.querySelector('#newTask');newTaskBody??={plan_id:plan.plan_id,expected_state_version:plan.state_version,idempotency_key:key(),task:{task_id:key(),title:f.elements.title.value.trim(),description:f.elements.description.value,state:'proposed',activity_completion:false,mastery_verified:false,prerequisite_task_ids:[],locked:false,scheduled_at:null,estimated_hours:null,evidence_ids:[],skill_ids:[]}};try{await api('product/tasks',newTaskBody);}catch(e){if([413,415,422].includes(e.status))newTaskBody=null;throw e;}await render();});
  append(card('Filter activities','<label>Status<select id="task-filter"><option value="">All</option><option value="proposed">Proposed</option><option value="scheduled">Scheduled</option><option value="completed">Completed</option><option value="cancelled">Cancelled</option></select></label><div id="task-list"></div>'));
  async function list(state=''){
    const result=await api('product/views/tasks',{plan_id:plan.plan_id,limit:50,...(state?{state}:{})});
    const el=document.querySelector('#task-list');el.innerHTML=`<p>${result.data.total} activities · first ${result.data.tasks.length} shown. Progress counts all eligible activities in the active plan.</p>`+result.data.tasks.map(({task:t},i)=>{
      const blocked=t.prerequisite_task_ids.some(id=>!plan.tasks.find(p=>p.task_id===id)?.activity_completion);
      const immutable=t.locked||t.state==='cancelled';
      return card(t.title||'Preparation activity',`<p>${esc(t.description||'')}</p><p>${esc(t.state)} · effort ${esc(t.estimated_hours??'unknown')} h · ${esc(t.scheduled_at||'Unscheduled')}</p><small>${t.mastery_verified?'Mastery evidence recorded':'Mastery not verified'}</small>${!immutable?`<button id="task-${i}-${t.state==='completed'?'undo':'complete'}" ${blocked&&t.state!=='completed'?'disabled':''}>${t.state==='completed'?'Undo completion':'Mark activity complete'}</button>${t.state!=='completed'?`<details><summary>Edit or schedule</summary><label>Title<input id="title-${i}" value="${esc(t.title||'Preparation activity')}"></label><label>Description<textarea id="description-${i}">${esc(t.description||'')}</textarea></label><label>Effort in hours (optional)<input id="effort-${i}" type="number" min="0" step="0.25" value="${esc(t.estimated_hours??'')}"></label><button id="task-${i}-edit">Save task</button><label>Schedule (your local timezone)<input id="schedule-${i}" type="datetime-local"></label><button id="task-${i}-reschedule">Save schedule</button><button class="secondary" id="task-${i}-cancel">Cancel activity</button></details>`:''}`:''}${blocked?'<small>Prerequisite activities must be completed first.</small>':''}`);
    }).join('');
    result.data.tasks.forEach(({task:t,state_version},i)=>{
      for(const operation of ['complete','undo','edit','reschedule','cancel']){
        const idempotency_key=key();let exactBody=null;
        bind(`task-${i}-${operation}`,async()=>{
          if(!exactBody){let changes;
            if(operation==='edit'){const hours=document.querySelector('#effort-'+i).value;changes={title:document.querySelector('#title-'+i).value.trim(),description:document.querySelector('#description-'+i).value,estimated_hours:hours===''?null:Number(hours)};}
            if(operation==='reschedule'){const date=document.querySelector('#schedule-'+i).value;changes={scheduled_at:date?new Date(date).toISOString():null};}
            exactBody={plan_id:plan.plan_id,task_id:t.task_id,operation,expected_state_version:state_version,idempotency_key,...(changes?{changes}:{})};
          }
          try{await api('product/task-action',exactBody);}catch(e){if([413,415,422].includes(e.status))exactBody=null;throw e;}await render();
        });
      }
    });
  }
  document.querySelector('#task-filter').onchange=e=>list(e.target.value).catch(showError);await list();
}

async function news(){
  const [feed,directionState,plans]=await Promise.all([api('product/resources',{}),api('product/direction'),api('plans')]);
  append(card('News & next-quarter forecasts','<p>No verified news or video feed is integrated. Forecasts remain unavailable where source history is insufficient.</p><a href="#future">Inspect current evidence & outlook →</a>'));
  append(card('Learning resources',`<p>${feed.coverage.learning_resource} verified metadata records · ${feed.coverage.article} articles · ${feed.coverage.video} videos.</p><p>${esc(feed.limitations.join(' '))}</p><label>Format<select id="resource-format"><option value="">All available formats</option><option value="learning_resource">Learning resources</option><option value="article">Articles</option><option value="video">Videos</option></select></label><label><input id="saved-only" type="checkbox"> Saved only</label><label><input id="dismissed-only" type="checkbox"> Dismissed resources</label><div id="resources"></div>`));
  async function list(){
    const type=document.querySelector('#resource-format').value;const result=await api('product/resources',{...(type?{types:[type]}:{}),...(document.querySelector('#saved-only').checked?{saved:true}:{}),dismissed:document.querySelector('#dismissed-only').checked});
    const interactions=result.interactions.resource_states||[];
    const items=result.resources.filter(r=>!document.querySelector('#saved-only').checked||interactions.find(s=>s.resource_id===r.resource_id)?.saved);
    const el=document.querySelector('#resources');el.innerHTML=items.length?items.map((r,i)=>{
      const state=interactions.find(s=>s.resource_id===r.resource_id);
      return card(r.title,`<p>${esc(r.description)}</p><small>${esc(r.type.replaceAll('_',' '))} · ${esc(r.publisher)} · publication date ${esc(r.published_at||'unknown')} · retrieved ${esc(r.retrieved_at)}</small><p>${esc(r.relevance_reason)}</p><small>Duration, total cost and language ${r.language?esc(r.language):'unknown'}. Cached metadata is not revalidated on request.</small>${source(r.source)}<p>${state?.saved?'Saved':'Not saved'} · ${state?.dismissed?'Dismissed':'Not dismissed'}</p><button id="resource-${i}-save">${state?.saved?'Unsave':'Save resource'}</button><button id="resource-${i}-dismiss" class="secondary">${state?.dismissed?'Restore':'Dismiss'}</button><button id="resource-${i}-detail" class="secondary">Source details</button><div id="resource-detail-${i}"></div><button id="resource-${i}-add" ${directionState.direction?.plan_id?'':'disabled'}>Add to active roadmap</button>`);
    }).join(''):'<p>No resources match these filters. Change the format or saved-only filter.</p>';
    items.forEach((r,i)=>{
      const state=interactions.find(s=>s.resource_id===r.resource_id);
      for(const operation of ['save','dismiss']){
        const idempotency_key=key();bind(`resource-${i}-${operation}`,async()=>{await api('product/resource-state',{resource_id:r.resource_id,saved:operation==='save'?!state?.saved:!!state?.saved,dismissed:operation==='dismiss'?!state?.dismissed:!!state?.dismissed,expected_version:state?.version||null,idempotency_key},'PUT');await list();});
      }
      bind(`resource-${i}-detail`,async()=>{const detail=await api('product/resource-detail',{resource_id:r.resource_id});document.querySelector('#resource-detail-'+i).innerHTML=source(detail.resource.source)+`<p>${esc(detail.resource.prerequisites)}</p>`;});
      const plan=plans.plans.find(p=>p.plan_id===directionState.direction?.plan_id),idempotency_key=key();
      bind(`resource-${i}-add`,async()=>{await api('product/resource-to-plan',{resource_id:r.resource_id,plan_id:plan.plan_id,expected_state_version:plan.state_version,idempotency_key});await render();});
    });
  }
  document.querySelector('#resource-format').onchange=()=>list().catch(showError);document.querySelector('#saved-only').onchange=()=>list().catch(showError);document.querySelector('#dismissed-only').onchange=()=>list().catch(showError);await list();
}

await plansAndContent(page);
}
