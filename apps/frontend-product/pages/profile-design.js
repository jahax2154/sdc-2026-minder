// Static labels, icons and adaptive wording from approved profile-v2. No demo state.
export const sections = [
      { id:'overview', name:'Overview', icon:'grid' },
      { id:'background', name:'Background', icon:'user' },
      { id:'goals', name:'Goals & Preferences', icon:'target' },
      { id:'skills', name:'Skills', icon:'bars' },
      { id:'record', name:'My Record', icon:'document' }
    ];
export const stages = [
      { id:'studying', title:"I'm studying", desc:"I'm currently in school, college, or university.", icon:'graduation' },
      { id:'entering', title:"I'm entering the workforce", desc:"I'm preparing for my first full-time role.", icon:'briefcase' },
      { id:'working', title:"I'm working", desc:"I'm currently employed in a professional role.", icon:'laptop' },
      { id:'changing', title:"I'm changing careers", desc:"I'm moving into a new field or role.", icon:'switch' },
      { id:'between', title:"I'm between roles", desc:"I'm exploring my next opportunity.", icon:'search' },
      { id:'other', title:'Something else', desc:'My situation is different from these options.', icon:'more' }
    ];
export const studentGoals = [
      { id:'fit', title:'Discover careers that fit me', desc:'Explore roles that match my interests, strengths, and goals.', icon:'brain' },
      { id:'internship', title:'Prepare for internships or my first job', desc:'Get guidance on what to learn, build, and apply for.', icon:'briefcase' },
      { id:'path', title:'Build a path toward a career', desc:'Create a step-by-step plan with skills and milestones.', icon:'bars' },
      { id:'future', title:'Explore future opportunities', desc:'Learn about emerging roles, industries, and trends.', icon:'compass' },
      { id:'unsure', title:"I'm not sure yet", desc:'Help me explore my options.', icon:'chat' }
    ];
export const otherGoals = [
      { id:'fit', title:'Discover careers that fit me', desc:'Explore directions that suit my interests and experience.', icon:'brain' },
      { id:'internship', title:'Prepare for my next role', desc:'Understand what I can build and improve.', icon:'briefcase' },
      { id:'path', title:'Build a path toward a career', desc:'Plan practical steps toward a role I have in mind.', icon:'bars' },
      { id:'future', title:'Explore future opportunities', desc:'Discover possible new fields and directions.', icon:'compass' },
      { id:'unsure', title:"I'm not sure yet", desc:'Explore my options without choosing a role today.', icon:'chat' }
    ];
export const svgPaths = {
      grid:'<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>',
      user:'<path d="M20 21a8 8 0 0 0-16 0"/><circle cx="12" cy="7" r="4"/>',
      target:'<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>',
      bars:'<rect x="4" y="13" width="4" height="8" rx=".5"/><rect x="10" y="8" width="4" height="13" rx=".5"/><rect x="16" y="3" width="4" height="18" rx=".5"/>',
      document:'<path d="M6 2h8l5 5v15H6a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2z"/><path d="M14 2v5h5M8 12h8M8 16h8"/>',
      plus:'<path d="M12 4v16M4 12h16"/>',
      chevron:'<path d="m9 18 6-6-6-6"/>',
      down:'<path d="m6 9 6 6 6-6"/>',
      up:'<path d="m6 15 6-6 6 6"/>',
      back:'<path d="m15 18-6-6 6-6M9 12h12"/>',
      arrow:'<path d="M4 12h16m-7-7 7 7-7 7"/>',
      check:'<path d="m5 12 4 4L19 6"/>',
      x:'<path d="M18 6 6 18M6 6l12 12"/>',
      edit:'<path d="M12 20h9M16.5 3.5a2.12 2.12 0 0 1 3 3L9 17l-4 1 1-4L16.5 3.5z"/>',
      graduation:'<path d="m2 10 10-5 10 5-10 5-10-5zM6 12v5c3 3 9 3 12 0v-5M22 10v7"/>',
      briefcase:'<rect x="3" y="7" width="18" height="14" rx="2"/><path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M3 13c6 4 12 4 18 0"/>',
      laptop:'<rect x="4" y="4" width="16" height="12" rx="1"/><path d="m2 20 2-4h16l2 4H2z"/>',
      switch:'<path d="M4 7h16m-5-5 5 5-5 5M20 17H4m5-5-5 5 5 5"/>',
      search:'<circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/>',
      more:'<circle cx="5" cy="12" r="1"/><circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/>',
      brain:'<path d="M12 6a3 3 0 0 0-5-2 4 4 0 0 0-3 5 4 4 0 0 0 0 7 4 4 0 0 0 3 5 3 3 0 0 0 5-2V6zM12 6a3 3 0 0 1 5-2 4 4 0 0 1 3 5 4 4 0 0 1 0 7 4 4 0 0 1-3 5 3 3 0 0 1-5-2V6zM8 9v7m8-7v7"/>',
      compass:'<circle cx="12" cy="12" r="9"/><path d="m15.8 8.2-2.5 5.1-5.1 2.5 2.5-5.1 5.1-2.5z"/>',
      chat:'<path d="M21 11.5a8.5 8.5 0 0 1-8.5 8.5A8.3 8.3 0 0 1 9 19.3L3 21l1.7-6A8.3 8.3 0 0 1 4 11.5a8.5 8.5 0 1 1 17 0z"/>',
      bot:'<rect x="4" y="7" width="16" height="14" rx="2"/><path d="M12 3v4M9 3h6M1 12h3m16 0h3"/><circle cx="9" cy="13" r="1"/><circle cx="15" cy="13" r="1"/><path d="M9 17h6"/>',
      sprout:'<path d="M12 22V12M12 17c-5 0-8-3-8-8 5 0 8 3 8 8zM12 12c0-5 3-8 8-8 0 5-3 8-8 8z"/>',
      sparkle:'<path d="m12 2 2.4 7.6L22 12l-7.6 2.4L12 22l-2.4-7.6L2 12l7.6-2.4L12 2z"/>',
      info:'<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7h.01"/>',
      clock:'<circle cx="12" cy="12" r="9"/><path d="M12 7v6l4 2"/>',
      library:'<path d="M4 6h5v15H4zM10 3h5v18h-5zM16 8h5v13h-5z"/>',
      paperclip:'<path d="m21 11.5-8 8a6 6 0 0 1-8.5-8.5l9-9a4 4 0 0 1 5.7 5.7L9 17.9a2 2 0 0 1-2.8-2.8l9-9"/>'
    };
export const icon = (name, size=20) => `<svg class="icon" viewBox="0 0 24 24" width="${size}" height="${size}" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${svgPaths[name]||svgPaths.info}</svg>`;

export function contextDefinition(stage,goal) {
      if (stage === 'studying') {
        if (goal==='fit'||goal==='internship') return {title:"What are you studying?",label:'Field of study',placeholder:'e.g. Computer Science / Artificial Intelligence',required:true,study:true,desc:'We use your current studies as a starting point, not a limit on your options.'};
        if (goal==='path') return {title:'Which career are you interested in?',label:'Career or role',placeholder:'e.g. Robotics Engineer',required:true,desc:'A rough direction is enough—you can change it later.'};
        if (goal==='future') return {title:'Which fields or technologies interest you?',label:'Interests',placeholder:'e.g. AI, Robotics, Healthcare',required:false,desc:'Any topic that catches your curiosity is useful.'};
        return {title:'Which subjects or activities do you enjoy?',label:'Subjects or activities',placeholder:'e.g. Mathematics, coding, design',required:false,desc:'You can leave this open if you are still exploring.'};
      }
      if (stage==='changing' && goal==='path') return {title:'Which career would you like to move toward?',label:'Career or role',placeholder:'e.g. Data Scientist',required:false,desc:'A direction is helpful but not required.'};
      if (stage==='changing') return {title:'What kind of work do you do now?',label:'Current role or field',placeholder:'e.g. Operations coordinator',required:false,desc:'Use a broad description if you prefer.'};
      if (stage==='entering') return {title:'What did you study or learn most recently?',label:'Study or experience',placeholder:'e.g. Diploma in Business',required:false,desc:'Formal and informal experience both count.'};
      if (goal==='path') return {title:'Which career are you interested in?',label:'Career or role',placeholder:'e.g. UX Designer',required:false,desc:'Any starting direction works.'};
      if (goal==='future') return {title:'Which fields interest you?',label:'Interests',placeholder:'e.g. Green energy, software',required:false,desc:'You can explore beyond your current work.'};
      return {title:'What would you like Minder to know about your background?',label:'Current background',placeholder:'Describe your studies or experience briefly',required:false,desc:'A short answer is enough; you can fill in details later.'};
    }

export function initials(name) {
      const words = String(name||'').trim().split(/\s+/u).filter(Boolean);
      if (!words.length) return '?';
      const graphemes = s => (typeof Intl.Segmenter === 'function' ? Array.from(new Intl.Segmenter(undefined,{granularity:'grapheme'}).segment(s), x=>x.segment) : Array.from(s));
      return (words.length === 1 ? graphemes(words[0]).slice(0,2).join('') : graphemes(words[0])[0]+graphemes(words[words.length-1])[0]).toLocaleUpperCase();
    }
