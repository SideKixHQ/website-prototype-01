# -*- coding: utf-8 -*-
import os, sys, json, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from toolgen import page, crumbs, webapp, faqpage
def e(s): return html.escape(str(s), quote=True)

CSS = """
/* ---- founder diagnostic ----
   The same shape as the advisor screener: one question at a time, an answer at
   the end that names where you are and points at the things on this site that
   fit. It reads the answers rather than scoring them out of ten, because a
   number would imply a precision that six questions do not have. */
.dg{max-width:760px;margin:0 auto}
.dg-prog{display:flex;align-items:center;gap:14px;margin:0 0 30px}
.dg-prog span{font-family:var(--util);font-size:10.5px;letter-spacing:.16em;
  text-transform:uppercase;color:#9C968D;flex:none}
.dg-bar{flex:1 1 auto;height:4px;border-radius:99px;background:rgba(212,168,86,.16);overflow:hidden}
.dg-bar i{display:block;height:100%;width:0;border-radius:99px;
  background:linear-gradient(90deg,#A1853E,#F3E4A8);transition:width .5s cubic-bezier(.16,1,.3,1)}
.dg-q{display:none}
.dg-q.on{display:block;animation:dgIn .5s cubic-bezier(.16,1,.3,1) both}
@keyframes dgIn{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
.dg-q h2{font-family:var(--display);font-size:clamp(24px,3.6vw,34px);color:#FFF8E8;
  line-height:1.2;margin:0 0 22px}
.dg-opts{display:grid;gap:10px;margin:0 0 22px}
.dg-o{display:block;width:100%;text-align:left;cursor:pointer;
  border:1px solid rgba(212,168,86,.26);border-radius:13px;padding:17px 19px;
  background:rgba(255,255,255,.02);color:#CEC9BC;
  font-family:var(--body);font-size:16px;line-height:1.55;
  transition:border-color .25s,background .25s,color .25s,transform .25s}
.dg-o:hover{border-color:var(--gold);background:rgba(212,168,86,.07);color:#F1ECE2;transform:translateX(3px)}
.dg-o:focus-visible{outline:3px solid #F3E4A8;outline-offset:3px}
.dg-back{font-family:var(--util);font-size:10px;letter-spacing:.16em;text-transform:uppercase;
  color:#7E7A73;background:none;border:none;cursor:pointer;padding:8px 0;min-height:40px}
.dg-back:hover{color:var(--gold)}
.dg-res{display:none}
.dg-res.on{display:block;animation:dgIn .6s cubic-bezier(.16,1,.3,1) both}
.dg-res h2{font-family:var(--display);font-size:clamp(28px,4.4vw,44px);color:#FFF8E8;
  line-height:1.12;margin:0 0 14px}
.dg-res h2 em{font-style:italic;color:var(--gold)}
.dg-lede{font-size:17px;line-height:1.8;color:#CEC9BC;margin:0 0 30px}
.dg-next{display:grid;gap:12px;margin:0 0 26px}
.dg-card{display:block;text-decoration:none;border:1px solid rgba(212,168,86,.24);
  border-radius:14px;padding:20px 22px;
  background:radial-gradient(120% 120% at 50% 0,rgba(33,26,10,.45),rgba(12,11,8,.7));
  transition:border-color .3s,transform .3s}
.dg-card:hover{border-color:var(--gold);transform:translateY(-2px)}
.dg-card b{display:block;font-family:var(--display);font-size:21px;color:#FFF8E8;margin:0 0 4px}
.dg-card span{display:block;font-size:15px;line-height:1.6;color:#9C968D}
.dg-again{font-family:var(--util);font-size:10.5px;letter-spacing:.16em;text-transform:uppercase;
  padding:12px 20px;min-height:44px;border-radius:999px;cursor:pointer;
  border:1px solid rgba(212,168,86,.45);background:none;color:var(--gold)}
.dg-again:hover{background:var(--gold);border-color:var(--gold);color:#1B1400}
"""

# question, options -> each option carries a tag
QS = [
 ("Where is the thing right now?", [
   ("It is an idea I have not told many people about", "idea"),
   ("I have told people and I am working out whether it holds up", "validate"),
   ("It exists and a few people have paid for it", "early"),
   ("It is running and I am trying to make it bigger or steadier", "running")]),
 ("What takes up most of your thinking?", [
   ("Whether it is even the right thing to build", "direction"),
   ("Finding people who want it", "customers"),
   ("The money side, in or out", "money"),
   ("There is too much to do and no order to it", "order")]),
 ("How much of your week goes to it?", [
   ("Evenings and weekends around a job", "sidehours"),
   ("Most of a week, most weeks", "fulltime"),
   ("It varies wildly and that is part of the problem", "erratic")]),
 ("Who do you talk to about it?", [
   ("Nobody, really", "alone"),
   ("Friends and family, who are kind about it", "kind"),
   ("Other people building things", "peers"),
   ("Someone further along than me", "mentor")]),
 ("What would help most in the next month?", [
   ("Deciding something and stopping the going back and forth", "decide"),
   ("A first customer, or the next one", "sales"),
   ("Getting the legal and money side set up properly", "setup"),
   ("A system so the same things stop falling over", "systems")]),
]

# a read, keyed by the first answer, then adjusted by the rest
READS = {
 "idea": ("You are at the point where <em>talking about it</em> is the work.",
   "Nothing about an idea is knowable from inside your own head. The work at this stage is not building; it is finding out whether the thing you imagine is a thing anybody else recognises. That is uncomfortable and it is also the fastest part of the whole process, because a conversation costs an hour and building the wrong thing costs a year."),
 "validate": ("You are past the idea and into <em>finding out</em>.",
   "This is the stage most people skip, and skipping it is the single most expensive decision in the whole thing. You are trying to establish whether anyone will pay, not whether they like it. Liking it is free."),
 "early": ("You have proof. Now it is about <em>repeating it</em>.",
   "A few people paying is the hardest evidence there is, and it is also the point where the question changes: it stops being whether this works and becomes whether it works again, predictably, without you doing everything by hand each time."),
 "running": ("It works. The question is what it <em>rests on</em>.",
   "A business that runs is usually held together by a set of things only you know how to do. Making it bigger and making it steadier are the same job at this point, and both start with finding out which of those things would fall over first."),
}
ADJUST = {
 "alone": "One answer stands out: you said you talk to nobody about this. That is the most common reason people stop, and it almost never announces itself as the reason.",
 "kind": "You said the people you talk to are kind about it. Kindness and useful feedback are different things, and the second one usually has to come from somewhere else.",
 "money": "Money being the thing on your mind is worth taking at face value. It is the one area where a wrong assumption stays invisible until it is expensive.",
 "order": "Too much to do with no order to it is a structure problem rather than an effort problem, and no amount of working harder fixes it.",
 "erratic": "The wildly varying week is worth naming as its own problem. Irregular attention is much less effective than a smaller amount of regular attention.",
}
CARDS = {
 "direction": ("business-structures.html", "Business structures compared", "Sole proprietor, LLC and S corp on what actually differs, so the shape question stops being a fog."),
 "customers": ("outreach-email.html", "Outreach email generator", "The reason cold outreach fails is that it could have been sent to anyone. Six questions fixes that."),
 "money":     ("breakeven-calculator.html", "Breakeven calculator", "Fixed costs divided by what each sale contributes. The number you cannot plan without."),
 "order":     ("90-day-goals.html", "90-day goals worksheet", "Reflect, pick three priorities, build the weekly rhythm. Three, not ten."),
 "decide":    ("startup-checklist.html", "Startup checklist", "Five phases ordered by risk. Each one exists to stop you spending on the next too early."),
 "sales":     ("hourly-rate-calculator.html", "Hourly rate calculator", "What to charge, worked back from the income you want and the hours you can actually bill."),
 "setup":     ("state-filing.html", "State filing lookup", "What you file in your state, what it costs, and the annual report nobody warns you about."),
 "systems":   ("weekly-check-in.html", "Weekly check-in", "Fifteen minutes a week so the same things stop falling over without anyone noticing."),
 "alone":     ("support-system-checklist.html", "Support system checklist", "Five kinds of support and fifteen honest questions about which ones you actually have."),
 "kind":      ("support-system-checklist.html", "Support system checklist", "Audit who is in your corner, and where honest feedback would have to come from."),
 "sidehours": ("blog/how-to-build-a-business-while-working-a-9-to-5/", "Building around a job", "How to build the other thing without walking away from the paycheque."),
 "erratic":   ("weekly-check-in.html", "Weekly check-in", "A small amount of regular attention beats a large amount of irregular attention."),
}
ALWAYS = ("library.html", "The resource library", "Sixty-three pieces, filterable by topic, on starting, funding, growing and staying with it.")

qs_html = []
for qi, (q, opts) in enumerate(QS):
    qs_html.append('<section class="dg-q%s" data-q="%d">' % (" on" if qi == 0 else "", qi))
    qs_html.append("<h2>%s</h2><div class=\"dg-opts\">" % e(q))
    for oi, (txt, tag) in enumerate(opts):
        qs_html.append('<button class="dg-o" data-tag="%s" type="button">%s</button>' % (e(tag), e(txt)))
    qs_html.append("</div>")
    if qi:
        qs_html.append('<button class="dg-back" type="button">&larr; Back</button>')
    qs_html.append("</section>")

BODY = ('<div class="dg">'
        '<div class="dg-prog"><span id="dg-step">Question 1 of %d</span>'
        '<span class="dg-bar"><i></i></span></div>' % len(QS)
        + "".join(qs_html) +
        '<section class="dg-res" id="dg-res"><h2 id="dg-h"></h2>'
        '<p class="dg-lede" id="dg-l"></p>'
        '<div class="dg-next" id="dg-n"></div>'
        '<button class="dg-again" type="button">Start again</button></section>'
        '<script id="dg-data" type="application/json">%s</script></div>'
        % json.dumps({"reads": READS, "adjust": ADJUST, "cards": CARDS, "always": ALWAYS},
                     ensure_ascii=False).replace("</", "<\\/"))

JS = r"""
  var root=document.querySelector('.dg'); if(!root) return;
  var D=JSON.parse(document.getElementById('dg-data').textContent);
  var qs=[].slice.call(root.querySelectorAll('.dg-q'));
  var res=document.getElementById('dg-res'), bar=root.querySelector('.dg-bar i'),
      step=document.getElementById('dg-step');
  var answers=[], at=0;
  function show(){
    qs.forEach(function(s,i){ s.classList.toggle('on', i===at && at<qs.length); });
    res.classList.toggle('on', at>=qs.length);
    bar.style.width=Math.round(Math.min(at,qs.length)/qs.length*100)+'%';
    step.textContent = at<qs.length ? ('Question '+(at+1)+' of '+qs.length) : 'Done';
    var live = at<qs.length ? qs[at] : res;
    var h=live.querySelector('h2'); if(h){ h.setAttribute('tabindex','-1'); h.focus({preventScroll:true}); }
  }
  function finish(){
    var read=D.reads[answers[0]]||D.reads.idea;
    document.getElementById('dg-h').innerHTML=read[0];
    var extra='';
    for(var i=1;i<answers.length;i++){ if(D.adjust[answers[i]]){ extra=' '+D.adjust[answers[i]]; break; } }
    document.getElementById('dg-l').innerHTML=read[1]+extra;
    var seen={}, out=[];
    answers.forEach(function(t){ var c=D.cards[t]; if(c&&!seen[c[0]]){ seen[c[0]]=1; out.push(c); } });
    if(!seen[D.always[0]]) out.push(D.always);
    document.getElementById('dg-n').innerHTML=out.slice(0,4).map(function(c){
      return '<a class="dg-card" href="'+c[0]+'"><b>'+c[1]+'</b><span>'+c[2]+'</span></a>'; }).join('');
    show();
  }
  root.addEventListener('click',function(ev){
    var o=ev.target.closest('.dg-o');
    if(o){ answers[at]=o.getAttribute('data-tag'); at++; if(at>=qs.length) finish(); else show(); return; }
    if(ev.target.closest('.dg-back')){ if(at>0){ at--; answers.length=at; show(); } return; }
    if(ev.target.closest('.dg-again')){ answers=[]; at=0; show(); return; }
  });
  show();
"""

n = page("founder-diagnostic.html",
 "Founder Diagnostic: Where Are You Actually? | SideKix",
 "Five questions and a straight read on where your business actually is, plus the things on this site that fit that stage. No score, no email, nothing stored.",
 "Diagnostic",
 "Where <em>are</em> you, actually?",
 "Five questions. At the end you get a read on the stage you are at and what tends to matter there, plus the handful of things on this site that fit. No score out of ten, because five questions do not earn that kind of precision.",
 BODY, css=CSS, js=JS,
 schema=(webapp("Founder Diagnostic","founder-diagnostic.html",
   "Five questions returning a read on the stage a business is at and what fits it.",
   ["Five questions","A read on your stage","Matched resources","Nothing stored"]),
  faqpage([("What does this diagnostic actually do?",
    "It reads five answers and names the stage you are describing, then points at the things on this site that tend to matter at that stage. It does not score you, because five questions cannot support a number."),
   ("Is anything saved or sent?",
    "No. The questions and the result are assembled in your browser and nothing leaves the page. There is no account and no email step.")]),
  crumbs("Founder diagnostic","founder-diagnostic.html")))
print("founder-diagnostic.html %.0f KB" % (n/1024))
