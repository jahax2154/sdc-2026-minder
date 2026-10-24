import { readFileSync } from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';

const html=readFileSync('minder-user-profile-prototype-v2.html','utf8');
const source=html.match(/<script>([\s\S]*?)<\/script>/)?.[1];
assert.ok(source,'Self-contained inline script must exist');
new vm.Script(source,{filename:'minder-profile-inline.js'});
assert.match(html,/--forest: #345c46/,'Sage/forest token must be present');
assert.match(html,/class="profile-identity"/,'Identity component must exist');
assert.match(html,/class="profile-tabs"/,'Five-tab rounded component must exist');

const storage=new Map();
const element={innerHTML:''};
const listeners={};
let currentHash='';
const location={search:''};
Object.defineProperty(location,'hash',{get:()=>currentHash,set(v){currentHash=v;listeners.hashchange?.();}});
const document={getElementById:()=>element,addEventListener:(n,f)=>listeners[n]=f};
const window={addEventListener:(n,f)=>listeners[n]=f};
const sandbox={
  document,window,location,
  history:{replaceState(_a,_b,url){currentHash=url;}},
  localStorage:{getItem:k=>storage.get(k)??null,setItem:(k,v)=>storage.set(k,v),removeItem:k=>storage.delete(k)},
  URLSearchParams,Date,Intl,structuredClone,setTimeout:()=>0,clearTimeout:()=>{},requestAnimationFrame:()=>{},console,
};
vm.createContext(sandbox);
vm.runInContext(source,sandbox,{timeout:5000});
const run=js=>vm.runInContext(js,sandbox,{timeout:5000});

assert.match(element.innerHTML,/Where are you in your journey\?/);
assert.ok(!element.innerHTML.includes('class="profile-tabs"'),'No completed-profile tabs during setup');
run("setStage('studying');nextSetup('situation')");
assert.match(element.innerHTML,/What would you like help with\?/);
run("setGoal('fit');nextSetup('objective')");
assert.match(element.innerHTML,/What are you studying\?/);
run("draft.context='Computer Science / Artificial Intelligence';draft.educationLevel='Undergraduate degree';nextSetup('context')");
assert.match(element.innerHTML,/Anything else you.d like Minder to know\?/);
run("go('profile/setup/review')");
assert.match(element.innerHTML,/Create my profile/);
run('createProfile()');
assert.match(element.innerHTML,/Ready to explore what fits\?/);
assert.match(element.innerHTML,/Avery Lim/);
assert.match(element.innerHTML,/class="identity-avatar"[^>]*>AL<\/div>/);
const tabs=(element.innerHTML.match(/role="tab"/g)||[]).length;
assert.equal(tabs,5,'Exactly five post-setup tabs');

run("beginEdit('displayName')");
run("edit.value='Junhong';saveEdit()");
assert.match(element.innerHTML,/class="identity-avatar"[^>]*>JU<\/div>/);
assert.equal(run("profile.displayName"),'Junhong');

run("go('profile/background');beginEdit('context')");
run("edit.value='Robotics';saveEdit()");
assert.equal(run('profile.context'),'Robotics');
run("go('profile/goals');beginEdit('interestsText')");
run("edit.value='AI, Robotics';saveEdit()");
assert.equal(run('profile.interests.join(",")'),'AI,Robotics');

run("go('profile/skills');startSkillAdd()");
run("edit.value.name='Python';saveEdit()");
assert.equal(run('profile.skills.length'),1);
run("startSkillAdd();edit.value.name='python';saveEdit()");
assert.match(element.innerHTML,/already in your profile/);
run('cancelEdit()');

run("go('profile/record');startRecordAdd('projects')");
run("edit.value.title='A real project';saveEdit()");
assert.equal(run('profile.records.projects.length'),1);

run("go('profile/background');beginEdit('context')");
run("edit.value='Unsaved';go('profile/skills')");
assert.match(element.innerHTML,/Discard unsaved changes\?/);
assert.equal(run('route'),'profile/background');
run('discardAndNavigate()');
assert.equal(run('route'),'profile/skills');

run('resetDemo()');
assert.match(element.innerHTML,/Where are you in your journey\?/);
run("setStage('studying');nextSetup('situation');setGoal('path');nextSetup('objective')");
assert.match(element.innerHTML,/Which career are you interested in\?/);

assert.equal(run("initials('Avery Lim')"),'AL');
assert.equal(run("initials('Junhong')"),'JU');
assert.equal(run("initials('Nur Aina Rahman')"),'NR');

console.log('PASS: inline JS parses; onboarding routes/branch, optional/review/save, five tabs, dynamic initials, inline field/interest/skill/record saves, duplicate rejection, dirty edit guard, reset. Browser visual QA remains separate.');
