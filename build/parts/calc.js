<script>
try{
/* ---------------- membership ---------------- */
(function(){
  var sec=document.getElementById('membership'); if(!sec) return;
  var PLANS={
    access :{mo:39, yr:399,  moYear:468,  label:'Access'},
    core   :{mo:99, yr:999,  moYear:1188, label:'Core'},
    premium:{mo:299,yr:3300, moYear:3588, label:'Premium'}
  };
  function money(n){ return '$'+n.toLocaleString('en-US'); }
  var yearly=false;
  function paint(){
    Object.keys(PLANS).forEach(function(k){
      var el=sec.querySelector('[data-tier="'+k+'"]'); if(!el) return;
      var p=PLANS[k];
      if(yearly){
        var saved=p.moYear-p.yr, months=saved/p.mo;
        el.querySelector('[data-price]').textContent=money(p.yr);
        el.querySelector('[data-per]').textContent='per year';
        el.querySelector('[data-sub]').textContent =
          (months>=1.7?'Nearly two months free':(months>=0.9?'A month free':'You save '+money(saved)))+
          ' \u00b7 ' + money(p.mo) + ' a month billed monthly';
      }else{
        el.querySelector('[data-price]').textContent=money(p.mo);
        el.querySelector('[data-per]').textContent='per month';
        el.querySelector('[data-sub]').textContent=money(p.yr)+' a year saves you '+money(p.moYear-p.yr);
      }
    });
  }
  var bmo=document.getElementById('bmo'), byr=document.getElementById('byr');
  function setBill(v){ yearly=v; bmo.setAttribute('aria-pressed',!v); byr.setAttribute('aria-pressed',v); paint(); }
  bmo.addEventListener('click',function(){ setBill(false); });
  byr.addEventListener('click',function(){ setBill(true); });
  paint();

  var seeall=document.getElementById('seeall'), grid=document.getElementById('grid');
  seeall.addEventListener('click',function(){
    var on=grid.classList.toggle('on');
    seeall.setAttribute('aria-expanded',on);
    seeall.textContent = on ? 'Close the comparison' : 'See everything, side by side';
  });

  /* the recommendation follows whatever they picked in the carousel */
  var REC={
    'THE LAYOFF'   :['access','runway is the pressure, so the cheapest way to start moving is the right one'],
    'PERFECTIONISM':['access','you need finish lines and nudges more than anything behind the paywall'],
    'TOOLS'        :['access','member discounts and perks start here'],
    'EDUCATION'    :['access','the resource library and Self-Discoveries are included from the first tier'],
    'MOMENTUM'     :['core','a full Journey Map, redrawn from where the business actually is'],
    'FOCUS'        :['access','one step a day, with the nudges that keep it going'],
    'FEAR'         :['core','it is the first membership with an Advisor session included'],
    'DOUBT'        :['access','the guided map and the twenty questions are all in the first tier'],
    'NO TIME'      :['access','the map, the nudges and the daily step are all here'],
    'FUNDING'      :['core','grants and Capital Readiness both live here'],
    'GROWTH'       :['premium','investor matching and VIP Advisor booking are what a ceiling needs'],
    'LEADERSHIP'   :['core','trainings plus an Advisor to call before the hard conversation'],
    'NEW SKILLS'   :['access','trainings are available from the first tier onward'],
    'NETWORK'      :['premium','this is the tier that lets you build your own Squads'],
    'ANSWERS'      :['free','the live feed and community chat cost nothing, so start there'],
    'SUPPORT'      :['core','Squads are the answer, and Core is where you get invited into one'],
    'BELONGING'    :['access','rooms and the feed are open to you from the first tier'],
    'CREDIBILITY'  :['core','Capital Readiness plus a record an Advisor has signed off on']
  };
  var rectext=document.getElementById('rectext');
  function apply(name,q){
    var r=REC[name]; if(!r) return;
    var e={detail:{name:name,q:q}};
    var tier=r[0], why=r[1];
    var said = e.detail.q ? 'You said <strong>&ldquo;'+e.detail.q+'&rdquo;</strong>' : 'You picked <strong>'+name.toLowerCase()+'</strong>';
    if(tier==='free'){
      rectext.innerHTML=said+' &mdash; and honestly, '+why+'.';
    }else{
      rectext.innerHTML=said+', so we would start you on <strong>'+PLANS[tier].label+'</strong>, because '+why+'.';
    }
    sec.querySelectorAll('.tier').forEach(function(el){
      el.classList.toggle('best', el.dataset.tier===tier);
      var flag=el.querySelector('.flag');
      if(el.dataset.tier===tier && !flag){
        var f=document.createElement('span'); f.className='flag'; f.textContent='For you'; el.insertBefore(f,el.firstChild);
      } else if(el.dataset.tier===tier && flag){ flag.textContent='For you'; }
      else if(flag){ flag.remove(); }
    });
  }
  var QS={};
  (location.search||'').replace(/^\?/,'').split('&').forEach(function(kv){
    var p=kv.split('='); if(p[0]) QS[decodeURIComponent(p[0])]=decodeURIComponent((p[1]||'').replace(/\+/g,' '));
  });
  if(QS.need && REC[QS.need]) apply(QS.need, QS.q||'');
  window.addEventListener('kx:barrier',function(e){ apply(e.detail.name, e.detail.q); });
})();
}catch(e){console.error("SideKix [membership] failed:",e);}
</script>
<script>
try{
/* the info tips */
(function(){
  var holds=[].slice.call(document.querySelectorAll('.ihold'));
  if(!holds.length) return;
  function closeAll(except){
    holds.forEach(function(h){
      if(h===except) return;
      h.classList.remove('on');
      var c=h.closest('.tier'); if(c) c.classList.remove('tipopen');
      var b=h.querySelector('.info'); if(b) b.setAttribute('aria-expanded','false');
    });
  }
  holds.forEach(function(h){
    var btn=h.querySelector('.info');
    btn.addEventListener('click',function(e){
      e.preventDefault(); e.stopPropagation();
      var on=h.classList.toggle('on');
      btn.setAttribute('aria-expanded',on);
      var card=h.closest('.tier');
      if(card) card.classList.toggle('tipopen',on);
      if(on) closeAll(h);
    });
    btn.addEventListener('mousedown',function(e){ e.preventDefault(); });
  });
  document.addEventListener('click',function(){ closeAll(null); });
  window.addEventListener('keydown',function(e){ if(e.key==='Escape') closeAll(null); });
})();
}catch(e){console.error("SideKix [info tips] failed:",e);}
</script>
<script>
try{
/* chrome fades while you read, returns when you reach for it */
(function(){
  var nav=document.getElementById('kx-nav'); if(!nav) return;
  var wm=nav.querySelector('a'); if(wm) wm.classList.add('wm');
  var body=document.body, hideT=null, lastY=window.scrollY, TOUCH=!!(window.matchMedia&&matchMedia('(hover:none)').matches);
  function here(){
    body.classList.remove('chrome-away'); body.classList.add('chrome-here');
    clearTimeout(hideT);
    hideT=setTimeout(function(){ if(window.scrollY>220) away(); }, TOUCH?2200:1500);
  }
  function away(){ body.classList.add('chrome-away'); body.classList.remove('chrome-here'); }
  addEventListener('scroll',function(){
    var y=window.scrollY;
    if(y<160){ here(); }
    else if(y<lastY-4){ here(); }          /* reaching back up */
    else if(y>lastY+4){ away(); }
    lastY=y;
  },{passive:true});
  if(!TOUCH) addEventListener('pointermove',function(e){ if(e.clientY<130) here(); });
  nav.addEventListener('focusin',here);
  here();
})();
}catch(e){console.error("SideKix [chrome] failed:",e);}
</script>
<script>
try{
/* ---------------- membership effects ---------------- */
(function(){
  var RM=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;
  var tiers=document.querySelector('.tiers'); if(!tiers) return;

  /* reveal on approach */
  if('IntersectionObserver' in window && !RM){
    var io=new IntersectionObserver(function(es){
      es.forEach(function(e){ if(e.isIntersecting){ tiers.classList.add('lit'); io.disconnect(); } });
    },{threshold:.2});
    io.observe(tiers);
  } else { tiers.classList.add('lit'); }

  /* the sheen follows the pointer across each card */
  if(!RM && !(window.matchMedia && matchMedia('(hover:none)').matches)){
    [].slice.call(tiers.querySelectorAll('.tier')).forEach(function(card){
      card.addEventListener('pointermove',function(ev){
        var r=card.getBoundingClientRect();
        card.style.setProperty('--px',(ev.clientX-r.left)+'px');
        card.style.setProperty('--py',(ev.clientY-r.top)+'px');
      });
    });
  }

  /* roll the numbers when the billing period changes */
  var money=function(n){ return '$'+Math.round(n).toLocaleString('en-US'); };
  function roll(el,from,to){
    if(RM){ el.textContent=money(to); return; }
    var t0=performance.now(), dur=520;
    el.parentNode.classList.add('rolling');
    (function step(now){
      var k=Math.min(1,(now-t0)/dur), e=1-Math.pow(1-k,3);
      el.textContent=money(from+(to-from)*e);
      if(k<1) requestAnimationFrame(step);
      else el.parentNode.classList.remove('rolling');
    })(t0);
  }
  var prices={access:[39,399],core:[99,999],premium:[299,3300]};
  function hook(id,yearly){
    var b=document.getElementById(id); if(!b) return;
    b.addEventListener('click',function(){
      Object.keys(prices).forEach(function(k){
        var card=tiers.querySelector('[data-tier="'+k+'"]'); if(!card) return;
        var el=card.querySelector('[data-price]');
        var from=parseFloat((el.textContent||'').replace(/[^0-9.]/g,''))||0;
        roll(el, from, prices[k][yearly?1:0]);
        var sub=card.querySelector('[data-sub]');
        if(sub){ sub.classList.add('swap'); setTimeout(function(){ sub.classList.remove('swap'); },320); }
      });
    });
  }
  hook('bmo',false); hook('byr',true);
})();
}catch(e){console.error("SideKix [membership effects] failed:",e);}
</script>
<script>
try{
/* the orb is the menu, so say so until it has been used once */
(function(){
  var nav=document.getElementById('kx-orbnav'); if(!nav) return;
  var cue=document.createElement('div');
  cue.id='kx-orbcue'; cue.textContent='Menu';
  document.body.appendChild(cue);
  var master=document.getElementById('kx-orbmaster'), used=false;
  setTimeout(function(){ if(!used) cue.classList.add('on'); },1400);
  function hide(){ used=true; cue.classList.remove('on'); }
  if(master){ master.addEventListener('click',hide); master.addEventListener('pointerenter',hide); }
})();
}catch(e){console.error("SideKix [orb cue] failed:",e);}
</script>
<script>
try{
(function(){
  var btns=[].slice.call(document.querySelectorAll('.filters button')),
      cards=[].slice.call(document.querySelectorAll('#grid .card')),
      count=document.getElementById('count');
  function apply(cat){
    var n=0;
    cards.forEach(function(c){
      var on = cat==='all' || c.dataset.cat===cat;
      c.hidden=!on; if(on) n++;
    });
    btns.forEach(function(b){ b.setAttribute('aria-pressed', b.dataset.cat===cat ? 'true':'false'); });
    count.textContent = cat==='all' ? ('Showing all '+n+' pieces') : ('Showing '+n+' in '+cat);
  }
  btns.forEach(function(b){ b.addEventListener('click',function(){ apply(b.dataset.cat); }); });
})();
}catch(e){console.error("SideKix [resources] failed:",e);}
</script>
<script>
(function(){
  document.addEventListener('click',function(e){
    var a=e.target&&e.target.closest?e.target.closest('.sk-footer a'):null;
    if(!a) return;
    var href=a.getAttribute('href')||'';
    if(!href||href.charAt(0)==='#') return;
    if(a.getAttribute('target')==='_blank') return;
    e.preventDefault(); e.stopPropagation();
    window.location.href=href;
  },true);
})();
</script>
<script>
try{
(function(){
  var RM=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;
  var grid=document.getElementById('grid'); if(!grid) return;
  var cards=[].slice.call(grid.querySelectorAll('.card'));

  /* reveal in sequence as the grid comes into view */
  if('IntersectionObserver' in window && !RM){
    cards.forEach(function(c,i){ c.style.transitionDelay=(Math.min(i,12)*45)+'ms'; });
    var io=new IntersectionObserver(function(es){
      es.forEach(function(e){ if(e.isIntersecting){ grid.classList.add('lit');
        setTimeout(function(){ cards.forEach(function(c){ c.style.transitionDelay=''; }); },900);
        io.disconnect(); } });
    },{threshold:.05});
    io.observe(grid);
  } else { grid.classList.add('lit'); }

  /* the sheen follows the pointer */
  if(!RM && !(window.matchMedia && matchMedia('(hover:none)').matches)){
    cards.forEach(function(c){
      c.addEventListener('pointermove',function(ev){
        var r=c.getBoundingClientRect();
        c.style.setProperty('--px',(ev.clientX-r.left)+'px');
        c.style.setProperty('--py',(ev.clientY-r.top)+'px');
      });
    });
  }

  /* animate the filter instead of snapping */
  var btns=[].slice.call(document.querySelectorAll('.filters button'));
  var count=document.getElementById('count');
  btns.forEach(function(b){
    b.addEventListener('click',function(){
      var cat=b.dataset.cat, n=0;
      btns.forEach(function(x){ x.setAttribute('aria-pressed', x===b ? 'true':'false'); });
      cards.forEach(function(c){
        var on = cat==='all' || c.dataset.cat===cat;
        if(on) n++;
        if(RM){ c.hidden=!on; return; }
        if(on){
          c.hidden=false;
          requestAnimationFrame(function(){ c.classList.remove('going'); });
        } else {
          c.classList.add('going');
          setTimeout(function(){ if(c.classList.contains('going')) c.hidden=true; },320);
        }
      });
      count.textContent = cat==='all' ? ('Showing all '+n+' pieces') : ('Showing '+n+' in '+cat);
    },true);
  });
})();
}catch(e){console.error("SideKix [resources effects] failed:",e);}
</script>
<script>
try{
(function(){
  var RM=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;
  var grid=document.getElementById('grid'); if(!grid) return;
  var cards=[].slice.call(grid.querySelectorAll('.card'));
  var btns=[].slice.call(document.querySelectorAll('.filters button'));
  var COL={Advisors:'#6FB0E0',Community:'#A6E0B4',Education:'#B18BE4',Funding:'#FFE7A6',Guides:'#5FB6A6',
           Members:'#D2B4F0',Mentorship:'#84D0C6',Mindset:'#FF6367',News:'#DCE2E8',Templates:'#F2933F',Tools:'#F0855A'};

  /* how many pieces sit behind each chip */
  var counts={};
  cards.forEach(function(c){ counts[c.dataset.cat]=(counts[c.dataset.cat]||0)+1; });
  btns.forEach(function(b){
    var n = b.dataset.cat==='all' ? cards.length : (counts[b.dataset.cat]||0);
    if(!b.querySelector('.n')) b.insertAdjacentHTML('beforeend','<span class="n">'+n+'</span>');
  });

  /* a wash of the hovered topic's color behind the whole section */
  var wash=document.createElement('div'); wash.id='reswash'; document.body.appendChild(wash);
  var off=null;
  function washTo(col){
    clearTimeout(off);
    wash.style.setProperty('--wash',col);
    wash.classList.add('on');
  }
  function washOff(){ off=setTimeout(function(){ wash.classList.remove('on'); },260); }
  if(!RM){
    cards.forEach(function(c){
      c.addEventListener('pointerenter',function(){ washTo(COL[c.dataset.cat]||'#D4A856'); });
      c.addEventListener('pointerleave',washOff);
    });
    btns.forEach(function(b){
      b.addEventListener('pointerenter',function(){ washTo(COL[b.dataset.cat]||'#D4A856'); });
      b.addEventListener('pointerleave',washOff);
    });
  }

  /* sheen on the featured piece */
  var feat=document.querySelector('.feat');
  if(feat && !RM){
    feat.addEventListener('pointermove',function(ev){
      var r=feat.getBoundingClientRect();
      feat.style.setProperty('--px',(ev.clientX-r.left)+'px');
      feat.style.setProperty('--py',(ev.clientY-r.top)+'px');
    });
  }

  /* surprise me: pick something from whatever is currently showing */
  var btn=document.createElement('button');
  btn.type='button'; btn.className='surprise'; btn.textContent='Surprise me';
  var count=document.getElementById('count');
  count.parentNode.insertBefore(btn, count.nextSibling);
  btn.addEventListener('click',function(){
    var pool=cards.filter(function(c){ return !c.hidden; });
    if(!pool.length) return;
    var c=pool[Math.floor(Math.random()*pool.length)];
    cards.forEach(function(x){ x.classList.remove('picked'); });
    c.classList.add('picked');
    washTo(COL[c.dataset.cat]||'#D4A856');
    c.scrollIntoView({behavior:RM?'auto':'smooth',block:'center'});
    var link=c.querySelector('h3 a');
    if(link) link.focus({preventScroll:true});
    count.textContent='Picked for you: '+(link?link.textContent.trim():'')+' \u00b7 '+c.dataset.cat;
  });
})();
}catch(e){console.error("SideKix [resources extras] failed:",e);}
</script>
<footer class="sk-footer"><div class="sk-inner"><div class="sk-brand"><div class="sk-word">SideKix</div><p>A complete business operating system. Find a personalized path from where you are to where you want to be.</p><div class="sk-social"><a aria-label="SideKix on LinkedIn" href="https://www.linkedin.com/company/sidekixhq" rel="noopener noreferrer" target="_blank"><svg aria-hidden="true" focusable="false" viewbox="0 0 24 24"><path d="M4.98 3.5a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5zM3 9h4v12H3zM9 9h3.8v1.7h.05c.53-1 1.83-2.05 3.77-2.05C20.4 8.65 21 11 21 14.1V21h-4v-6.1c0-1.45-.03-3.3-2-3.3-2 0-2.3 1.57-2.3 3.2V21H9z"></path></svg></a><a aria-label="SideKix on YouTube" href="https://www.youtube.com/@sidekixhq" rel="noopener noreferrer" target="_blank"><svg aria-hidden="true" focusable="false" viewbox="0 0 24 24"><path d="M23 12s0-3.2-.4-4.7a3 3 0 0 0-2.1-2.1C18.9 4.8 12 4.8 12 4.8s-6.9 0-8.5.4a3 3 0 0 0-2.1 2.1C1 8.8 1 12 1 12s0 3.2.4 4.7a3 3 0 0 0 2.1 2.1c1.6.4 8.5.4 8.5.4s6.9 0 8.5-.4a3 3 0 0 0 2.1-2.1C23 15.2 23 12 23 12zM9.8 15.3V8.7l5.7 3.3z"></path></svg></a><a aria-label="SideKix on Instagram" href="https://www.instagram.com/sidekixhqinc" rel="noopener noreferrer" target="_blank"><svg aria-hidden="true" focusable="false" viewbox="0 0 24 24"><path d="M12 2.2c3.2 0 3.6 0 4.9.07 1.2.05 1.8.25 2.2.42.6.22 1 .48 1.4.9.43.42.7.83.9 1.4.18.44.38 1.05.43 2.25.06 1.28.07 1.66.07 4.9s0 3.6-.07 4.9c-.05 1.2-.25 1.8-.42 2.2-.22.6-.48 1-.9 1.4-.42.43-.83.7-1.4.9-.44.18-1.05.38-2.25.43-1.28.06-1.66.07-4.9.07s-3.6 0-4.9-.07c-1.2-.05-1.8-.25-2.2-.42-.6-.22-1-.48-1.4-.9-.43-.42-.7-.83-.9-1.4-.18-.44-.38-1.05-.43-2.25C2.2 15.6 2.2 15.2 2.2 12s0-3.6.07-4.9c.05-1.2.25-1.8.42-2.2.22-.6.48-1 .9-1.4.42-.43.83-.7 1.4-.9.44-.18 1.05-.38 2.25-.43C8.4 2.2 8.8 2.2 12 2.2zm0 5.4a4.4 4.4 0 1 0 0 8.8 4.4 4.4 0 0 0 0-8.8zm0 7.25a2.85 2.85 0 1 1 0-5.7 2.85 2.85 0 0 1 0 5.7zm5.6-7.44a1.03 1.03 0 1 1-2.06 0 1.03 1.03 0 0 1 2.06 0z"></path></svg></a><a aria-label="SideKix on Facebook" href="https://www.facebook.com/people/SideKix/100091394580450/" rel="noopener noreferrer" target="_blank"><svg aria-hidden="true" focusable="false" viewbox="0 0 24 24"><path d="M22 12a10 10 0 1 0-11.56 9.88v-6.99H7.9V12h2.54V9.8c0-2.5 1.5-3.9 3.77-3.9 1.1 0 2.24.2 2.24.2v2.46h-1.26c-1.24 0-1.63.77-1.63 1.56V12h2.78l-.44 2.89h-2.34v6.99A10 10 0 0 0 22 12z"></path></svg></a><a aria-label="SideKix on Threads" href="https://www.threads.com/@sidekixhqinc" rel="noopener noreferrer" target="_blank"><svg aria-hidden="true" focusable="false" viewbox="0 0 24 24"><path d="M16.4 11.3c-.1-.05-.2-.1-.3-.14-.18-3.3-1.98-5.2-5-5.22h-.04c-1.8 0-3.3.77-4.23 2.17l1.66 1.14c.69-1.05 1.78-1.27 2.57-1.27h.03c.98.01 1.72.3 2.2.85.35.4.58.96.7 1.66-.87-.15-1.8-.19-2.8-.13-2.8.16-4.6 1.8-4.48 4.08.06 1.15.64 2.14 1.62 2.79.83.55 1.9.82 3.01.76 1.47-.08 2.62-.64 3.42-1.66.61-.78.99-1.78 1.16-3.05.7.42 1.22.98 1.5 1.65.5 1.14.53 3-1 4.55-1.35 1.35-2.97 1.94-5.42 1.96-2.71-.02-4.76-.89-6.09-2.59C4.34 16.9 3.7 14.66 3.68 12c.02-2.66.66-4.9 1.9-6.65C6.91 3.65 8.96 2.78 11.67 2.76c2.73.02 4.82.9 6.2 2.6.68.85 1.2 1.9 1.53 3.14l1.95-.52c-.4-1.52-1.05-2.84-1.93-3.93C17.66 1.86 15 .75 11.68.73h-.01C8.35.75 5.72 1.87 4.06 4.06 2.58 6 1.81 8.7 1.79 12v.01c.02 3.3.79 6 2.27 7.94 1.66 2.18 4.29 3.3 7.61 3.32h.01c2.95-.02 5.03-.79 6.74-2.5 2.24-2.23 2.17-5.03 1.43-6.74-.53-1.23-1.54-2.23-2.91-2.9zm-5 4.9c-1.23.07-2.5-.48-2.57-1.66-.05-.88.62-1.86 2.65-1.98.23-.01.46-.02.68-.02.74 0 1.43.07 2.06.21-.23 2.9-1.6 3.4-2.82 3.46z"></path></svg></a><a aria-label="SideKix on Reddit" href="https://www.reddit.com/r/sidekix" rel="noopener noreferrer" target="_blank"><svg aria-hidden="true" focusable="false" viewbox="0 0 24 24"><path d="M22 12.1c0-1.2-1-2.2-2.2-2.2-.6 0-1.1.23-1.5.6-1.5-1-3.5-1.7-5.7-1.8l1-4.6 3.2.7c0 .9.7 1.6 1.6 1.6s1.6-.7 1.6-1.6-.7-1.6-1.6-1.6c-.6 0-1.2.36-1.45.9l-3.6-.77a.5.5 0 0 0-.6.38l-1.1 5.03c-2.2.1-4.2.8-5.7 1.8a2.16 2.16 0 0 0-1.5-.6C2.98 9.9 2 10.9 2 12.1c0 .85.5 1.6 1.2 1.95a4 4 0 0 0-.05.63c0 3.2 3.7 5.8 8.3 5.8s8.3-2.6 8.3-5.8c0-.2-.02-.42-.05-.62.7-.36 1.2-1.1 1.2-1.96zM7.4 13.6c0-.9.7-1.6 1.6-1.6s1.6.7 1.6 1.6-.7 1.6-1.6 1.6-1.6-.72-1.6-1.6zm8.9 4.2c-1.1 1.1-3.2 1.18-3.8 1.18s-2.7-.08-3.8-1.18a.42.42 0 0 1 .6-.6c.7.7 2.2.95 3.2.95s2.5-.25 3.2-.95a.42.42 0 0 1 .6.6zm-.3-2.6c-.9 0-1.6-.72-1.6-1.6s.7-1.6 1.6-1.6 1.6.7 1.6 1.6-.7 1.6-1.6 1.6z"></path></svg></a></div></div><nav aria-labelledby="fh1" class="sk-col"><h2 id="fh1">Explore</h2><ul><li><a href="index.html">Home</a></li><li><a href="how-it-works.html">How it works</a></li><li><a href="membership.html">Membership</a></li><li><a href="library.html">Resources</a></li></ul></nav><nav aria-labelledby="fh2" class="sk-col"><h2 id="fh2">Get started</h2><ul><li><a href="join.html">Early access</a></li><li><a href="become-an-advisor.html">Become an Advisor</a></li><li><a href="partners.html">Partner with us</a></li><li><a href="faq.html">FAQs</a></li></ul></nav><nav aria-labelledby="fh3" class="sk-col"><h2 id="fh3">Company</h2><ul><li><a href="terms.html">Terms of Use</a></li><li><a href="privacy.html">Privacy Policy</a></li><li><a href="cookies.html">Cookie Policy</a></li><li><a href="mailto:support@sidekixhq.com">Support</a></li></ul></nav></div><div class="sk-base"><span>© 2026 Character Limit LLC, doing business as SideKix</span><span>North Carolina, United States</span><span class="sk-tag">Begin. Build. Become.</span><span class="sk-tm">SideKix™ is a trademark of Character Limit LLC. U.S. federal trademark application pending.</span></div></footer><!--kx-tray-links-->
<script>
(function(){
  /* the tray items are real links now, and this app eats clicks, so force them */
  document.addEventListener('click',function(e){
    var a=e.target&&e.target.closest?e.target.closest('.kx-tray-item[href]'):null;
    if(!a) return;
    e.preventDefault(); e.stopPropagation();
    window.location.href=a.getAttribute('href');
  },true);
  /* keep them reachable and visible whenever the tray is open */
  function sync(){
    var tray=document.getElementById('kx-orbtray'); if(!tray) return false;
    var items=[].slice.call(tray.querySelectorAll('.kx-tray-item'));
    if(!items.length) return false;
    var open = tray.dataset.open==='1';
    items.forEach(function(el,i){
      el.style.pointerEvents = open?'auto':'none';
      el.style.opacity = open?'1':'0';
      el.style.transform = open?'translateX(0) scale(1)':'translateX(24px) scale(.7)';
      el.style.transitionDelay = (open? i*45 : (items.length-i)*25)+'ms';
      el.setAttribute('tabindex', open?'0':'-1');
    });
    return true;
  }
  var master=null;
  function wire(){
    var tray=document.getElementById('kx-orbtray');
    master=document.getElementById('kx-orbmaster');
    if(!tray||!master) return false;
    if(master.dataset.tw) return true;
    master.dataset.tw='1';
    document.addEventListener('click',function(e){
      if(!e.target.closest) return;
      if(e.target.closest('#kx-orbmaster')){
        tray.dataset.open = tray.dataset.open==='1' ? '0' : '1';
        master.setAttribute('aria-expanded', tray.dataset.open==='1');
        sync();
      } else if(!e.target.closest('#kx-orbtray')){
        if(tray.dataset.open==='1'){ tray.dataset.open='0'; master.setAttribute('aria-expanded','false'); sync(); }
      }
    },true);
    document.addEventListener('keydown',function(e){
      if(e.key==='Escape' && tray.dataset.open==='1'){ tray.dataset.open='0'; master.setAttribute('aria-expanded','false'); sync(); }
    });
    sync();
    return true;
  }
  var t=0, iv=setInterval(function(){ if(wire()||++t>240) clearInterval(iv); },300);
  if(document.readyState!=='loading') wire(); else document.addEventListener('DOMContentLoaded',wire);
})();
</script>
<!--kx-magnetic-->
<script>
try{
(function(){
  var TOUCH = !!(window.matchMedia && matchMedia('(hover:none)').matches);
  var RM = !!(window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches);
  if(TOUCH||RM) return;

  /* the same pull the home page uses: 0.32 across, 0.42 down */
  var SEL = '.kx-mag,.cta,.go,.wait,.credgo,.joinbtn,.btn,.seeall,.qbtn,.surprise,'
          + '.faqfoot a,.hub,.sk-social a,.bill button,.filters button,.kx-tray-item,.tier .acts a';
  function wire(root){
    [].slice.call((root||document).querySelectorAll(SEL)).forEach(function(el){
      if(el.dataset.mag) return;
      el.dataset.mag='1';
      var t=el.style.transition||'';
      el.style.transition = (t? t+',' : '') + 'transform .25s cubic-bezier(.16,1,.3,1),box-shadow .25s';
      el.addEventListener('pointermove',function(ev){
        var r=el.getBoundingClientRect();
        var dx=ev.clientX-r.left-r.width/2, dy=ev.clientY-r.top-r.height/2;
        el.style.transform='translate('+(dx*0.32)+'px,'+(dy*0.42)+'px)';
      });
      el.addEventListener('pointerleave',function(){ el.style.transform='translate(0,0)'; });
    });
  }
  wire(document);
  /* anything the app re-renders gets wired on the next pass */
  var t=0, iv=setInterval(function(){ wire(document); if(++t>60) clearInterval(iv); },500);
})();
}catch(e){console.error("SideKix [magnetic] failed:",e);}
</script>
<!--kx-lightfix-->
<script>
try{
(function(){
  var RM=!!(window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches);
  var TOUCH=!!(window.matchMedia&&matchMedia('(hover:none)').matches);
  if(RM||TOUCH) return;
  var cur=document.getElementById('kx-cursor'),
      ring=document.getElementById('kx-ring'),
      desat=document.getElementById('kx-desat');
  if(!cur) return;
  var tx=innerWidth/2, ty=innerHeight/2, x=tx, y=ty, mx=tx, my=ty;
  addEventListener('pointermove',function(e){
    tx=e.clientX; ty=e.clientY;
    cur.style.opacity='1'; if(ring) ring.style.opacity='1';
  },{passive:true});
  (function loop(){
    x+=(tx-x)*0.22; y+=(ty-y)*0.22;
    mx+=(tx-mx)*0.09; my+=(ty-my)*0.09;
    cur.style.transform='translate('+x+'px,'+y+'px) translate(-50%,-50%)';
    if(ring) ring.style.transform='translate('+mx+'px,'+my+'px) translate(-50%,-50%)';
    if(desat){ desat.style.setProperty('--mx',mx+'px'); desat.style.setProperty('--my',my+'px'); }
    requestAnimationFrame(loop);
  })();
  document.addEventListener('pointerover',function(e){
    if(e.target.closest && e.target.closest('a,button,input,.card,.hub,.filters button')){
      cur.style.width='58px'; cur.style.height='58px'; }
  },true);
  document.addEventListener('pointerout',function(e){
    if(e.target.closest && e.target.closest('a,button,input,.card,.hub,.filters button')){
      cur.style.width='26px'; cur.style.height='26px'; }
  },true);
})();
}catch(e){console.error("SideKix [light] failed:",e);}
</script>
<div aria-hidden="true" id="kx-support">
<div aria-labelledby="kx-support-h" aria-modal="true" class="box" role="dialog">
<div id="kx-support-form">
<h2 id="kx-support-h">How can we help?</h2>
<p class="sub">Tell us what you need and we will come back to you at the address you leave here.</p>
<label for="sup-name">Your name</label>
<input autocomplete="name" id="sup-name" name="name" type="text"/>
<label for="sup-email">Email address</label>
<input autocomplete="email" id="sup-email" name="email" required="" type="email"/>
<label for="sup-msg">Message</label>
<textarea id="sup-msg" name="message" required=""></textarea>
<div class="row">
<button class="send" id="sup-send" type="button">Send to SideKix</button>
<button class="cancel" id="sup-cancel" type="button">Cancel</button>
</div>
<p class="note" id="sup-note">Goes to support@sidekixhq.com.</p>
</div>
<div class="done" hidden="" id="kx-support-done">
<b>Message sent.</b>
<p>Thank you. We read every one and will reply to the address you gave us.</p>
</div>
</div>
</div><!--kx-support-->
<script>
try{
(function(){
  /* Paste a form endpoint here and the message posts straight through.
     Until then it opens the visitor's mail app with everything filled in,
     so the Support link always does something. */
  var ENDPOINT = 'https://sidekix-email-server.onrender.com/public/form';            /* e.g. 'https://formspree.io/f/xxxxxxx' */
  var TO = 'support@sidekixhq.com';

  var box, lastFocus=null;
  function el(id){ return document.getElementById(id); }
  function open(){
    box=el('kx-support'); if(!box) return;
    lastFocus=document.activeElement;
    box.classList.add('on'); box.setAttribute('aria-hidden','false');
    el('kx-support-form').hidden=false; el('kx-support-done').hidden=true;
    document.documentElement.style.overflow='hidden';
    var f=el('sup-name'); if(f) f.focus();
  }
  function close(){
    if(!box) return;
    box.classList.remove('on'); box.setAttribute('aria-hidden','true');
    document.documentElement.style.overflow='';
    if(lastFocus&&lastFocus.focus) lastFocus.focus();
  }
  function send(){
    var name=(el('sup-name').value||'').trim(),
        mail=(el('sup-email').value||'').trim(),
        msg=(el('sup-msg').value||'').trim();
    if(!mail||!msg){
      el('sup-note').textContent='Please add your email and a message.';
      el('sup-note').style.color='#F3E4A8';
      return;
    }
    if(ENDPOINT){
      fetch(ENDPOINT,{method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json'},
        body:JSON.stringify({form_type:'contact',name:name,email:mail,message:msg})})
        .then(function(){ el('kx-support-form').hidden=true; el('kx-support-done').hidden=false; })
        .catch(function(){ mailtoFallback(name,mail,msg); });
    } else {
      mailtoFallback(name,mail,msg);
    }
  }
  function mailtoFallback(name,mail,msg){
    var subject='Support request'+(name?' from '+name:'');
    var body=msg+'\n\n---\nFrom: '+(name||'(no name)')+'\nReply to: '+mail;
    window.location.href='mailto:'+TO+'?subject='+encodeURIComponent(subject)+'&body='+encodeURIComponent(body);
    el('kx-support-form').hidden=true; el('kx-support-done').hidden=false;
  }

  document.addEventListener('click',function(e){
    var t=e.target; if(!t||!t.closest) return;
    var a=t.closest('a[href^="mailto:support@sidekixhq.com"]');
    if(a && !/subject=/.test(a.getAttribute('href'))){
      e.preventDefault(); e.stopPropagation(); open(); return;
    }
    if(t.closest('#sup-cancel')){ e.preventDefault(); close(); return; }
    if(t.closest('#sup-send')){ e.preventDefault(); send(); return; }
    if(box && box.classList.contains('on') && t===box){ close(); }
  },true);
  document.addEventListener('keydown',function(e){
    if(e.key==='Escape' && box && box.classList.contains('on')) close();
  });
})();
}catch(e){console.error("SideKix [support] failed:",e);}
</script>
<script>
try{

(function(){
  var root=document.querySelector('.calcs'); if(!root) return;
  function n(id){var e=document.getElementById(id);var v=e?parseFloat(e.value):0;return isFinite(v)&&v>0?v:0;}
  function raw(id){var e=document.getElementById(id);var v=e?parseFloat(e.value):0;return isFinite(v)?v:0;}
  var DASH='\u2014';
  function M(x){return isFinite(x)?('$'+Math.round(x).toLocaleString('en-US')):DASH;}
  function P(x){return isFinite(x)?((Math.round(x*10)/10)+'%'):DASH;}
  function set(id,t){var e=document.getElementById(id); if(e) e.textContent=t;}

  function startup(){
    var one=n('s_reg')+n('s_equip')+n('s_web')+n('s_stock')+n('s_pro');
    var mo=n('s_rent')+n('s_tools')+n('s_ins')+n('s_mkt')+n('s_other');
    var mos=n('s_months')||6, total=one+mo*mos;
    set('s_out',M(total)); set('s_one',M(one)); set('s_mo',M(mo)); set('s_run',M(mo*mos));
    set('s_sub','One-time setup plus '+mos+' month'+(mos===1?'':'s')+' of running costs.');
    window.__s='Startup cost estimate: '+M(total)+' total. One-time setup '+M(one)+', monthly running costs '+
      M(mo)+', covering '+mos+' months ('+M(mo*mos)+').';
  }
  function breakeven(){
    var f=n('b_fixed'), p=n('b_price'), v=n('b_var'), c=p-v;
    if(p<=0||c<=0){
      set('b_out',DASH);
      set('b_sub', p<=0?'Add a price to see the breakeven point.'
        :'Your variable cost is at or above your price, so no number of sales breaks even.');
      set('b_units',DASH); set('b_rev',DASH); set('b_margin',DASH); window.__b=''; return;
    }
    var u=Math.ceil(f/c);
    set('b_out',u.toLocaleString('en-US')+' sales');
    set('b_sub','Per month, at '+M(p)+' each, to cover '+M(f)+' of fixed costs.');
    set('b_units',u.toLocaleString('en-US')); set('b_rev',M(u*p)); set('b_margin',P(c/p*100));
    window.__b='Breakeven: '+u+' sales a month at '+M(p)+' each ('+M(u*p)+' revenue). Fixed costs '+
      M(f)+', contribution per sale '+M(c)+', contribution margin '+P(c/p*100)+'.';
  }
  function hourly(){
    var want=n('h_income'), costs=n('h_costs'), wk=n('h_weeks')||46, hrs=n('h_hours')||30, bill=n('h_bill')||60;
    var b=wk*hrs*(bill/100);
    if(b<=0){ set('h_out',DASH); set('h_sub','Add your working weeks and hours.');
      set('h_bh',DASH); set('h_day',DASH); set('h_need',DASH); window.__h=''; return; }
    var need=want+costs, rate=need/b;
    set('h_out',M(rate)+'/hr');
    set('h_sub','To take home '+M(want)+' after '+M(costs)+' of business costs.');
    set('h_bh',Math.round(b).toLocaleString('en-US')+' hrs'); set('h_day',M(rate*8)); set('h_need',M(need));
    window.__h='Hourly rate: '+M(rate)+' an hour. Target income '+M(want)+' plus '+M(costs)+' costs = '+
      M(need)+', across '+Math.round(b)+' billable hours a year ('+wk+' weeks x '+hrs+' hrs at '+bill+
      '% billable). Day rate about '+M(rate*8)+'.';
  }
  function pricing(){
    var mat=n('p_mat'), lab=n('p_lab'), ov=n('p_over'), mg=raw('p_margin'), fee=raw('p_fee');
    var unit=mat+lab+ov;
    if(unit<=0||mg<=0||mg>=100){
      set('p_out',DASH);
      set('p_sub', unit<=0?'Add your unit costs to see a price.':'Enter a target margin between 1 and 99.');
      set('p_unit',M(unit)); set('p_profit',DASH); set('p_net',DASH); window.__p=''; return;
    }
    var price=unit/(1-mg/100);
    var hasFee=(fee>0&&fee<100);
    if(hasFee) price=price/(1-fee/100);
    var feeAmt=hasFee?price*(fee/100):0, net=price-feeAmt-unit;
    set('p_out',M(price));
    set('p_sub','Unit cost '+M(unit)+' at a '+mg+'% target margin.');
    set('p_unit',M(unit)); set('p_profit',M(net)); set('p_net',P(net/price*100));
    window.__p='Suggested price: '+M(price)+'. Unit cost '+M(unit)+' (materials '+M(mat)+', labor '+M(lab)+
      ', overhead '+M(ov)+'), target margin '+mg+'%, payment fees '+fee+'%. Profit per sale about '+
      M(net)+' ('+P(net/price*100)+').';
  }
  var RM=!!(window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches);
  var wash=document.getElementById('reswash');
  if(!wash){ wash=document.createElement('div'); wash.id='reswash'; document.body.appendChild(wash); }
  var off=null;
  function washTo(c){ clearTimeout(off); wash.style.setProperty('--wash',c); wash.classList.add('on'); }
  function washOff(){ off=setTimeout(function(){ wash.classList.remove('on'); },260); }
  if(!RM){
    var CM={startup:'#F0855A',breakeven:'#FFE7A6',hourly:'#5FB6A6',pricing:'#B18BE4'};
    [].slice.call(root.querySelectorAll('.calc')).forEach(function(el){
      el.addEventListener('pointerenter',function(){ washTo(CM[el.id]||'#D4A856'); });
      el.addEventListener('pointerleave',washOff);
    });
    [].slice.call(root.querySelectorAll('.cjump')).forEach(function(el){
      el.addEventListener('pointerenter',function(){ washTo(el.getAttribute('data-c')||'#D4A856'); });
      el.addEventListener('pointerleave',washOff);
    });
  }

  var jumps=[].slice.call(root.querySelectorAll('.cjump'));
  jumps.forEach(function(b){
    b.addEventListener('click',function(){
      var t=document.getElementById(b.getAttribute('data-go')); if(!t) return;
      jumps.forEach(function(x){ x.setAttribute('aria-pressed', x===b ? 'true':'false'); });
      t.scrollIntoView({behavior:RM?'auto':'smooth',block:'start'});
      var f=t.querySelector('input'); if(f) f.focus({preventScroll:true});
    });
  });

  var all=[startup,breakeven,hourly,pricing];
  root.addEventListener('input',function(){ all.forEach(function(f){f();}); });
  all.forEach(function(f){f();});
  root.addEventListener('click',function(ev){
    var b=ev.target.closest && ev.target.closest('.ccopy'); if(!b) return;
    var txt=window['__'+b.getAttribute('data-k')]||''; if(!txt) return;
    var done=function(){ var o=b.textContent; b.textContent='Copied'; b.classList.add('ok');
      setTimeout(function(){ b.textContent=o; b.classList.remove('ok'); },1500); };
    if(navigator.clipboard&&navigator.clipboard.writeText){ navigator.clipboard.writeText(txt).then(done,function(){}); }
    else { var ta=document.createElement('textarea'); ta.value=txt; ta.style.position='absolute';
      ta.style.left='-9999px'; document.body.appendChild(ta); ta.select();
      try{ document.execCommand('copy'); done(); }catch(err){} document.body.removeChild(ta); }
  });
})();

}catch(e){console.error('SideKix [tools.html] failed:',e);}
</script>