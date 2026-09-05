
/* The scoring is the spec's: sum four items per energy, divide by the grand
   total, express as a percentage. The only addition is a rounding pass, so the
   twelve integers on screen still add to 100 rather than to 99 or 101.

   Items are shuffled within the page so the four belonging to one energy are
   not answered as a block, which is what produces a run of identical taps. */
(function(){
  var form=document.getElementById('aform');
  if(!form) return;
  var box=document.getElementById('aitems'),
      startBtn=document.getElementById('astart'),
      intro=document.querySelector('.asmt-intro'),
      err=document.getElementById('aerr'),
      res=document.getElementById('ares'),
      prog=document.getElementById('aprogbar'),
      progn=document.getElementById('aprogn');
  var DATA=null, ORDER=[];

  function esc(t){ return String(t==null?'':t).replace(/[&<>"]/g,function(c){
    return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }

  function shuffle(a){
    for(var i=a.length-1;i>0;i--){ var j=Math.floor(Math.random()*(i+1));
      var t=a[i]; a[i]=a[j]; a[j]=t; }
    return a;
  }

  function render(){
    var flat=[];
    DATA.energies.forEach(function(e){
      e.items.forEach(function(text,i){ flat.push({key:e.key,i:i,text:text}); });
    });
    ORDER=shuffle(flat);
    var html='';
    ORDER.forEach(function(it,n){
      var name='q'+n;
      html+='<fieldset class="aitem" data-key="'+esc(it.key)+'" data-i="'+it.i+'" data-n="'+n+'">'+
            '<legend><span class="aitem-n">'+(n+1)+'</span>'+esc(it.text)+'</legend>'+
            '<div class="aitem-row">';
      DATA.scale.forEach(function(s){
        html+='<label class="opt opt-'+s.value+'">'+
              '<input type="radio" name="'+name+'" value="'+s.value+'">'+
              '<span class="opt-dot" aria-hidden="true"></span>'+
              '<span class="opt-t">'+esc(s.label)+'</span></label>';
      });
      html+='</div></fieldset>';
    });
    box.innerHTML=html;
    page=0;
  }

  function answered(){
    return box.querySelectorAll('input:checked').length;
  }
  var PER=6, page=0;

  function pages(){ return Math.ceil(ORDER.length/PER); }

  function showPage(){
    var items=[].slice.call(box.querySelectorAll('.aitem'));
    items.forEach(function(fs,i){
      fs.hidden = Math.floor(i/PER)!==page;
    });
    /* Each page takes one of the twelve accents. It cannot come from the
       statements themselves: a page holds six different energies and colouring
       them by energy would tell the reader what each item measures, which is
       the whole reason they are shuffled. The page is a neutral carrier. */
    var PAGEC=['#E6323F','#3FAEBD','#DE9E33','#B950C2','#EB2745','#E76A23','#D64635','#BD4FAF',
               '#4B7CC7','#E62B68','#DF4036','#D4A856'];
    form.style.setProperty('--p', PAGEC[page % PAGEC.length]);

    var lab=document.getElementById('apagen');
    if(lab) lab.textContent='Page '+(page+1)+' of '+pages();
    var back=document.getElementById('aback'),
        next=document.getElementById('anext'),
        sub=document.getElementById('asubmit');
    if(back) back.hidden = page===0;
    /* the submit only appears on the last page, so it is never a way to
       skip the rest by accident */
    if(next) next.hidden = page>=pages()-1;
    if(sub)  sub.hidden  = page< pages()-1;
    if(form.scrollIntoView) try{ form.scrollIntoView({behavior:'smooth',block:'start'}); }catch(e){}
  }

  function tick(){
    var n=answered();
    progn.textContent=n;
    prog.style.width=(n/ORDER.length*100).toFixed(1)+'%';
    var lab=document.getElementById('apageleft');
    if(lab) lab.textContent = n+' of '+ORDER.length+' answered';
  }

  box && box.addEventListener('change', function(e){
    if(e.target && e.target.type==='radio'){
      var fs=e.target.closest('.aitem');
      if(fs) fs.classList.remove('missing');
      tick();
    }
  });

  /* ---- what the research changed ----
     Reverse-keyed items were the obvious way to control acquiescence, and the
     evidence went the other way: testing versions of the Grit-s scale on 1,419
     adults found all-positive and all-negative versions both functioned better
     than mixed ones, and mixed wording raises cognitive load without a
     reliable gain.

     They are not needed here anyway, because the distribution scoring already
     neutralises it. Someone who agrees with all 48 gets twelve equal shares;
     agreeing with everything cancels out arithmetically rather than by
     wording. What it cannot catch is inattention, so that is checked directly
     below.

     Options are ordered from least to most, since descending scales are shown
     to pull answers upward. */
  function quality(){
    var vals=[].slice.call(box.querySelectorAll('.aitem')).map(function(fs){
      var s=fs.querySelector('input:checked'); return s?s.value:null; });
    var counts={};
    vals.forEach(function(v){ if(v) counts[v]=(counts[v]||0)+1; });
    var top=0; for(var k in counts) if(counts[k]>top) top=counts[k];
    return {
      straightLining: top/vals.length >= 0.8,
      sameShare: Math.round(top/vals.length*100)
    };
  }

  function scoreIt(){
    var raw={}, order=[];
    DATA.energies.forEach(function(e){ raw[e.key]=0; order.push(e.key); });
    [].slice.call(box.querySelectorAll('.aitem')).forEach(function(fs){
      var sel=fs.querySelector('input:checked');
      if(sel) raw[fs.getAttribute('data-key')] += parseInt(sel.value,10);
    });
    var total=0; order.forEach(function(k){ total+=raw[k]; });
    var exact={}, ints={}, sum=0;
    order.forEach(function(k){
      exact[k]=(raw[k]/total)*100;
      ints[k]=Math.round(exact[k]);
      sum+=ints[k];
    });
    /* the rounding pass: hand the drift to whichever energies were rounded
       furthest, so the twelve shown always add to 100 */
    var drift=100-sum;
    if(drift!==0){
      var by=order.slice().sort(function(a,b){
        var da=exact[a]-ints[a], db=exact[b]-ints[b];
        return drift>0 ? db-da : da-db;
      });
      for(var i=0;i<Math.abs(drift);i++){
        ints[by[i%by.length]] += (drift>0?1:-1);
      }
    }
    return {raw:raw, pct:ints, order:order};
  }

  function show(r){
    var byKey={}; DATA.energies.forEach(function(e){ byKey[e.key]=e; });
    var ranked=r.order.slice().sort(function(a,b){ return r.pct[b]-r.pct[a]; });
    var top=ranked.slice(0,3), low=ranked.slice(-2);

    /* a flat result is a real outcome, not an error, so it is named */
    var q=quality();
    var flag=document.getElementById('aflag');
    if(q.straightLining){
      flag.hidden=false;
      flag.textContent='You picked the same answer for '+q.sameShare+'% of the statements. '+
        'The result below still adds to one hundred, but it is describing your answering '+
        'more than your behaviour. Taking it again with the wording read slowly gives you something usable.';
    } else { flag.hidden=true; }

    var spread=r.pct[ranked[0]]-r.pct[ranked[ranked.length-1]];
    document.getElementById('areslead').textContent = spread<=3
      ? 'Your twelve came out close together, which usually means you answered near the middle throughout or you genuinely draw on all of them evenly. The three below are your highest, but the gap is small.'
      : 'All twelve are part of you. Your highest are the energies you naturally lead with. Your lowest are still there. They simply tend to show up when the moment calls for them.';

    var sc=document.getElementById('ascene');
    if(sc && window.kxScene) window.kxScene(sc, ranked, byKey, r.pct, top);

    var ph=document.getElementById('apractice');
    if(ph && window.kxPractice) window.kxPractice(ph, ranked, byKey, r.pct);

    var tog=document.getElementById('alisttoggle');
    if(tog && !tog.getAttribute('data-wired')){
      tog.setAttribute('data-wired','1');
      tog.addEventListener('click', function(){
        var box=document.getElementById('alistwrap');
        var open=box.hidden;
        box.hidden=!open;
        tog.setAttribute('aria-expanded', open?'true':'false');
        tog.textContent = open ? 'Hide the exact figures' : 'Show the exact figures';
      });
    }

    var chart=document.getElementById('achart');
    chart.innerHTML='<p class="sr-only" id="h-chart">Your twelve energies as percentages</p>'+
      ranked.map(function(k){
        var e=byKey[k], w=Math.max(2, r.pct[k]);
        var isTop=top.indexOf(k)!==-1;
        var ico = e.artSm
          ? '<img class="abar-ico" src="'+esc(e.artSm)+'" alt="" width="34" height="34" loading="lazy" decoding="async">'
          : '<span class="abar-ico abar-noico" aria-hidden="true"></span>';
        return '<div class="abar'+(isTop?' abar-top':'')+'" style="--e:'+esc(e.accent||'#D4A856')+'">'+
          ico+
          '<span class="abar-name">'+esc(e.name)+'</span>'+
          '<span class="abar-track"><span class="abar-fill" style="width:'+w+'%"></span></span>'+
          '<span class="abar-pct">'+r.pct[k]+'%</span></div>';
      }).join('');

    document.getElementById('atop').innerHTML = top.map(function(k){
      var e=byKey[k];
      var art = e.art
        ? '<div class="acard-art"><img src="'+esc(e.art)+'" alt="'+esc(e.name)+'" width="200" height="200" loading="lazy" decoding="async"></div>'
        : '';
      return '<article class="acard" style="--e:'+esc(e.accent||'#D4A856')+'">'+art+
        '<p class="acard-pct">'+r.pct[k]+'%</p>'+
        '<h4 class="acard-name">'+esc(e.name)+'</h4>'+
        '<p class="acard-title">'+esc(e.title)+'</p>'+
        '<p class="acard-short">'+esc(e.short)+'</p>'+
        '<dl class="acard-dl">'+
          '<dt>At work</dt><dd>'+esc(e.work)+'</dd>'+
          '<dt>With people</dt><dd>'+esc(e.relationships)+'</dd>'+
          '<dt>In life</dt><dd>'+esc(e.life)+'</dd>'+
          '<dt>Put it to work</dt><dd>'+esc(e.business)+'</dd>'+
          '<dt>Watch for</dt><dd>'+esc(e.cost)+'</dd>'+
        '</dl>'+
        '<div class="acard-with">'+
          '<p class="acard-withlab">Works well with</p>'+
          '<div class="awith"><p class="awith-n">'+esc(e.balances.name)+
            '<span class="awith-tag awith-bal">balances you</span></p>'+
            '<p class="awith-w">'+esc(e.balances.why)+'</p></div>'+
          '<div class="awith"><p class="awith-n">'+esc(e.amplifies.name)+
            '<span class="awith-tag awith-amp">amplifies you</span></p>'+
            '<p class="awith-w">'+esc(e.amplifies.why)+'</p></div>'+
        '</div></article>';
    }).join('');

    document.getElementById('alow').textContent =
      byKey[low[0]].name+' and '+byKey[low[1]].name+' came out lowest. That is not an absence. '+
      'These are the energies you reach for when a situation calls for them rather than by default, '+
      'and knowing which they are tells you where to bring someone else in.';

    form.hidden=true; res.hidden=false;
    if(res.scrollIntoView) try{ res.scrollIntoView({behavior:'smooth',block:'start'}); }catch(x){}
  }

  form.addEventListener('submit', function(e){
    e.preventDefault();
    var missing=[].slice.call(box.querySelectorAll('.aitem')).filter(function(fs){
      var m=!fs.querySelector('input:checked');
      fs.classList.toggle('missing', m);
      return m;
    });
    if(missing.length){
      err.hidden=false;
      /* naming the page is more use than a total, since that is where they are */
      var pg=Math.floor([].slice.call(box.querySelectorAll('.aitem')).indexOf(missing[0])/PER)+1;
      err.textContent=missing.length+(missing.length===1?' statement still needs':' statements still need')+
        ' an answer. The first is on page '+pg+'.';
      page=pg-1; showPage();
      if(missing[0].scrollIntoView) try{ missing[0].scrollIntoView({behavior:'smooth',block:'center'}); }catch(x){}
      return;
    }
    err.hidden=true;
    show(scoreIt());
  });

  document.addEventListener('click', function(e){
    var t=e.target; if(!t||!t.closest) return;
    if(t.closest('#anext')){
      /* every statement on this page needs an answer before moving on, which
         is what stops someone reaching the end with gaps they cannot find */
      var here=[].slice.call(box.querySelectorAll('.aitem')).filter(function(fs,i){
        return Math.floor(i/PER)===page; });
      var missing=here.filter(function(fs){
        var m=!fs.querySelector('input:checked');
        fs.classList.toggle('missing', m); return m; });
      if(missing.length){
        err.hidden=false;
        err.textContent=missing.length+(missing.length===1?' statement on this page still needs':' statements on this page still need')+' an answer.';
        return;
      }
      err.hidden=true;
      page=Math.min(page+1, pages()-1); showPage(); return;
    }
    if(t.closest('#aback')){ err.hidden=true; page=Math.max(0,page-1); showPage(); return; }
  });

  document.getElementById('aagain').addEventListener('click', function(){
    res.hidden=true; form.hidden=false;
    render(); tick(); showPage(); err.hidden=true;
    if(form.scrollIntoView) try{ form.scrollIntoView({behavior:'smooth',block:'start'}); }catch(x){}
  });

  document.getElementById('acopy').addEventListener('click', function(){
    var lines=[].slice.call(document.querySelectorAll('#achart .abar')).map(function(b){
      return b.querySelector('.abar-name').textContent+': '+b.querySelector('.abar-pct').textContent;
    });
    var txt='My twelve energies\n\n'+lines.join('\n');
    var btn=this;
    function done(){ var was=btn.textContent; btn.textContent='Copied';
      setTimeout(function(){ btn.textContent=was; },1600); }
    if(navigator.clipboard && navigator.clipboard.writeText){
      navigator.clipboard.writeText(txt).then(done, function(){});
    }
  });

  /* ?preview in the address bar fills the answers at random and shows the
     result, so the page can be reviewed without answering forty eight
     statements each time. It does nothing without that parameter. */
  function preview(){
    intro.hidden=true; form.hidden=false;
    [].slice.call(box.querySelectorAll('.aitem')).forEach(function(fs){
      var o=fs.querySelectorAll('input');
      o[Math.floor(Math.random()*o.length)].checked=true;
    });
    tick();
    form.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true}));
  }
  if(/[?&]preview/.test(location.search)){
    setTimeout(preview, 60);
  }

  startBtn.addEventListener('click', function(){
    intro.hidden=true; form.hidden=false; tick();
    if(form.scrollIntoView) try{ form.scrollIntoView({behavior:'smooth',block:'start'}); }catch(x){}
  });

  fetch('energies.json').then(function(r){ return r.json(); }).then(function(d){
    DATA=d; render(); tick(); showPage();
  }).catch(function(){
    intro.innerHTML='<p class="asmt-note">The assessment could not load. Refreshing the page usually fixes it.</p>';
  });
})();


/* ---- the practice step ----
   The research is unambiguous that a results page on its own changes nothing.
   Jelley's review found personality feedback interventions have not been shown
   to improve performance, and feedback intervention theory warns that
   self-focused feedback can be worse than none. What does hold up is the
   implementation intention: 642 tests, effects from d=.27 to .66, roughly
   doubling the rate at which a behaviour actually happens.

   Three conditions raise that effect and all three are built in here. The plan
   is contingent, in if-then form. The energy is self-chosen rather than
   assigned, because motivation moderates the effect. And the plan is rehearsed
   at least once: writing it out is the rehearsal, and the rehearsal card is a
   real thing to do this week. */
(function(){
  window.kxPractice=function(host, ranked, byKey, pct){
    var chosen=null, plan=null;

    function esc(s){ return String(s==null?'':s).replace(/[&<>"]/g,function(c){
      return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }

    function chips(){
      return '<p class="pr-lab">Pick one to work on for the next thirty days</p>'+
        '<p class="pr-note">Any of the twelve. The one you lean on least is the '+
        'obvious choice, but the one you rely on most is often where the cost is.</p>'+
        '<div class="pr-chips">'+ranked.map(function(k){
          var e=byKey[k];
          return '<button type="button" class="pr-chip" data-k="'+k+'" '+
                 'style="--e:'+esc(e.accent)+'" aria-pressed="false">'+
                 (e.artSm?'<img src="'+esc(e.artSm)+'" alt="" width="26" height="26">':'')+
                 esc(e.name)+'<span class="pr-pct">'+pct[k]+'%</span></button>';
        }).join('')+'</div><div id="prbody"></div>';
    }

    function body(k){
      var e=byKey[k];
      return '<div class="pr-open" style="--e:'+esc(e.accent)+'">'+
        '<p class="pr-lab">Thirty days of '+esc(e.name)+'</p>'+
        '<h4 class="pr-h">Choose one plan. Write it out.</h4>'+
        '<p class="pr-note">An if-then plan works because the cue does the '+
        'remembering for you. Pick the one whose situation you actually meet.</p>'+
        '<div class="pr-plans">'+e.plans.map(function(pl,i){
          return '<button type="button" class="pr-plan" data-i="'+i+'" aria-pressed="false">'+
            '<span class="pr-if">If '+esc(pl["if"])+',</span>'+
            '<span class="pr-then">then '+esc(pl.then)+'</span></button>';
        }).join('')+'</div>'+

        '<div class="pr-commit" id="prcommit" hidden>'+
          '<p class="pr-lab">Write it in your own words</p>'+
          '<p class="pr-note">Rehearsing the plan once is what makes it stick. '+
          'Type it rather than copy it.</p>'+
          '<textarea id="prtext" class="pr-text" rows="3" '+
            'aria-label="Write your if-then plan in your own words"></textarea>'+
          '<p class="pr-count" id="prcount"></p>'+
        '</div>'+

        '<div class="pr-reh">'+
          '<p class="pr-lab">And one thing to do this week</p>'+
          '<h5 class="pr-rh">'+esc(e.rehearse.title)+'</h5>'+
          '<p class="pr-rb">'+esc(e.rehearse.body)+'</p>'+
        '</div>'+

        '<div class="pr-acts">'+
          '<button type="button" class="kxcta kxcta-lead" id="prsave">Copy my plan</button>'+
        '</div>'+
      '</div>';
    }

    host.innerHTML=chips();

    host.addEventListener('click', function(ev){
      var t=ev.target; if(!t||!t.closest) return;

      var c=t.closest('.pr-chip');
      if(c){
        chosen=c.getAttribute('data-k'); plan=null;
        [].slice.call(host.querySelectorAll('.pr-chip')).forEach(function(b){
          b.setAttribute('aria-pressed', b===c ? 'true':'false'); });
        document.getElementById('prbody').innerHTML=body(chosen);
        return;
      }

      var pl=t.closest('.pr-plan');
      if(pl){
        plan=parseInt(pl.getAttribute('data-i'),10);
        [].slice.call(host.querySelectorAll('.pr-plan')).forEach(function(b){
          b.setAttribute('aria-pressed', b===pl ? 'true':'false'); });
        var box=document.getElementById('prcommit');
        if(box){ box.hidden=false;
          var ta=document.getElementById('prtext');
          if(ta) ta.focus();
        }
        return;
      }

      if(t.closest('#prsave')){
        var e=byKey[chosen], ta=document.getElementById('prtext');
        var written=(ta&&ta.value.trim()) ? ta.value.trim()
          : 'If '+e.plans[plan]["if"]+', then '+e.plans[plan].then;
        var txt='Thirty days of '+e.name+'\n\nMy plan\n'+written+
                '\n\nThis week\n'+e.rehearse.title+'\n'+e.rehearse.body;
        var b=t.closest('#prsave'), was=b.textContent;
        function done(){ b.textContent='Copied';
          setTimeout(function(){ b.textContent=was; },1800); }
        if(navigator.clipboard&&navigator.clipboard.writeText){
          navigator.clipboard.writeText(txt).then(done,function(){});
        }
      }
    });

    host.addEventListener('input', function(ev){
      if(ev.target && ev.target.id==='prtext'){
        var n=ev.target.value.trim().length;
        var c=document.getElementById('prcount');
        if(c) c.textContent = n<15 ? 'Keep going.' :
          (/\bif\b/i.test(ev.target.value) && /\bthen\b/i.test(ev.target.value)
            ? 'That is the shape. The cue is what does the work.'
            : 'Try to keep the if and the then in it.');
      }
    });
  };
})();


/* ---- the twelve as a scene ----
   The wheel was a picture of numbers already shown in the list below it, which
   is why it read as decoration. This uses the artwork as the chart instead:
   twelve animals laid out by rank, sized by percentage, your strongest large
   and forward and your least-used small and receding.
   
   Size is doing the same job a bar length does, so it stays readable, and the
   thing you look at is the animal rather than an abstraction of it. */
(function(){
  window.kxScene=function(host, ranked, byKey, pct, top){
    function esc(s){ return String(s==null?'':s).replace(/[&<>"]/g,function(c){
      return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }

    var vals=ranked.map(function(k){ return pct[k]; });
    var hi=Math.max.apply(null,vals), lo=Math.min.apply(null,vals);
    var span=Math.max(1, hi-lo);

    /* the spread of results is narrow, roughly 5 to 14 percent, so a linear
       size mapping would make all twelve nearly the same. This widens the
       visible difference without misreporting: the number is always printed. */
    function scale(v){
      var t=(v-lo)/span;                 /* 0 at the lowest, 1 at the highest */
      return 0.34 + Math.pow(t,0.85)*0.66;
    }

    var html='<div class="scene">';
    ranked.forEach(function(k,i){
      var e=byKey[k], v=pct[k], s=scale(v);
      var isTop=top.indexOf(k)!==-1;
      /* the card is inside the figure so it is part of the same focusable
         thing, which is what makes it work for keyboard and touch as well as
         a pointer */
      html+='<figure class="sc'+(isTop?' sc-top':'')+'" style="--e:'+esc(e.accent)+
            ';--s:'+s.toFixed(3)+';--i:'+i+'" tabindex="0" '+
            'aria-label="'+esc(e.name)+', '+v+' percent, ranked '+(i+1)+' of 12. '+
            'Opens what skilled and unskilled look like.">'+
        '<span class="sc-art">'+
          (e.art?'<img src="'+esc(e.art)+'" alt="" loading="lazy" decoding="async">':'')+
        '</span>'+
        '<figcaption class="sc-cap">'+
          '<span class="sc-n">'+esc(e.name)+'</span>'+
          '<span class="sc-p">'+v+'%</span>'+
        '</figcaption>'+
        '<span class="sc-card" role="tooltip">'+
          '<span class="sc-card-h">'+esc(e.name)+'<em>'+v+'%</em></span>'+
          '<span class="sc-card-t">'+esc(e.title)+'</span>'+
          '<span class="sc-col sc-good">'+
            '<span class="sc-col-l">Skilled looks like</span>'+
            '<span class="sc-bul">'+e.skilled.map(function(b){
              return '<span>'+esc(b)+'</span>'; }).join('')+'</span>'+
          '</span>'+
          '<span class="sc-col sc-bad">'+
            '<span class="sc-col-l">Unskilled looks like</span>'+
            '<span class="sc-bul">'+e.unskilled.map(function(b){
              return '<span>'+esc(b)+'</span>'; }).join('')+'</span>'+
          '</span>'+
        '</span>'+
      '</figure>';
    });
    html+='</div>';
    host.innerHTML=html;

    /* On a touch screen there is no hover, so a tap opens the card and a tap
       elsewhere closes it. On a pointer device the CSS already handles it and
       this only adds the pinned state. */
    host.addEventListener('click', function(ev){
      var f=ev.target.closest ? ev.target.closest('.sc') : null;
      [].slice.call(host.querySelectorAll('.sc')).forEach(function(x){
        if(x!==f) x.classList.remove('sc-open');
      });
      if(f) f.classList.toggle('sc-open');
    });
    document.addEventListener('click', function(ev){
      if(!host.contains(ev.target)){
        [].slice.call(host.querySelectorAll('.sc-open')).forEach(function(x){
          x.classList.remove('sc-open'); });
      }
    });
    document.addEventListener('keydown', function(ev){
      if(ev.key==='Escape'){
        [].slice.call(host.querySelectorAll('.sc-open')).forEach(function(x){
          x.classList.remove('sc-open'); });
      }
    });
  };
})();


/* ---- a card you can actually post ----
   The result is a picture of twelve animals, which is the one thing here worth
   sharing, and a screenshot of a web page is a poor version of it. This draws
   the top three onto a canvas at 1200x630, the size LinkedIn and X read for a
   link preview, and hands it over as a PNG.

   Everything it needs is already on the page: the chart rows carry the name,
   the percentage and the plate, in rank order. Reading the DOM rather than the
   scoring means the card can never disagree with what the visitor is looking
   at. The small plates are swapped for the 640px ones so the card is sharp.

   No upload and no service. The canvas is same-origin so it is never tainted,
   and the file is produced and downloaded on the device. */
(function(){
  var acts = document.querySelector('.ares-acts');
  if(!acts || !document.getElementById('achart')) return;

  var W = 1200, H = 630, GOLD = '#D4A856', CREAM = '#FFF6DC', INK = '#0B0A06';

  var btn = document.createElement('button');
  btn.type = 'button';
  btn.className = 'kxcta kxcta-quiet';
  btn.id = 'acard';
  btn.textContent = 'Save a share card';
  acts.appendChild(btn);

  var say = document.createElement('p');
  say.className = 'acard-say';
  say.setAttribute('aria-live', 'polite');
  say.hidden = true;
  acts.parentNode.insertBefore(say, acts.nextSibling);

  function top3(){
    return [].slice.call(document.querySelectorAll('#achart .abar')).slice(0, 3)
      .map(function(b){
        var img = b.querySelector('img');
        return {
          name: (b.querySelector('.abar-name') || {}).textContent || '',
          pct:  (b.querySelector('.abar-pct')  || {}).textContent || '',
          /* the row uses the 200px plate; the card wants the 640px one */
          src:  img ? img.getAttribute('src').replace('-sm.webp', '.webp') : null
        };
      });
  }

  function load(src){
    return new Promise(function(res, rej){
      var i = new Image();
      i.onload = function(){ res(i); };
      i.onerror = rej;
      i.src = src;
    });
  }

  function fonts(){
    if(!document.fonts || !document.fonts.load) return Promise.resolve();
    return Promise.all([
      document.fonts.load('600 62px "Cormorant Garamond"'),
      document.fonts.load('600 40px "Cormorant Garamond"'),
      document.fonts.load('400 20px "Space Grotesk"')
    ]).catch(function(){});
  }

  function draw(rows, imgs){
    var c = document.createElement('canvas');
    c.width = W; c.height = H;
    var x = c.getContext('2d');

    x.fillStyle = INK; x.fillRect(0, 0, W, H);
    var glow = x.createRadialGradient(210, 90, 0, 210, 90, 760);
    glow.addColorStop(0, 'rgba(212,168,86,.17)');
    glow.addColorStop(1, 'rgba(212,168,86,0)');
    x.fillStyle = glow; x.fillRect(0, 0, W, H);

    x.strokeStyle = 'rgba(212,168,86,.34)'; x.lineWidth = 1;
    x.strokeRect(24.5, 24.5, W - 49, H - 49);

    x.font = '400 19px "Space Grotesk", system-ui, sans-serif';
    x.fillStyle = GOLD; x.textBaseline = 'alphabetic';
    x.letterSpacing && (x.letterSpacing = '3px');
    x.fillText('THE TWELVE ENERGIES', 62, 88);
    x.textAlign = 'right';
    x.fillStyle = 'rgba(189,180,164,.85)';
    x.fillText('SIDEKIX', W - 62, 88);
    x.textAlign = 'left';
    x.letterSpacing && (x.letterSpacing = '0px');

    /* three columns, animals sitting on one baseline */
    var base = 400, colW = (W - 160) / 3;
    imgs.forEach(function(im, i){
      if(!im) return;
      var maxH = 210, maxW = colW - 44;
      var s = Math.min(maxH / im.naturalHeight, maxW / im.naturalWidth);
      var w = im.naturalWidth * s, h = im.naturalHeight * s;
      var cx = 80 + colW * i + colW / 2;
      x.drawImage(im, cx - w / 2, base - h, w, h);
    });

    rows.forEach(function(r, i){
      var cx = 80 + colW * i + colW / 2;
      x.textAlign = 'center';
      x.font = '600 40px "Cormorant Garamond", Georgia, serif';
      x.fillStyle = CREAM;
      x.fillText(r.name, cx, base + 56);
      x.font = '400 22px "Space Grotesk", system-ui, sans-serif';
      x.fillStyle = GOLD;
      x.fillText(r.pct, cx, base + 90);
    });

    x.textAlign = 'left';
    x.strokeStyle = 'rgba(212,168,86,.22)';
    x.beginPath(); x.moveTo(62, H - 118); x.lineTo(W - 62, H - 118); x.stroke();

    x.font = '600 30px "Cormorant Garamond", Georgia, serif';
    x.fillStyle = CREAM;
    x.fillText('Everyone runs on all twelve. These are the three I lead with.', 62, H - 74);
    x.font = '400 18px "Space Grotesk", system-ui, sans-serif';
    x.fillStyle = 'rgba(189,180,164,.8)';
    x.fillText('sidekixhq.com/assessment.html', 62, H - 42);
    return c;
  }

  btn.addEventListener('click', function(){
    var rows = top3();
    if(!rows.length) return;
    btn.disabled = true;
    var was = btn.textContent;
    btn.textContent = 'Drawing it';
    say.hidden = true;

    fonts()
      .then(function(){
        return Promise.all(rows.map(function(r){
          return r.src ? load(r.src).catch(function(){ return null; }) : null;
        }));
      })
      .then(function(imgs){
        var c = draw(rows, imgs);
        return new Promise(function(res){ c.toBlob(res, 'image/png'); });
      })
      .then(function(blob){
        if(!blob) throw new Error('no blob');
        var name = 'sidekix-twelve-energies.png';
        var file = null;
        try { file = new File([blob], name, {type: 'image/png'}); } catch(e){}
        /* a phone can hand it straight to the share sheet */
        if(file && navigator.canShare && navigator.canShare({files: [file]})){
          return navigator.share({files: [file], title: 'My twelve energies'})
            .catch(function(){ download(blob, name); });
        }
        download(blob, name);
      })
      .catch(function(err){
        say.hidden = false;
        say.textContent = 'The card could not be drawn. The results above are still yours to copy.';
        if(window.console) console.error('SideKix share card:', err);
      })
      .then(function(){
        btn.disabled = false; btn.textContent = was;
      });
  });

  function download(blob, name){
    var u = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = u; a.download = name;
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(function(){ URL.revokeObjectURL(u); }, 4000);
    say.hidden = false;
    say.textContent = 'Saved as ' + name + '.';
  }
})();
