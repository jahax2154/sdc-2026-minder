import assert from 'node:assert/strict';
import { readFileSync, mkdirSync } from 'node:fs';
import { createRequire } from 'node:module';
import { createServer } from 'node:http';
import { resolve } from 'node:path';

const require = createRequire(import.meta.url);
const { chromium } = require('playwright');
const document = readFileSync(resolve('minder-user-profile-prototype-v2.html'));
const outputDir = resolve('minder-user-profile-v2-screenshots');
mkdirSync(outputDir, { recursive: true });

const server = createServer((req, res) => {
  res.writeHead(200, {'content-type':'text/html; charset=utf-8', 'cache-control':'no-store'});
  res.end(document);
});
await new Promise(r => server.listen(0, '127.0.0.1', r));
const url = `http://127.0.0.1:${server.address().port}/`;
const browser = await chromium.launch({ headless:true, args:['--no-sandbox'] });
const context = await browser.newContext({ viewport:{ width:1672, height:940 }, deviceScaleFactor:1 });
const page = await context.newPage();
const jsErrors = [];
page.on('pageerror', e => jsErrors.push(e.message));
const button = name => page.getByRole('button', { name, exact:false }).first();
const shot = name => page.screenshot({ path:resolve(outputDir,name),fullPage:true });

try {
  await page.goto(url);
  await page.getByRole('heading',{name:'Where are you in your journey?'}).waitFor();
  await button("I'm studying").click();
  await shot('01_onboarding_situation.png');
  await button('Continue').click();

  await page.getByRole('heading',{name:'What would you like help with?'}).waitFor();
  await button('Discover careers that fit me').click();
  await shot('02_onboarding_objective.png');
  await button('Continue').click();

  await page.getByRole('heading',{name:'What are you studying?'}).waitFor();
  await page.getByLabel('Field of study').fill('Computer Science / Artificial Intelligence');
  await page.getByLabel('Education level').selectOption('Undergraduate degree');
  await shot('03_onboarding_student_context.png');
  await button('Continue').click();

  await page.getByRole('heading',{name:"Anything else you'd like Minder to know?"}).waitFor();
  await shot('04_onboarding_optional_enrichment.png');
  await button('Skip for now').click();
  await page.getByRole('heading',{name:'Almost ready to begin'}).waitFor();
  await shot('05_onboarding_review.png');
  await button('Create my profile').click();

  await page.getByRole('heading',{name:'Your profile'}).waitFor();
  assert.equal(await page.locator('.identity-avatar').innerText(),'AL');
  assert.equal(await page.locator('.identity-name').innerText(),'Avery Lim');
  assert.equal(await page.getByRole('tab').count(),5);
  assert.match(await page.locator('.callout').innerText(),/Explore Career Match/);
  await shot('06_profile_overview.png');

  // The name/initials are dynamic, not a baked-in image.
  await button('Edit display name').click();
  await page.getByLabel('Edit your display name').fill('Junhong');
  await button('Save').click();
  assert.equal(await page.locator('.identity-avatar').innerText(),'JU');
  assert.equal(await page.locator('.top-avatar').innerText(),'JU');
  await shot('07_profile_name_initials_update.png');
  await page.reload();
  assert.equal(await page.locator('.identity-avatar').innerText(),'JU','Saved browser-local profile must survive reload');
  await button('Edit display name').click();
  await page.getByLabel('Edit your display name').fill('Avery Lim');
  await button('Save').click();

  await page.getByRole('tab',{name:'Background'}).click();
  await button('Edit Field of study').click();
  await page.getByRole('textbox',{name:'Edit context'}).fill('Computer Science and Robotics');
  await shot('08_profile_background_inline_edit.png');
  await button('Cancel').click();
  assert.match(await page.locator('#profile-content').innerText(),/Computer Science \/ Artificial Intelligence/);
  await button('Edit Field of study').click();
  await page.getByRole('textbox',{name:'Edit context'}).fill('Computer Science and Robotics');
  await button('Save changes').click();
  assert.match(await page.locator('#profile-content').innerText(),/Computer Science and Robotics/);

  await page.getByRole('tab',{name:'Goals & Preferences'}).click();
  await shot('09_profile_goals.png');
  await button('Why this matters').click();
  await page.getByRole('dialog',{name:'Why these details matter'}).waitFor();
  await shot('10_profile_goals_explanation_drawer.png');
  await page.keyboard.press('Escape');
  assert.equal(await page.getByRole('dialog').count(),0);

  await page.getByRole('tab',{name:'Skills'}).click();
  await shot('11_profile_skills_empty.png');
  await button('Add a skill').click();
  await page.getByRole('textbox',{name:'Skill name'}).fill('Python');
  await button('Add skill').click();
  assert.match(await page.locator('#profile-content').innerText(),/Python/);
  await button('Add a skill').click();
  await page.getByRole('textbox',{name:'Skill name'}).fill('Python');
  await button('Add skill').click();
  await page.getByRole('alert').waitFor();
  assert.match(await page.getByRole('alert').innerText(),/already in your profile/);
  await button('Cancel').click();
  await shot('12_profile_skills_populated.png');

  await page.getByRole('tab',{name:'My Record'}).click();
  await shot('13_profile_record_empty.png');
  await button('Add project').click();
  await page.getByLabel('Project title').fill('Campus robotics experiment');
  await page.getByLabel('Description (optional)').fill('A small self-reported coursework project.');
  await button('Save project').click();
  assert.match(await page.locator('#profile-content').innerText(),/Campus robotics experiment/);
  await shot('14_profile_record_populated.png');

  // Navigating away from dirty edit must be guarded.
  await page.getByRole('tab',{name:'Background'}).click();
  await button('Edit Field of study').click();
  await page.getByRole('textbox',{name:'Edit context'}).fill('Unsaved value');
  await page.getByRole('tab',{name:'Skills'}).click();
  await page.getByRole('alertdialog',{name:'Discard unsaved changes?'}).waitFor();
  await shot('15_unsaved_edit_guard.png');
  await button('Stay here').click();
  assert.equal(await page.getByRole('tab',{name:'Background'}).getAttribute('aria-selected'),'true');
  await page.getByRole('tab',{name:'Skills'}).click();
  await button('Discard changes').click();
  await page.getByRole('tab',{name:'Skills'}).waitFor();

  // Separate first-time run confirms adaptive Q3 differs with a career-path goal.
  await page.evaluate(()=>window.MinderPreview.reset());
  await button("I'm studying").click();
  await button('Continue').click();
  await button('Build a path toward a career').click();
  await button('Continue').click();
  await page.getByRole('heading',{name:'Which career are you interested in?'}).waitFor();
  await shot('16_adaptive_career_goal_question.png');

  const mobile = await browser.newContext({viewport:{width:390,height:844},deviceScaleFactor:1});
  const mobilePage = await mobile.newPage();
  mobilePage.on('pageerror',e=>jsErrors.push(e.message));
  await mobilePage.goto(url+'?demo=profile');
  await mobilePage.getByRole('heading',{name:'Your profile'}).waitFor();
  const dims = await mobilePage.evaluate(()=>({scroller:document.querySelector('.tabs-scroller').clientWidth,pill:document.querySelector('.profile-tabs').scrollWidth}));
  assert.ok(dims.pill>dims.scroller,'Five mobile tabs must horizontally scroll instead of crush');
  await mobilePage.screenshot({path:resolve(outputDir,'17_mobile_profile.png'),fullPage:true});
  await mobile.close();

  assert.equal(jsErrors.length,0,`Unexpected page JS errors: ${jsErrors.join('; ')}`);
  console.log('PASS: onboarding, branching, optional skip, Review, saved profile, live initials, inline save/cancel, duplicate skills, My Record, dirty navigation, mobile scrolling; 17 browser screenshots.');
} finally {
  await browser.close();
  await new Promise(r=>server.close(r));
}
