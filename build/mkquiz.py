# -*- coding: utf-8 -*-
"""One page per quiz, at q/<slug>/, plus the shared engine.

Short URL on purpose. Instagram carries no links in a feed post, so the result
card gets screenshotted and the address on it has to be typeable by hand.
q/founder-energy is; discovery-which-energy-do-you-run-on.html is not.

The page ships the quiz as JSON inside itself and scores in the browser.
Nothing is stored and nothing is sent, which keeps the promise the Energy
Discovery already makes, and the answer lives in the URL hash so a result can
be linked, reopened and posted.
"""
import io, os, sys, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from toolgen import page, SITE
from quizdata import load, check
import html as H

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def e(s):
    return H.escape(str(s), quote=True)


# ---- depth ------------------------------------------------------------------
# toolgen renders for the site root. These pages sit two deep, the same as the
# blog, so every relative reference needs lifting. Anything already absolute,
# anchored, a protocol or a data URI is left alone.
_SKIP = re.compile(r'^(https?:|//|/|#|mailto:|tel:|data:|javascript:|\.\./)', re.I)

def deepen(html):
    def fix(m):
        attr, url = m.group(1), m.group(2)
        # An empty src is a placeholder the script fills in later. Prefixing it
        # turned it into src="../../", which is a request for a directory and
        # draws a broken-image icon until the script runs.
        if not url or _SKIP.match(url):
            return m.group(0)
        return '%s="../../%s"' % (attr, url)
    return re.sub(r'\b(href|src|poster)="([^"]*)"', fix, html)


CSS = """
.qz{max-width:40rem;margin:0 auto}
.qz [hidden]{display:none!important}

/* ---- intro ---- */
.qz-intro{text-align:center;padding:8px 0 0}
.qz-intro p{font-size:17px;line-height:1.75;color:#CFC7B4;margin:0 0 22px}
.qz-kick{font-family:var(--util,inherit);font-size:11px;letter-spacing:.2em;
  text-transform:uppercase;color:#D4A856;margin:0 0 14px}
.qz-go{display:inline-flex;align-items:center;justify-content:center;gap:10px;
  min-height:52px;padding:15px 30px;border-radius:999px;border:0;cursor:pointer;
  background:linear-gradient(180deg,#F0CE7E,#D4A856);color:#241B06;
  font-family:var(--util,inherit);font-size:13px;letter-spacing:.16em;
  text-transform:uppercase;font-weight:700;text-decoration:none}
.qz-go:hover{filter:brightness(1.07)}
.qz-go:focus-visible{outline:3px solid #F3E4A8;outline-offset:3px}

/* ---- progress ---- */
.qz-prog{display:flex;gap:6px;justify-content:center;margin:0 0 26px}
.qz-prog i{width:26px;height:4px;border-radius:2px;background:rgba(212,168,86,.22)}
.qz-prog i.on{background:#D4A856}
.qz-prog i.done{background:rgba(212,168,86,.6)}

/* ---- questions ---- */
/* A fieldset is the right element for a radio group and the wrong one to
   leave unstyled: browsers give it a 2px groove border, their own padding and
   min-inline-size:min-content, which drew a grey box round every question and
   pushed the options two pixels out of line with the rest of the page. */
.qz-q{margin:0 0 22px;border:0;padding:0;min-inline-size:0;display:block}
.qz-q legend{display:block;float:none;width:100%;max-width:100%;box-sizing:border-box;
  font-family:Georgia,serif;font-size:clamp(21px,4.2vw,27px);
  color:#FFF8D8;line-height:1.3;padding:0;margin:0 0 20px;text-align:center}
.qz-opts{display:grid;gap:10px}
.qz-opt{display:block;position:relative}
.qz-opt input{position:absolute;opacity:0;width:0;height:0}
.qz-opt span{display:flex;align-items:center;min-height:56px;padding:15px 18px;
  border:1px solid rgba(212,168,86,.28);border-radius:14px;cursor:pointer;
  background:rgba(212,168,86,.04);color:#E4DAC4;font-size:16.5px;line-height:1.5;
  transition:border-color .15s,background .15s,transform .12s}
.qz-opt span:hover{border-color:#D4A856;background:rgba(212,168,86,.11)}
.qz-opt input:focus-visible + span{outline:3px solid #F3E4A8;outline-offset:3px}
.qz-opt input:checked + span{border-color:#D4A856;background:rgba(212,168,86,.18);
  color:#FFF8E8;transform:scale(.985)}
.qz-back{background:none;border:0;color:#9C9484;font:inherit;font-size:14px;
  cursor:pointer;padding:10px 4px;min-height:44px}
.qz-back:hover{color:#F3E4A8}
.qz-back:focus-visible{outline:3px solid #F3E4A8;outline-offset:2px;border-radius:6px}
.qz-navrow{display:flex;justify-content:center;margin:6px 0 0}
"""

CSS += """
/* ---- the reveal ---- */
.qz-res{text-align:center}
.qz-res.noart .qz-name{margin-top:6px}
.qz-res.noart::before{content:"";display:block;width:96px;height:3px;margin:0 auto 22px;
  background:var(--qa,#D4A856);border-radius:2px}
.qz-orb{position:relative;width:min(258px,62vw);aspect-ratio:1;margin:0 auto 18px}
/* The art is not square: goat is 341x640, octopus 640x550. Sizing it to the
   full box and clipping it to a circle left tall animals as a narrow strip and
   pushed wide ones against the ring. It is cut-out artwork on transparency, so
   it needs no circular clip at all, just centring and room to breathe. */
.qz-orb{display:flex;align-items:center;justify-content:center}
.qz-orb img{position:relative;z-index:2;width:auto;height:auto;
  max-width:68%;max-height:68%;object-fit:contain;
  animation:qzPop .62s cubic-bezier(.16,1.02,.3,1.02) both}
/* the glow is a rotating conic behind the art, the same trick the declaration
   uses, so the prize belongs to this site rather than to a confetti library */
.qz-orb::before{content:"";position:absolute;inset:-9%;border-radius:50%;z-index:1;
  background:conic-gradient(from 0deg,var(--qa,#D4A856),transparent 32%,
    var(--qa,#D4A856) 68%,transparent 92%,var(--qa,#D4A856));
  filter:blur(15px);opacity:.55;animation:qzSpin 7s linear infinite}
.qz-orb::after{content:"";position:absolute;inset:0;border-radius:50%;z-index:3;
  border:2px solid var(--qa,#D4A856);opacity:.85;
  animation:qzRing .85s cubic-bezier(.2,.9,.25,1) both}
/* An emblem is circular already and has its own rim, so it fills the orb and
   the orb's ring gets out of the way. The 68% cap is only there because the
   animal art is not square. */
.qz-orb.emb img{max-width:100%;max-height:100%}
.qz-orb.emb::after{display:none}
@keyframes qzPop{from{transform:scale(.55);opacity:0}
  60%{transform:scale(1.05);opacity:1}to{transform:scale(1);opacity:1}}
@keyframes qzSpin{to{transform:rotate(360deg)}}
@keyframes qzRing{from{transform:scale(.6);opacity:0}to{transform:scale(1);opacity:.85}}

.qz-spark{position:absolute;inset:0;z-index:4;pointer-events:none}
.qz-spark i{position:absolute;top:50%;left:50%;width:7px;height:7px;border-radius:50%;
  background:var(--qa,#D4A856);opacity:0;animation:qzFly .9s ease-out both}
@keyframes qzFly{0%{opacity:0;transform:translate(-50%,-50%) scale(.4)}
  25%{opacity:1}100%{opacity:0;
  transform:translate(calc(-50% + var(--dx)),calc(-50% + var(--dy))) scale(.2)}}

.qz-you{font-family:var(--util,inherit);font-size:11px;letter-spacing:.22em;
  text-transform:uppercase;color:var(--qa,#BDB4A4);opacity:.9;margin:0 0 6px}
/* The answer, not a heading. Every result already carries an accent colour
   that was only driving the ring, so it drives the name too: the thing the
   visitor came for should be the loudest thing on the page and should not
   look like the rest of it. */
.qz-name{font-family:Georgia,serif;font-size:clamp(40px,11vw,68px);line-height:1.0;
  color:var(--qa,#FFF8D8);margin:0 0 4px;letter-spacing:-.015em;
  text-shadow:0 0 34px color-mix(in srgb,var(--qa,#D4A856) 45%,transparent);
  animation:qzUp .5s .2s ease-out both}
.qz-rule{width:74px;height:4px;border-radius:2px;margin:0 auto 16px;
  background:var(--qa,#D4A856);opacity:.85;animation:qzUp .5s .25s ease-out both}
.qz-head{font-size:clamp(19px,4vw,23px);line-height:1.5;color:#FFF8E8;
  font-family:Georgia,serif;
  margin:0 auto 18px;max-width:30rem;animation:qzUp .5s .3s ease-out both}
.qz-body{font-size:16.5px;line-height:1.78;color:#CFC7B4;margin:0 auto 26px;
  max-width:32rem;animation:qzUp .5s .4s ease-out both}
@keyframes qzUp{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}

/* ---- share ---- */
.qz-acts{display:flex;flex-wrap:wrap;gap:10px;justify-content:center;margin:0 0 26px}
.qz-btn{display:inline-flex;align-items:center;gap:8px;min-height:48px;
  padding:13px 22px;border-radius:999px;cursor:pointer;font:inherit;font-size:14.5px;
  border:1px solid rgba(212,168,86,.4);background:rgba(212,168,86,.08);color:#F3E4A8}
.qz-btn:hover{border-color:#D4A856;background:rgba(212,168,86,.16)}
.qz-btn:focus-visible{outline:3px solid #F3E4A8;outline-offset:3px}
.qz-btn.pri{background:linear-gradient(180deg,#F0CE7E,#D4A856);color:#241B06;
  border-color:transparent;font-family:var(--util,inherit);font-size:12.5px;
  letter-spacing:.14em;text-transform:uppercase;font-weight:700}
.qz-note{font-size:13.5px;color:#9C9484;margin:0 0 8px}
.qz-url{display:block;margin-top:4px;font-family:var(--util,inherit);font-size:13px;
  letter-spacing:.06em;color:#F3E4A8;overflow-wrap:anywhere;word-break:normal}
.qz-cost{max-width:32rem;margin:0 auto 26px;padding:14px 18px;border-radius:12px;
  border:1px dashed rgba(212,168,86,.32);font-size:15.5px;line-height:1.65;
  color:#C6BCA6;animation:qzUp .5s .5s ease-out both}
.qz-cost b{display:block;font-family:var(--util,inherit);font-size:10.5px;
  letter-spacing:.2em;text-transform:uppercase;color:#BDB4A4;margin:0 0 6px}

.qz-links{max-width:32rem;margin:0 auto 26px;text-align:left}
.qz-links h2{font-family:var(--util,inherit);font-size:10.5px;letter-spacing:.2em;
  text-transform:uppercase;color:#BDB4A4;font-weight:600;margin:0 0 10px}
.qz-links ul{list-style:none;margin:0;padding:0;display:grid;gap:8px}
.qz-links a{display:block;padding:13px 16px;border-radius:12px;text-decoration:none;
  border:1px solid rgba(212,168,86,.24);color:#E4DAC4;font-size:15.5px;min-height:44px}
.qz-links a:hover{border-color:#D4A856;color:#F3E4A8}
.qz-cta{margin:34px 0 0;padding:22px 24px;border:1px solid rgba(212,168,86,.3);
  border-radius:16px;background:rgba(212,168,86,.05);text-align:left}
.qz-cta b{display:block;font-family:Georgia,serif;font-size:20px;color:#FFF8D8;margin:0 0 8px}
.qz-cta p{font-size:15.5px;line-height:1.7;color:#CFC7B4;margin:0 0 16px}
/* This list used to be a stack of gold-bordered rounded boxes, which is
   exactly what an answer option is. Mid-quiz on a phone it read as more
   answers to the question above it. Two changes: it is hidden entirely while
   questions are on screen, and where it does show it is plainly navigation,
   with no border, no box and no gold. */
.qz-more{margin:40px 0 0;border-top:1px solid rgba(212,168,86,.14);padding-top:20px}
.qz-more h2{font-family:var(--util,inherit);font-size:11px;letter-spacing:.2em;
  text-transform:uppercase;color:#8F887A;font-weight:600;margin:0 0 4px}
.qz-more ul{list-style:none;margin:0;padding:0}
.qz-more li{margin:0}
.qz-more a{display:inline-block;padding:7px 0;text-decoration:none;
  color:#9C9484;font-size:14px;line-height:1.45;border:0;background:none;
  border-bottom:1px solid transparent}
.qz-more a:hover,.qz-more a:focus-visible{color:#D4A856;border-bottom-color:rgba(212,168,86,.5)}
.qz-cv{display:none}

@media(prefers-reduced-motion:reduce){
  .qz-orb img,.qz-orb::after,.qz-name,.qz-head,.qz-body{animation:none!important}
  .qz-orb::before{animation:none!important}
  .qz-spark{display:none}
}
"""

JS = r"""
(function(){
  var D = window.KXQUIZ; if(!D) return;
  var $  = function(s){ return document.querySelector(s); };
  var stage=$('#qzstage'), intro=$('#qzintro'), res=$('#qzres');
  var prog=$('#qzprog'), form=$('#qzform');
  var answers = [], at = 0;

  /* ---- scoring. Highest total wins; ties break on the order the results are
     declared, so the same answers always give the same result. ---- */
  function score(){
    var s = {};
    D.results.forEach(function(r){ s[r.key]=0; });
    answers.forEach(function(oi, qi){
      var w = D.questions[qi].options[oi].w;
      for(var k in w){ if(s.hasOwnProperty(k)) s[k] += w[k]; }
    });
    var best = D.results[0].key;
    D.results.forEach(function(r){ if(s[r.key] > s[best]) best = r.key; });
    return best;
  }
  function resultByKey(k){
    for(var i=0;i<D.results.length;i++){ if(D.results[i].key===k) return D.results[i]; }
    return D.results[0];
  }

  /* ---- the hash carries the answers, so a result is a real link. ---- */
  function writeHash(){
    try{ history.replaceState(null,'','#'+answers.join('')); }catch(e){}
  }
  function readHash(){
    var h=(location.hash||'').replace('#','');
    if(!/^[0-9]+$/.test(h) || h.length!==D.questions.length) return null;
    var a=h.split('').map(Number);
    for(var i=0;i<a.length;i++){ if(a[i]>=D.questions[i].options.length) return null; }
    return a;
  }

  function drawProgress(){
    prog.innerHTML='';
    for(var i=0;i<D.questions.length;i++){
      var b=document.createElement('i');
      b.className = i<at ? 'done' : (i===at ? 'on' : '');
      prog.appendChild(b);
    }
    prog.setAttribute('aria-label','Question '+(at+1)+' of '+D.questions.length);
  }

  function renderQ(){
    var q=D.questions[at];
    var h='<fieldset class="qz-q"><legend>'+q.q+'</legend><div class="qz-opts">';
    q.options.forEach(function(o,i){
      h+='<label class="qz-opt"><input type="radio" name="q'+at+'" value="'+i+'"'
        +(answers[at]===i?' checked':'')+'><span>'+o.a+'</span></label>';
    });
    h+='</div></fieldset>';
    if(at>0) h+='<p class="qz-navrow"><button type="button" class="qz-back" id="qzback">Back</button></p>';
    form.innerHTML=h;
    drawProgress();
    var first=form.querySelector('input');
    if(first){
      /* move focus to the question, not the first option, so a screen reader
         hears the question before the choices */
      form.querySelector('legend').setAttribute('tabindex','-1');
      form.querySelector('legend').focus();
    }
    form.querySelectorAll('input').forEach(function(inp){
      inp.addEventListener('change', function(){
        answers[at]=parseInt(inp.value,10);
        tel('answer', {quiz:D.slug, q:at+1, opt:answers[at]});
        setTimeout(next, 190);
      });
    });
    var b=$('#qzback');
    if(b) b.addEventListener('click', function(){ at--; renderQ(); });
  }

  function next(){
    if(at < D.questions.length-1){ at++; renderQ(); }
    else {
      writeHash();
      var k=score();
      tel('complete', {quiz:D.slug, result:k, answers:answers.join('')});
      show(k);
    }
  }

  function sparks(host, colour){
    if(window.matchMedia && window.matchMedia('(prefers-reduced-motion:reduce)').matches) return;
    var w=document.createElement('div'); w.className='qz-spark'; w.setAttribute('aria-hidden','true');
    for(var i=0;i<12;i++){
      var s=document.createElement('i'), a=(Math.PI*2*i)/12, d=88+Math.random()*46;
      s.style.setProperty('--dx', Math.cos(a)*d+'px');
      s.style.setProperty('--dy', Math.sin(a)*d+'px');
      s.style.animationDelay=(0.16+Math.random()*0.16)+'s';
      w.appendChild(s);
    }
    host.appendChild(w);
  }

  /* Telemetry. kx is defined by assets/kx-analytics.js and is a no-op until
     the panel endpoint is filled in there, so these calls are safe to ship
     ahead of the collector existing. */
  function tel(kind, props){
    try{ if(window.kx && window.kx.ev) window.kx.ev(kind, props); }catch(e){}
  }
  tel('view', {quiz:D.slug});

  /* The other quizzes are shown on the intro and on the result, and never
     while a question is on screen, where a list of links below the options
     is just one more thing that looks tappable. */
  function more(on){ var n=$('#qzmore'); if(n) n.hidden=!on; }

  function show(key){
    var r=resultByKey(key);
    intro.hidden=true; stage.hidden=true; res.hidden=false; more(true);
    res.style.setProperty('--qa', r.accent||D.accent);
    $('#qzname').textContent=r.name;
    $('#qzhead').textContent=r.headline||'';
    $('#qzbody').textContent=r.body||'';
    $('#qzcostt').textContent=r.cost||'';
    $('#qzcost').hidden=!r.cost;
    var ln=$('#qzlinks'), ul=ln.querySelector('ul');
    ul.innerHTML='';
    (r.links||[]).forEach(function(l){
      var li=document.createElement('li'), a=document.createElement('a');
      a.href=l.href; a.textContent=l.label; li.appendChild(a); ul.appendChild(li);
    });
    ln.hidden = !(r.links && r.links.length);
    var img=$('#qzart'), orb=$('#qzorb');
    orb.querySelectorAll('.qz-spark').forEach(function(n){ n.remove(); });
    if(r.art){
      img.src=D.base+r.art; img.alt=r.name;
      orb.hidden=false; res.classList.remove('noart');
      orb.classList.toggle('emb', /\.svg$/i.test(r.art));
      sparks(orb, r.accent);
    } else {
      /* no picture for this result, so no ring either. Setting src to the base
         path pointed the image at a directory and drew a broken icon. */
      img.removeAttribute('src'); img.alt='';
      orb.hidden=true; res.classList.add('noart');
    }
    $('#qzurl').textContent=D.shortUrl;
    res.setAttribute('tabindex','-1'); res.focus();
    document.title = D.shareLine+' '+r.name+' | SideKix';
    window.__kxResult = r;
  }
"""

JS += r"""
  /* ---- the card Instagram actually needs ----------------------------------
     A feed post carries no link, so the image is the whole message: it has to
     say what you got, which quiz it was, and where to go, all in pixels. Drawn
     on a canvas rather than screenshotting the DOM, so there is no library and
     the output is the same on every device. 1080x1350 is the portrait slot. */
  function card(r, cb){
    var W=1080, H=1350, c=document.createElement('canvas');
    c.width=W; c.height=H;
    var x=c.getContext('2d');
    var accent=r.accent||D.accent;

    x.fillStyle='#0B0A08'; x.fillRect(0,0,W,H);
    var g=x.createRadialGradient(W/2,560,40,W/2,560,620);
    g.addColorStop(0, accent+'44'); g.addColorStop(1,'rgba(11,10,8,0)');
    x.fillStyle=g; x.fillRect(0,0,W,H);
    x.strokeStyle=accent+'66'; x.lineWidth=3; x.strokeRect(38,38,W-76,H-76);

    function centred(text, y, size, font, fill, max, dry){
      /* the size is passed rather than parsed out of the font string:
         parseInt('400 38px Georgia') returns the weight, 400, which put the
         line height at 520px and threw every line after the name off the
         bottom of the card */
      x.font=font; x.fillStyle=fill; x.textAlign='center'; x.textBaseline='alphabetic';
      var words=String(text).split(' '), line='', lines=[];
      words.forEach(function(w){
        var t=line?line+' '+w:w;
        if(x.measureText(t).width>max && line){ lines.push(line); line=w; }
        else line=t;
      });
      if(line) lines.push(line);
      var lh=size*1.28;
      /* dry runs measure without drawing, so the caller can find out whether a
         block fits before committing to it. A two line result name used to
         push the cost line straight into the footer and the card came out with
         three lines of text on top of each other. */
      if(!dry) lines.forEach(function(L,i){ x.fillText(L, W/2, y+i*lh); });
      return y + lines.length*lh;
    }

    x.font='600 26px Georgia, serif'; x.fillStyle='#BDB4A4'; x.textAlign='center';
    x.fillText(D.shareLine.toUpperCase(), W/2, 150);

    /* Half the quizzes resolve to one of the twelve animals and have art.
       The rest resolve to something that has no picture, so that card is
       typographic: a rule instead of an empty ring, and the name starts
       higher to use the space the art would have taken. */
    function paint(img){
      var top;
      if(img && img.width){
        /* drawImage into a square stretched every animal that is not square,
           and goat at 341x640 came out 88% too wide. Fit inside the ring
           on the artwork's own aspect ratio instead. */
        var S=420, cx=W/2, cy=225+S/2;
        // same reasoning as the page: a circular emblem fills the ring, the
        // animal art is inscribed so its corners cannot escape the circle
        var box = /\.svg$/i.test(r.art||'') ? S : S*0.68;
        var k=Math.min(box/img.width, box/img.height);
        var dw=img.width*k, dh=img.height*k;
        x.drawImage(img, cx-dw/2, cy-dh/2, dw, dh);
        x.beginPath(); x.arc(cx, cy, S/2+10, 0, Math.PI*2);
        x.strokeStyle=accent; x.lineWidth=5; x.stroke();
        top = 782;
      } else {
        x.beginPath(); x.moveTo(W/2-90, 300); x.lineTo(W/2+90, 300);
        x.strokeStyle=accent; x.lineWidth=5; x.stroke();
        top = 430;
      }
      var y=centred(r.name, top, 92, '700 92px Georgia, serif', '#FFF8D8', W-180);
      /* not the accent: four of the twelve are deep reds that vanish on black.
         The ring, the glow and the art already carry the colour. */
      y=centred(r.headline||'', y+30, 40, '400 40px Georgia, serif', '#F3E4A8', W-200);
      var FOOT = H-210;               // where the title, url and wordmark begin
      if(r.cost){
        var end = centred('What it costs you: '+r.cost, y+46, 29,
                          '400 29px system-ui, sans-serif', '#9C9484', W-230, true);
        if(end < FOOT){
          centred('What it costs you: '+r.cost, y+46, 29,
                  '400 29px system-ui, sans-serif', '#9C9484', W-230);
        }
      }

      x.font='600 25px system-ui, sans-serif'; x.fillStyle='#8A8272';
      x.fillText(D.title, W/2, H-190);
      x.font='700 34px system-ui, sans-serif'; x.fillStyle='#F3E4A8';
      x.fillText(D.shortUrl, W/2, H-130);
      x.font='700 27px system-ui, sans-serif'; x.fillStyle='#BDB4A4';
      x.fillText('SIDEKIX', W/2, H-72);
      c.toBlob(function(b){ cb(b, c); }, 'image/png');
    }
    if(!r.art){ paint(null); return; }
    var img=new Image();
    img.crossOrigin='anonymous';
    img.onload=function(){ paint(img); };
    img.onerror=function(){ paint(null); };
    img.src = D.base + r.art;
  }
  /* exposed so the card can be rendered and inspected without a share sheet,
     which is the only way to check what actually gets posted */
  window.__kxCard = card;

  function toast(msg){
    var n=$('#qztoast'); if(!n) return;
    n.textContent=msg; n.hidden=false;
    clearTimeout(n._t); n._t=setTimeout(function(){ n.hidden=true; }, 2600);
  }

  function wireShare(){
    var sh=$('#qzshare'), cp=$('#qzcopy'), dl=$('#qzsave');
    /* Sharing a file is the Instagram path and it only exists on mobile. Where
       it is missing the button saves the image instead, which is the same job
       one step longer, so it is never shown as broken. */
    var canFile = !!(navigator.canShare && navigator.share);
    sh.addEventListener('click', function(){
      var r=window.__kxResult; if(!r) return;
      tel('share', {quiz:D.slug, result:r.key});
      sh.disabled=true; sh.textContent='Making the card...';
      card(r, function(blob){
        sh.disabled=false; sh.textContent='Share my result';
        if(!blob){ toast('Could not make the image'); return; }
        var f=new File([blob], D.slug+'.png', {type:'image/png'});
        if(canFile && navigator.canShare({files:[f]})){
          navigator.share({files:[f], text:D.shareLine+' '+r.name+'. '+D.shortUrl})
            .catch(function(){});
        } else {
          saveBlob(blob); toast('Saved. Post it and tag the link.');
        }
      });
    });
    dl.addEventListener('click', function(){
      var r=window.__kxResult; if(!r) return;
      tel('save', {quiz:D.slug, result:r.key});
      dl.disabled=true;
      card(r, function(blob){ dl.disabled=false; if(blob) saveBlob(blob); });
    });
    cp.addEventListener('click', function(){
      var u=location.href;
      if(navigator.clipboard && navigator.clipboard.writeText){
        navigator.clipboard.writeText(u).then(function(){ toast('Link copied'); },
                                             function(){ toast(u); });
      } else { toast(u); }
    });
  }
  function saveBlob(b){
    var a=document.createElement('a');
    a.href=URL.createObjectURL(b); a.download=D.slug+'.png';
    document.body.appendChild(a); a.click();
    setTimeout(function(){ URL.revokeObjectURL(a.href); a.remove(); }, 1200);
  }

  $('#qzstart').addEventListener('click', function(){
    intro.hidden=true; stage.hidden=false; at=0; answers=[]; renderQ();
    more(false);
    tel('start', {quiz:D.slug, qs:D.questions.length});
  });
  var again=$('#qzagain');
  if(again) again.addEventListener('click', function(){
    try{ history.replaceState(null,'',location.pathname); }catch(e){}
    res.hidden=true; intro.hidden=false; at=0; answers=[]; more(true);
  });
  wireShare();

  /* A shared link opens straight on the result it encodes. */
  var pre=readHash();
  if(pre){
    answers=pre; at=D.questions.length-1;
    var pk=score();
    /* Someone arriving on a shared link did not play the quiz, so this is
       counted separately or the completion rate reads far too high. */
    tel('inbound', {quiz:D.slug, result:pk});
    show(pk);
  }
})();
"""


def build_one(q, others):
    slug = q["slug"]
    url = "%s/q/%s/" % (SITE, slug)
    short = "sidekixhq.com/q/%s" % slug

    b = ['<div class="qz">']

    # ---- intro
    b.append('<section class="qz-intro" id="qzintro">')
    b.append('<p class="qz-kick">%s</p>' % e(q["kicker"]))
    b.append("<p>%s</p>" % e(q["intro"]))
    b.append('<button class="qz-go" type="button" id="qzstart">%s</button>'
             % e(q.get("start_label", "Start")))
    b.append("</section>")

    # ---- questions. The markup is written by JS, but the questions are in the
    # HTML below so the page is not blank to a crawler or without scripting.
    b.append('<section id="qzstage" hidden>')
    b.append('<div class="qz-prog" id="qzprog" role="status" aria-live="polite"></div>')
    b.append('<form id="qzform"></form>')
    b.append("</section>")

    # ---- result
    b.append('<section class="qz-res" id="qzres" hidden aria-live="polite">')
    b.append('<p class="qz-you">%s</p>' % e(q["share_line"]))
    b.append('<div class="qz-orb" id="qzorb"><img id="qzart" alt="" src="" '
             'width="258" height="258" decoding="async"></div>')
    b.append('<h2 class="qz-name" id="qzname"></h2>')
    b.append('<div class="qz-rule" aria-hidden="true"></div>')
    b.append('<p class="qz-head" id="qzhead"></p>')
    b.append('<p class="qz-body" id="qzbody"></p>')
    # the honest half. A result that only flatters is a horoscope.
    b.append('<p class="qz-cost" id="qzcost"><b>What it costs you</b> '
             '<span id="qzcostt"></span></p>')
    b.append('<nav class="qz-links" id="qzlinks" hidden '
             'aria-label="Where to read more"><h2>Start here</h2><ul></ul></nav>')
    b.append('<div class="qz-acts">'
             '<button class="qz-btn pri" type="button" id="qzshare">Share my result</button>'
             '<button class="qz-btn" type="button" id="qzsave">Save the image</button>'
             '<button class="qz-btn" type="button" id="qzcopy">Copy link</button>'
             '</div>')
    b.append('<p class="qz-note" id="qztoast" role="status" hidden></p>')
    b.append('<p class="qz-note">Post the image anywhere. The address on it is '
             '<span class="qz-url" id="qzurl">%s</span></p>' % e(short))

    cta = q.get("cta") or {}
    if cta:
        b.append('<div class="qz-cta"><b>%s</b><p>%s</p>'
                 '<a class="qz-go" href="%s">%s</a></div>'
                 % (e(cta.get("title", "Want the real one?")), e(cta["blurb"]),
                    e(cta["href"]), e(cta["label"])))
    b.append('<p class="qz-navrow"><button type="button" class="qz-back" '
             'id="qzagain">Take it again</button></p>')
    b.append("</section>")

    # ---- the other quizzes, so one shared link leads to the rest
    if others:
        b.append('<nav class="qz-more" id="qzmore" aria-labelledby="qzmoreh">'
                 '<h2 id="qzmoreh">More discoveries</h2><ul>')
        # Six, not sixteen. A sixteen-item tail on every quiz buries the
        # result and reads as a sitemap. Each quiz takes the six that follow
        # it in order and wraps around, so the set differs page to page and
        # the internal linking still reaches all of them.
        for o in others[:6]:
            b.append('<li><a href="../%s/">%s</a></li>' % (e(o["slug"]), e(o["title"])))
        b.append('</ul></nav>')
    b.append('<p class="qz-navrow"><a class="qz-back" href="../../discoveries.html">'
             'All discoveries</a></p>')
    b.append("</div>")
    # Anonymous telemetry. Loaded as its own file rather than inlined so the
    # panel endpoint can be switched on later by editing one file, with no
    # rebuild of the seventeen quiz pages. It runs before the inline engine
    # below it, which is where the tel() calls live.
    b.append('<script src="assets/kx-analytics.js"></script>')

    # ---- the data the engine scores against
    payload = {
        "slug": slug,
        "title": q["title"],
        "shareLine": q["share_line"],
        "shortUrl": short,
        "accent": q.get("accent", "#D4A856"),
        "base": "../../",
        "questions": [{"q": it["q"],
                       "options": [{"a": o["a"], "w": o["w"]} for o in it["options"]]}
                      for it in q["questions"]],
        "results": [{"key": r["key"], "name": r["name"],
                     "headline": r.get("headline", ""), "body": r.get("body", ""),
                     "cost": r.get("cost", ""), "links": r.get("links", []),
                     "art": r["art"], "accent": r.get("accent", q.get("accent"))}
                    for r in q["results"]],
    }
    data_js = ("window.KXQUIZ=" + json.dumps(payload, ensure_ascii=False) + ";")

    schema = [
        {"@context": "https://schema.org", "@type": "Quiz",
         "name": q["title"], "url": url,
         "about": {"@type": "Thing", "name": "Starting a business"},
         "educationalLevel": "beginner",
         "numberOfQuestions": len(q["questions"])},
        {"@context": "https://schema.org", "@type": "BreadcrumbList",
         "itemListElement": [
             {"@type": "ListItem", "position": 1, "name": "SideKix", "item": SITE},
             {"@type": "ListItem", "position": 2, "name": "Discoveries",
              "item": "%s/discoveries.html" % SITE},
             {"@type": "ListItem", "position": 3, "name": q["title"], "item": url}]},
    ]

    title = "%s | SideKix" % q["title"]
    desc = q.get("og_line") or q["intro"]
    back = ('<p class="kx-backrow"><a class="kx-bk" href="../../discoveries.html">'
            '<svg aria-hidden="true" focusable="false" viewbox="0 0 24 24">'
            '<path d="M15 5l-7 7 7 7"></path></svg> Discoveries</a></p>')

    out = "q/%s/index.html" % slug
    os.makedirs(os.path.join(ROOT, "q", slug), exist_ok=True)
    # toolgen writes the file itself and renders for the site root. Rather than
    # add a no-write mode to a helper fifteen generators depend on, the page is
    # written, lifted to its real depth, and written back.
    page(out, title[:120], desc[:300], "A discovery",
         q["title"], q["kicker"], "".join(b),
         css=CSS, js=data_js + JS, schema=schema,
         wrapcls="wrap res", back=back)
    fp = os.path.join(ROOT, out)
    html = deepen(io.open(fp, encoding="utf-8").read())
    # trailingSlash serves this as /q/<slug>/, and the blog pages already
    # canonicalise without the filename. Two URLs for one page is the thing
    # canonical exists to prevent, so it must not name index.html.
    html = html.replace("%s/q/%s/index.html" % (SITE, slug),
                        "%s/q/%s/" % (SITE, slug))
    # the donor carries the sitewide default card, so each quiz points at its
    # own here rather than depending on a later pass to correct it
    ogcard = "%s/assets/og/q-%s.png" % (SITE, slug)
    if os.path.exists(os.path.join(ROOT, "assets", "og", "q-%s.png" % slug)):
        html = re.sub(r'(<meta content=")[^"]*(" property="og:image")',
                      lambda m: m.group(1) + ogcard + m.group(2), html, count=1)
        html = re.sub(r'(<meta content=")[^"]*(" name="twitter:image")',
                      lambda m: m.group(1) + ogcard + m.group(2), html, count=1)
    io.open(fp, "w", encoding="utf-8").write(html)
    return len(html), url, short


def main():
    qs = load()
    problems = 0
    for slug, q in qs.items():
        bad = check(q)
        for x in bad:
            print("  %s: %s" % (slug, x))
        problems += len(bad)
    if problems:
        print("%d problems, nothing written" % problems)
        return 1
    order = list(qs.values())
    total = 0
    for q in order:
        # rotate, so each quiz's "more" list starts at the one after it and
        # every quiz gets linked from roughly the same number of pages
        i = order.index(q)
        others = order[i + 1:] + order[:i]
        n, url, short = build_one(q, others)
        total += n
        print("  %-24s %-34s %d KB" % (q["slug"], short, n // 1024))
    print("%d quizzes, %d KB" % (len(order), total // 1024))
    return 0


if __name__ == "__main__":
    sys.exit(main())
