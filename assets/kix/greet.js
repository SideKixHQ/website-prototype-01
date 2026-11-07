/* Kix greets first-time visitors: corner orb, one-time greeting, and the "What's in your way?" panel. */
window.__KIX_GREETING="assets/kix/audio/greeting.mp3";
window.__KIX_SCRIPTS=[{"k": "funding", "clip": "assets/kix/audio/funding.mp3", "t": "Money's usually the first wall people name, and it's a real one. Often the better question is how little you need to find out if this works. What's the smallest version you could sell to one person? Let's price it out line by line tonight. If outside money makes sense after that, I'll help you get ready before you ask for it, and show you where you'd actually fit."}, {"k": "time", "clip": "assets/kix/audio/time.mp3", "t": "Twenty minutes a night is enough to move something, as long as it's the right twenty minutes. When could you protect three short blocks this week? Pick them now. I'll hand you one step that fits each block, small enough to finish, and the plan keeps track so you don't have to."}, {"k": "where_to_start", "clip": "assets/kix/audio/where_to_start.mp3", "t": "You don't need the whole plan to start. You need the next step, and finding it is my job. What's the idea in one sentence, the way you'd tell a friend? Write that down today. From there we'll lay out the first few steps together, in an order that fits your life, and I'll bring the training for each one when you get there."}, {"k": "fear_of_failure", "clip": "assets/kix/audio/fear_of_failure.mp3", "t": "That fear usually means this matters to you. So we aim to fail small, early and cheap, before anything big is riding on it. Which part are you most worried won't work? Let's test that part first, this week, with something you can try in an afternoon. Whatever happens, you'll know more than you do now."}, {"k": "access", "clip": "assets/kix/audio/access.mp3", "t": "A lot of advice assumes you already have the money, the contacts, or the right title. Plenty of people building something don't, and they build anyway. Which door feels most closed right now: money, people, or know how? Tell me, and I'll find the people, programs and training that open it, and help you get ready to walk through."}, {"k": "unsupported", "clip": "assets/kix/audio/unsupported.mp3", "t": "Building alone is heavier than it looks from the outside, and you don't have to carry all of it. Who's one person you could tell about this today, even in a text? I'll be here whenever you get stuck. And when you're ready, I'll connect you with people building something like yours, and advisors who've stood where you are."}, {"k": "not_ready", "clip": "assets/kix/audio/not_ready.mp3", "t": "Ready usually shows up after people see it, not before. What's the smallest piece you could show one person this week? Pick a date, show it as it is, and let their reaction tell you what to fix first."}, {"k": "overwhelm", "clip": "assets/kix/audio/overwhelm.mp3", "t": "When everything's urgent, it's hard to move anything. If only one thing moved this week, which would make the rest easier? Do that one first. I'll hold the rest of the list so it isn't sitting on you."}, {"k": "something_else", "clip": "assets/kix/audio/something_else.mp3", "t": "Whatever it is, say it the way it comes out. I'll listen first, ask what I need to, and then we'll work out the next step together."}];
window.track=window.track||function(n,p){try{if(window.kx&&kx.ev)kx.ev(n,p||{});}catch(_){}};
(function(){
  const $=s=>document.querySelector(s);
  const track=(n,p)=>{ try{ if(window.track) window.track(n,p||{}); }catch(_){} };
  const RM=matchMedia('(prefers-reduced-motion: reduce)').matches;
  const orb=$('#kxlOrb'), bubble=$('#kxlBubble'), panel=$('#kxlPanel'), said=$('#kxlSaid'), cta=$('#kxlCta'), stateEl=$('#kxlState');
  const chips=[...document.querySelectorAll('.kxl-chip')];
  const orbVoice=new KixVoice($('#kxlOrbCv'),{strands:9,maxSparks:40,scale:1.1}); orbVoice.setState('idle');
  let panelVoice=null;
  // one audio element and one analyser for the whole layer
  const audio=new Audio(); let actx=null, an=null, cur=null, timers=[];
  async function ensureAudio(){ if(!actx){ actx=new (window.AudioContext||window.webkitAudioContext)(); const src=actx.createMediaElementSource(audio); an=actx.createAnalyser(); an.fftSize=1024; src.connect(an); an.connect(actx.destination); } await actx.resume(); }
  function stop(){ timers.forEach(clearTimeout); timers=[]; audio.pause(); [orbVoice,panelVoice].forEach(v=>{ if(v){ v.attachAnalyser(null); v.setLevel(0); v.setState(v===orbVoice?'idle':'listening'); } }); }
  async function play(uri, voice){ try{ await ensureAudio(); audio.src=uri; await audio.play(); voice.attachAnalyser(an); voice.setState('speaking'); return true; }catch(e){ return false; } }

  // greeting: shown once per visitor, a moment after the page settles
  let greeted=false; try{ greeted=localStorage.getItem('kxl_greeted')==='1'; }catch(_){}
  function showBubble(){ bubble.hidden=false; track('kix_greet_shown',{}); }
  function hideBubble(remember){ bubble.hidden=true; stop(); if(remember){ try{ localStorage.setItem('kxl_greeted','1'); }catch(_){} } }
  if(!greeted) setTimeout(showBubble, RM?300:1600);
  window.__kxlReplay=()=>{ try{ localStorage.removeItem('kxl_greeted'); }catch(_){} hideBubble(false); setTimeout(showBubble,150); };
  $('#kxlX').addEventListener('click',()=>{ hideBubble(true); track('kix_greet_dismiss',{}); orb.focus(); });
  $('#kxlHear').addEventListener('click',async()=>{ stop(); const ok=await play(window.__KIX_GREETING, orbVoice); track('kix_greet_hear',{ok}); });
  ['#kxlTell','#kxlMini'].forEach(id=>$(id).addEventListener('click',()=>{ hideBubble(true); openPanel(); track('kix_greet_tell',{from:id}); }));
  // on phones the strip tucks back into the orb once the visitor starts scrolling
  const PHONE=matchMedia('(max-width:599px)');
  addEventListener('scroll',()=>{ if(PHONE.matches && !bubble.hidden && scrollY>120 && audio.paused){ hideBubble(true); track('kix_greet_scrolled_away',{}); } },{passive:true});

  // panel: a modal dialog with the barrier picker
  let lastFocus=null;
  function openPanel(){ lastFocus=document.activeElement; panel.hidden=false; orb.setAttribute('aria-expanded','true'); document.documentElement.style.overflow='hidden';
    if(!panelVoice){ panelVoice=new KixVoice($('#kxlPanelCv'),{strands:14,maxSparks:90}); } panelVoice.setState('listening'); if(panelVoice.kick) panelVoice.kick();
    (chips[0]||$('#kxlClose')).focus(); track('kix_panel_open',{}); }
  function closePanel(){ stop(); panel.hidden=true; orb.setAttribute('aria-expanded','false'); document.documentElement.style.overflow=''; (lastFocus&&lastFocus.focus&&lastFocus.offsetParent!==null?lastFocus:orb).focus(); }
  orb.addEventListener('click',()=>{ hideBubble(true); panel.hidden?openPanel():closePanel(); });
  $('#kxlClose').addEventListener('click',closePanel);
  panel.addEventListener('click',e=>{ if(e.target===panel) closePanel(); });
  document.addEventListener('keydown',e=>{
    if(e.key==='Escape'){ if(!panel.hidden) closePanel(); else if(!bubble.hidden){ hideBubble(true); orb.focus(); } }
    if(e.key==='Tab' && !panel.hidden){ const f=[...panel.querySelectorAll('button,a[href]')].filter(x=>x.offsetParent!==null); if(!f.length) return; const a=f[0], z=f[f.length-1];
      if(e.shiftKey && document.activeElement===a){ e.preventDefault(); z.focus(); } else if(!e.shiftKey && document.activeElement===z){ e.preventDefault(); a.focus(); } }
  });
  const esc=x=>x.replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])).replace(/'/g,'’');
  chips.forEach(c=>c.addEventListener('click',async()=>{
    stop(); const i=+c.dataset.i, S=(window.__KIX_SCRIPTS||[])[i]; if(!S) return;
    chips.forEach(x=>x.setAttribute('aria-pressed',x===c?'true':'false')); cta.classList.remove('in');
    const sentences=S.t.match(/[^.?!]+[.?!]+/g).map(x=>x.trim());
    said.innerHTML='<p class="you in">You: '+esc(c.textContent.trim())+'</p>'+sentences.map(x=>'<p'+(x.endsWith('?')?' class="qline"':'')+'>'+esc(x)+'</p>').join('');
    const sheet=panel.querySelector('.kxl-sheet'); sheet.scrollTo({top:sheet.scrollTop+said.getBoundingClientRect().top-sheet.getBoundingClientRect().top-panel.querySelector('.kxl-head').offsetHeight-12,behavior:RM?'auto':'smooth'});
    const lines=[...said.querySelectorAll('p:not(.you)')], words=sentences.map(x=>x.split(/\s+/).length), total=words.reduce((a,b)=>a+b,0);
    track('kix_panel_barrier',{barrier:S.k});
    const ok = S.clip ? await play(S.clip, panelVoice) : false;
    const dur = ok && audio.duration ? audio.duration*1000 : total/2.6*1000;
    stateEl.textContent='Kix · speaking';
    let at=0; lines.forEach((el,j)=>{ timers.push(setTimeout(()=>el.classList.add('in'), RM?0:at)); at+=dur*words[j]/total; });
    timers.push(setTimeout(()=>{ stateEl.textContent='Kix · listening'; panelVoice.attachAnalyser(null); panelVoice.setState('listening'); cta.classList.add('in'); cta.scrollIntoView({block:'nearest',behavior:RM?'auto':'smooth'}); }, RM?0:dur));
  }));
  audio.addEventListener('ended',()=>{ orbVoice.attachAnalyser(null); orbVoice.setState('idle'); });
  document.querySelectorAll('[data-kxl="answer"]').forEach(a=>a.addEventListener('click',()=>track('kix_panel_answer_in_app',{})));
})();
