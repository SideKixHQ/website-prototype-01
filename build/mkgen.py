# -*- coding: utf-8 -*-
import os, sys, json, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from toolgen import page, crumbs, webapp, faqpage
def e(s): return html.escape(str(s), quote=True)

GEN_CSS = """
/* ---- generators ----
   Answer a few things, get a draft you can edit. The draft is assembled in the
   browser from what you typed, so nothing is sent anywhere and there is nothing
   to wait for. */
.gn{max-width:860px;margin:0 auto;display:grid;gap:34px;
  grid-template-columns:minmax(0,1fr)}
@media(min-width:900px){ .gn{grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:44px;align-items:start} }
.gn-f{display:grid;gap:18px}
.gn-fd label{display:block;font-family:var(--util);font-size:10.5px;letter-spacing:.16em;
  text-transform:uppercase;color:var(--gold);margin:0 0 7px}
.gn-fd input,.gn-fd select,.gn-fd textarea{width:100%;box-sizing:border-box;
  font-family:var(--body);font-size:16px;color:#F1ECE2;
  background:rgba(255,255,255,.04);border:1px solid rgba(212,168,86,.28);
  border-radius:11px;padding:13px 15px;min-height:50px}
.gn-fd textarea{min-height:88px;resize:vertical;line-height:1.65}
.gn-fd input:focus,.gn-fd select:focus,.gn-fd textarea:focus{
  outline:none;border-color:var(--gold);background:rgba(255,255,255,.06)}
.gn-fd .h{display:block;font-family:var(--body);font-size:13px;color:#8E8A82;
  letter-spacing:0;text-transform:none;margin:6px 0 0}
.gn-out{position:sticky;top:96px;border:1px solid rgba(212,168,86,.24);border-radius:16px;
  padding:24px 22px;background:radial-gradient(120% 120% at 50% 0,rgba(33,26,10,.5),rgba(12,11,8,.72))}
.gn-out h2{font-family:var(--util);font-size:10.5px;letter-spacing:.18em;text-transform:uppercase;
  color:var(--gold);margin:0 0 14px}
.gn-draft{width:100%;box-sizing:border-box;min-height:280px;resize:vertical;
  font-family:var(--body);font-size:16px;line-height:1.8;color:#F1ECE2;
  background:rgba(0,0,0,.28);border:1px solid rgba(255,255,255,.08);border-radius:12px;padding:16px}
.gn-draft:focus{outline:none;border-color:var(--gold)}
.gn-acts{display:flex;gap:8px;flex-wrap:wrap;margin:14px 0 0}
.gn-btn{font-family:var(--util);font-size:10.5px;letter-spacing:.16em;text-transform:uppercase;
  padding:11px 17px;min-height:42px;border-radius:999px;cursor:pointer;
  border:1px solid rgba(212,168,86,.45);background:none;color:var(--gold);
  transition:background .25s,color .25s,border-color .25s}
.gn-btn:hover{background:var(--gold);border-color:var(--gold);color:#1B1400}
.gn-btn:focus-visible{outline:3px solid #F3E4A8;outline-offset:3px}
.gn-tip{font-size:14px;line-height:1.7;color:#8E8A82;margin:16px 0 0}
@media(max-width:899px){ .gn-out{position:static;top:auto} }
"""

def fields(fs):
    o = []
    for f in fs:
        o.append('<div class="gn-fd"><label for="%s">%s</label>' % (f["id"], e(f["label"])))
        if f.get("type") == "textarea":
            o.append('<textarea id="%s" placeholder="%s"></textarea>' % (f["id"], e(f.get("ph", ""))))
        elif f.get("type") == "select":
            o.append('<select id="%s">' % f["id"])
            for v in f["opts"]:
                o.append('<option value="%s">%s</option>' % (e(v), e(v)))
            o.append("</select>")
        else:
            o.append('<input id="%s" placeholder="%s" type="text"/>' % (f["id"], e(f.get("ph", ""))))
        if f.get("hint"):
            o.append('<span class="h">%s</span>' % e(f["hint"]))
        o.append("</div>")
    return "".join(o)

def shell(fs, outlabel, tip):
    return ('<div class="gn"><div class="gn-f">' + fields(fs) + "</div>"
            '<aside class="gn-out"><h2>' + e(outlabel) + "</h2>"
            '<textarea aria-label="' + e(outlabel) + '" class="gn-draft" id="gn-draft"></textarea>'
            '<div class="gn-acts">'
            '<button class="gn-btn" data-g="copy" type="button">Copy</button>'
            '<button class="gn-btn" data-g="download" type="button">Download</button>'
            '<button class="gn-btn" data-g="reset" type="button">Start again</button>'
            '</div><p class="gn-tip">' + tip + "</p></aside></div>")

COMMON_JS = r"""
  var draft=document.getElementById('gn-draft');
  var ins=[].slice.call(document.querySelectorAll('.gn-f input,.gn-f select,.gn-f textarea'));
  var edited=false;
  draft.addEventListener('input',function(){ edited=true; });
  function v(id){ var el=document.getElementById(id); return el?el.value.trim():''; }
  function paint(){ if(!edited) draft.value=build(); }
  ins.forEach(function(el){ el.addEventListener('input',paint); el.addEventListener('change',paint); });
  paint();
  var acts=document.querySelector('.gn-acts');
  acts.addEventListener('click',function(ev){
    var b=ev.target.closest('[data-g]'); if(!b) return;
    var k=b.getAttribute('data-g');
    if(k==='copy'){
      var done=function(){ var t=b.textContent; b.textContent='Copied'; setTimeout(function(){b.textContent=t;},1400); };
      if(navigator.clipboard&&navigator.clipboard.writeText){
        navigator.clipboard.writeText(draft.value).then(done,function(){});
      } else { draft.select(); try{ document.execCommand('copy'); done(); }catch(err){} }
    } else if(k==='download'){
      var blob=new Blob([draft.value],{type:'text/plain;charset=utf-8'});
      var a=document.createElement('a'); a.href=URL.createObjectURL(blob);
      a.download=location.pathname.replace(/^.*\//,'').replace('.html','')+'.txt';
      document.body.appendChild(a); a.click(); document.body.removeChild(a);
      setTimeout(function(){ URL.revokeObjectURL(a.href); },1000);
    } else if(k==='reset'){
      ins.forEach(function(el){ if(el.tagName==='SELECT') el.selectedIndex=0; else el.value=''; });
      edited=false; paint();
    }
  });
"""

# ---------------- positioning statement ----------------
POS_FIELDS = [
 dict(id="p_who", label="Who it is for", ph="independent bookkeepers", hint="Be narrower than feels comfortable. One group, described the way they would describe themselves."),
 dict(id="p_prob", label="What they are stuck with", type="textarea", ph="chasing invoices by hand and losing hours to it"),
 dict(id="p_what", label="What you make or do", ph="a scheduling app"),
 dict(id="p_diff", label="What is different about it", type="textarea", ph="it works from the calendar they already keep, so nothing is retyped"),
 dict(id="p_proof", label="Why that is believable", type="textarea", ph="fourteen years running a practice of my own", hint="A fact, not an adjective. Years, numbers, a place you worked, a thing you built."),
]
POS_JS = r"""
  function build(){
    var who=v('p_who'), prob=v('p_prob'), what=v('p_what'), diff=v('p_diff'), proof=v('p_proof');
    if(!who&&!prob&&!what) return '';
    var L=[];
    L.push('For '+(who||'[who it is for]')+' who '+(prob||'[what they are stuck with]')+',');
    L.push((what||'[what you make]')+' is '+(diff?('the one that '+diff):'[what is different]')+'.');
    if(proof) L.push('');
    if(proof) L.push('Which I can say because '+proof+'.');
    L.push('');
    L.push('---');
    L.push('Shorter, for a bio line:');
    L.push('I help '+(who||'[who]')+' '+(prob?('stop '+prob):'[do the thing]')+'.');
    L.push('');
    L.push('Shorter still, for when someone asks what you do:');
    L.push((what||'[what]')+' for '+(who||'[who]')+'.');
    return L.join('\n');
  }
"""
n = page("positioning-statement.html",
 "Positioning Statement Generator | SideKix",
 "Answer five questions and get a positioning statement you can edit, plus a bio line and a one-sentence answer for when somebody asks what you do. Nothing sent anywhere.",
 "Positioning",
 "Say what you do <em>in one sentence</em>.",
 "Five questions, three drafts: the full statement, a bio line, and the version for when somebody asks at a party. Everything is assembled in your browser and the draft is yours to edit.",
 shell(POS_FIELDS, "Your draft",
   "Edit it directly. Once you start typing in the draft it stops rewriting itself, so nothing you change gets overwritten."),
 css=GEN_CSS, js=POS_JS+COMMON_JS,
 schema=(webapp("Positioning Statement Generator","positioning-statement.html",
    "A positioning statement, a bio line and a one-sentence answer, from five questions.",
    ["Full positioning statement","Bio line","One-sentence version","Copy and download"]),
   faqpage([("What is a positioning statement?",
     "One sentence that names who something is for, what they are stuck with, what you make and what is different about it. It is written for you rather than for customers: it is the thing you check other copy against."),
    ("Why does it ask me to be narrow about who it is for?",
     "A statement that fits everybody describes nothing, and it cannot be checked. Naming one group makes the rest of the sentence either true or false, which is what makes it useful.")]),
   crumbs("Positioning statement","positioning-statement.html")))
print("positioning-statement.html %.0f KB" % (n/1024))

# ---------------- outreach email ----------------
OUT_FIELDS = [
 dict(id="o_name", label="Their first name", ph="Dana"),
 dict(id="o_how", label="How you came across them", type="textarea", ph="your talk at the Wilmington chamber last month"),
 dict(id="o_spec", label="The specific thing you noticed", type="textarea", ph="the part about pricing by outcome rather than hours", hint="One real detail. This is the line that decides whether the rest gets read."),
 dict(id="o_you", label="Who you are, in a few words", ph="a bookkeeper starting my own practice"),
 dict(id="o_ask", label="What you are asking for", type="select",
      opts=["Fifteen minutes to ask two questions","To hear how they handled one thing","An introduction to someone","Nothing, just to say it was useful"]),
 dict(id="o_sign", label="Your name", ph="James"),
]
OUT_JS = r"""
  function build(){
    var n=v('o_name'), how=v('o_how'), spec=v('o_spec'), you=v('o_you'), ask=v('o_ask'), sign=v('o_sign');
    if(!n&&!how&&!spec) return '';
    var ASK={
      'Fifteen minutes to ask two questions':'Would you be open to fifteen minutes some time in the next few weeks? I have two questions and I will keep to the time.',
      'To hear how they handled one thing':'If you ever have a spare few minutes, I would like to hear how you handled that. No rush and no obligation.',
      'An introduction to someone':'If anyone comes to mind who I should be talking to, an introduction would mean a lot. If not, no problem at all.',
      'Nothing, just to say it was useful':'Nothing needed from you. I just thought you would want to know it landed.'};
    var L=[];
    L.push('Subject: '+(spec? spec.charAt(0).toUpperCase()+spec.slice(1) : 'A quick note')
           +(n?(' · from '+(sign||'me')):''));
    L.push('');
    L.push('Hi '+(n||'[name]')+',');
    L.push('');
    L.push('I came across '+(how||'[how you came across them]')+', and '
           +(spec?('the thing that stuck with me was '+spec+'.'):'[the specific thing you noticed].'));
    L.push('');
    L.push('I am '+(you||'[who you are]')+', so it landed at a useful moment.');
    L.push('');
    L.push(ASK[ask]||ASK['Fifteen minutes to ask two questions']);
    L.push('');
    L.push('Either way, thank you for putting it out there.');
    L.push('');
    L.push(sign||'[your name]');
    return L.join('\n');
  }
"""
n = page("outreach-email.html",
 "Outreach Email Generator: Reach Out Without the Cringe | SideKix",
 "Six questions and you have a short outreach email that sounds like a person: how you found them, the specific thing you noticed, who you are and one clear ask. Nothing sent anywhere.",
 "Outreach",
 "Reach out <em>without the cringe</em>.",
 "The reason cold outreach reads badly is almost always that it could have been sent to anybody. Six questions, one of which is a real detail about them, and you have a draft that could only have been sent to one person.",
 shell(OUT_FIELDS, "Your draft",
   "Edit it directly. Once you start typing in the draft it stops rewriting itself. The detail you noticed is the part worth the most attention."),
 css=GEN_CSS, js=OUT_JS+COMMON_JS,
 schema=(webapp("Outreach Email Generator","outreach-email.html",
    "A short, specific outreach email from six questions.",
    ["Subject line","Specific opening","One clear ask","Copy and download"]),
   faqpage([("How do I write a cold outreach email that gets a reply?",
     "Make it obvious it could not have been sent to anybody else. One real detail about the person, one sentence on who you are, and one ask small enough to say yes to. Length is not the problem; interchangeability is."),
    ("What should I actually ask for?",
     "Something small enough that saying yes costs almost nothing. Fifteen minutes with two questions ready gets answered far more often than an open request for a chat, because the second one has no visible end.")]),
   crumbs("Outreach email","outreach-email.html")))
print("outreach-email.html %.0f KB" % (n/1024))
