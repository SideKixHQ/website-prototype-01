import os
import sys, json, html; sys.path.insert(0,'/home/claude/build')
from shell import page


SITE="https://sidekixhq.com"
DESC=("About 5,000 business ideas are buried in the US every day. The data behind that number, "
      "and the free federal help most people never use.")
def e(s): return html.escape(s,quote=True)

# ---- resources. every URL below was confirmed against a live search result ----
TYPES=[("Advice","#84D0C6"),("Registration","#F0855A"),("Money","#FFE7A6"),
       ("Data","#B18BE4"),("North Carolina","#4FC3F7")]
R=[
# --- Advice: the four SBA partner types, each at its own verified anchor ---
("Get local assistance","Advice","https://www.sba.gov/local-assistance",
 "Enter a ZIP code and the SBA returns the funded advisors nearest you.",
 "No cost","Anyone in the US","The single best starting point. It covers every partner type below in one search."),
("Small Business Development Centers","Advice","https://www.sba.gov/counseling/local-assistance/resource-partners/#sbdcs",
 "One-to-one advising and training, usually hosted at a university.",
 "No cost advising, low-cost training","Anyone",
 "SBDC advisors go deeper on financials, planning and access to capital than a general mentor."),
("SCORE business mentors","Advice","https://www.sba.gov/counseling/local-assistance/resource-partners/#score-business-mentoring",
 "The largest network of volunteer business mentors in the country.",
 "No cost","Anyone, any stage",
 "Mentoring is ongoing rather than one-off, by email, phone or video. They also run workshops and webinars."),
("Veterans Business Outreach Centers","Advice","https://www.sba.gov/counseling/local-assistance/resource-partners/#veterans-business-outreach-centers",
 "Training, counseling and one-to-one support for veterans, service members and military spouses.",
 "No cost","Veterans, National Guard and Reserve, military spouses and family",
 "31 centers nationally. They also run Boots to Business classes on and off base."),
("Women's Business Centers","Advice","https://www.sba.gov/counseling/local-assistance/resource-partners/#womens-centers",
 "A national network of centers focused on women starting and growing businesses.",
 "Little to no cost","Women starting or growing a business",
 "Counseling and training, plus routes into federal contracting and capital."),
("Boots to Business","Advice","https://sba.my.site.com/s/",
 "The SBA entrepreneurship course delivered through the military transition program.",
 "No cost","Service members, veterans and spouses",
 "There is also a Reboot version for veterans of any era, held off installation."),
("Plan your business","Advice","https://www.sba.gov/counseling/plan-your-business/",
 "The SBA's own walkthrough of market research, business plans and funding.",
 "No cost","Anyone at the idea stage",
 "Includes a business plan structure you can work through before paying anyone."),
("Browse by SBA district","Advice","https://www.sba.gov/local-assistance/district",
 "Pick your district office and filter by the kind of partner you want.",
 "No cost","Anyone",
 "Use this when the ZIP search returns too much and you want to narrow by type."),

# --- Money: real funding routes, all on sba.gov ---
("SBA 7(a) loans","Money","https://www.sba.gov/loans/7a-loans/",
 "The SBA's primary loan program, issued by lenders and partly guaranteed by the agency.",
 "Loan, terms vary","Businesses that can service debt",
 "The guarantee is what makes a lender say yes when they otherwise would not."),
("SBA microloans","Money","https://www.sba.gov/loans/microloans/",
 "Smaller loans through community-based intermediary lenders.",
 "Loan, smaller amounts","Newer and very small businesses",
 "Often the realistic option when a bank will not look at you yet."),
("Lender Match","Money","https://www.sba.gov/loans/lender-match/",
 "Describe what you need and the SBA connects you to participating lenders.",
 "No cost to use","Anyone seeking financing",
 "A referral tool, not an application. You still apply with the lender directly."),
("SBA 504 loans","Money","https://www.sba.gov/loans/504-loans/",
 "Long-term, fixed-rate financing for major fixed assets like buildings and equipment.",
 "Loan","Businesses buying property or heavy equipment",
 "Not for working capital or inventory. Read the eligible-use list first."),
("Grants","Money","https://www.sba.gov/loans/additional-funding-opportunities/grants/",
 "What federal grants actually exist, and who they are for.",
 "No cost to read","Anyone curious about grant funding",
 "Worth reading before you chase grants. Most small businesses do not qualify for federal ones."),
("Federal certifications","Money","https://www.sba.gov/certifications/",
 "Women-owned, veteran-owned, HUBZone and 8(a) programs for federal contracting.",
 "No cost to apply","Businesses that qualify by ownership or location",
 "Certification opens set-aside contracts. It takes paperwork but costs nothing to apply."),

# --- Registration ---
("Get an EIN","Registration","https://www.irs.gov/businesses/small-businesses-self-employed/get-an-employer-identification-number",
 "Your federal tax ID, issued by the IRS online in minutes.",
 "No cost, ever","Anyone forming a business entity",
 "The IRS says plainly you never pay for an EIN. Sites that charge are reselling a government service."),
("What an EIN is","Registration","https://www.irs.gov/businesses/employer-identification-number",
 "Who needs one, when you need a new one, what to do if you lose it.",
 "No cost","Anyone",
 "Read before applying so you answer the responsible party question correctly."),
("Form SS-4","Registration","https://www.irs.gov/forms-pubs/about-form-ss-4",
 "The paper route to an EIN, for anyone who cannot apply online.",
 "No cost","International applicants and anyone without online access",
 "Also useful just to see the questions before you start the online form."),
("Register a business in NC","Registration","https://www.sosnc.gov/divisions/business_registration",
 "File articles of organization or incorporation with the NC Secretary of State.",
 "State filing fee applies","North Carolina businesses",
 "Sole proprietors and general partnerships usually file with the county Register of Deeds instead."),
("Check an NC business name","Registration","https://www.sosnc.gov/online_services/search/by_title/search_Business_Registration",
 "Search existing NC registrations before you commit to a name.",
 "No cost","Anyone naming a business in NC",
 "Do this before printing anything. Name conflicts are cheap to avoid and expensive to fix."),

# --- North Carolina ---
("Start My Business, nc.gov","North Carolina","https://www.nc.gov/working/business-nc/start-my-business",
 "The state's own walkthrough of structure, licenses and taxes.",
 "No cost","North Carolina",
 "North Carolina has no single general business license, so requirements depend on what you do."),
("EDPNC Small Business Advisors","North Carolina","https://edpnc.com/start-or-grow-a-business/start-a-business/",
 "North Carolina's business advisors, reachable on 1-800-228-8443.",
 "No cost","North Carolina",
 "Particularly useful for the license and permit question, where most people get stuck."),
("NC SBTDC","North Carolina","https://sbtdc.org/",
 "The state's Small Business and Technology Development Center network.",
 "No cost counseling","North Carolina",
 "University-hosted, with offices across the state."),
("VBOC at Fayetteville State University","North Carolina","https://www.fsuvboc.com/",
 "The Veterans Business Outreach Center covering North Carolina, on 910-672-2683.",
 "No cost","Veterans and military families in NC",
 "One of 31 VBOCs nationally, and the one assigned to this state."),

# --- Data ---
("Business Formation Statistics","Data","https://www.census.gov/econ/bfs/index.html",
 "The monthly count of new business applications, national and by state.",
 "No cost, public domain","Anyone",
 "Updated monthly. The closest thing to a live read on how many people are starting."),
("Business Employment Dynamics","Data","https://www.bls.gov/bdm/",
 "Openings, closings and survival rates for establishments, from the BLS.",
 "No cost, public domain","Anyone",
 "The actual source behind most survival statistics you see quoted secondhand."),
("State small business statistics","Data","https://data.sba.gov/en/dataset/state-small-business-statistics-2025",
 "The SBA's state-by-state dataset, downloadable.",
 "No cost, public domain","Anyone",
 "Counts, employment share and ownership demographics for every state."),
("North Carolina state profile","Data","https://advocacy.sba.gov/wp-content/uploads/2025/06/North_Carolina_2025-State-Profile.pdf",
 "The full SBA profile for North Carolina, as a PDF.",
 "No cost, public domain","North Carolina",
 "Where the North Carolina figures further down this page come from."),
("Nonemployer Statistics","Data","https://www.census.gov/programs-surveys/nonemployer-statistics.html",
 "Census data on businesses with no employees, which is most businesses.",
 "No cost, public domain","Anyone",
 "If you are a solo operator, this is the dataset you actually belong to."),
("Statistics of US Businesses","Data","https://www.census.gov/programs-surveys/susb.html",
 "Employer business counts by size, industry and geography.",
 "No cost, public domain","Anyone",
 "Use it to size a market by number of firms rather than guessing."),
]
COLOR={t:c for t,c in TYPES}

cards=[]
for i,(name,typ,url,blurb,cost,who,note) in enumerate(R):
    rid=f"r{i}"
    cards.append(
      f'<article class="rcard" data-type="{typ}" data-name="{e(name.lower())} {e(blurb.lower())}">'
      f'<div class="rtop"><span class="rtype">{typ}</span>'
      f'<h3><a href="{url}" target="_blank" rel="noopener">{e(name)}</a></h3></div>'
      f'<p class="rblurb">{e(blurb)}</p>'
      f'<button class="rmore" type="button" aria-expanded="false" aria-controls="{rid}">Details</button>'
      f'<div class="rdet" id="{rid}" hidden>'
      f'<dl><dt>Cost</dt><dd>{e(cost)}</dd>'
      f'<dt>Who it is for</dt><dd>{e(who)}</dd>'
      f'<dt>Worth knowing</dt><dd>{e(note)}</dd></dl>'
      f'<a class="rgo" href="{url}" target="_blank" rel="noopener">Open {e(name)} &rarr;</a></div>'
      f'</article>')

pills=('<button class="rfilt" data-type="all" aria-pressed="true">Everything</button>'
       + "".join(f'<button class="rfilt" data-type="{t}" aria-pressed="false">{t}</button>' for t,_ in TYPES))

# ---- figures ----
def stat(num,lab,note=""):
    return (f'<div class="mstat"><span class="mnum">{num}</span><span class="mlab">{lab}</span>'
            + (f'<span class="mnote">{note}</span>' if note else '') + '</div>')
US="".join([stat("36.2 million","small businesses","99.9% of all US businesses"),
  stat("78%","of all US businesses have no employees at all","30,427,808 of them in 2023, turning over nearly $1.8 trillion"),
  stat("9 in 10","net new jobs came from small businesses","March 2023 to March 2024"),
  stat("1.1 million","new establishments opened","a net increase of 1.2 million jobs")])
NC="".join([stat("1.1 million","small businesses in North Carolina","99.6% of businesses in the state"),
  stat("1.8 million","people they employ","44.2% of everyone working in NC"),
  stat("+8,068","net new establishments","38,748 opened, 30,680 closed, March 2023 to March 2024"),
  stat("89.9%","of NC net new jobs came from small businesses","a net increase of 52,820 jobs")])
APPS="".join([stat("496,443","applications, February 2026","seasonally adjusted, down 5.8% on January"),
  stat("28,994","formations projected from that month","expected to start payroll within four quarters"),
  stat("29,741","projected, June 2026","up 0.7% on the month before")])

CSS = """
/* an author display rule outranks the browser rule for [hidden], so say it explicitly */
.mkt [hidden]{display:none !important}
/* the theme veil greyscales everything, which ruins a page built on colour */
#kx-desat{display:none !important}
.mkt .mbackrow{display:flex;justify-content:center;margin:0 0 22px}
.mkt .mback{display:inline-flex;align-items:center;gap:8px;min-height:44px;text-decoration:none;
  font-family:var(--util);font-size:10.5px;letter-spacing:.18em;text-transform:uppercase;
  color:var(--grey);transition:color .25s}
.mkt .mback:hover{color:var(--gold-pale)}
.mkt .mback svg{width:15px;height:15px;fill:none;stroke:currentColor;stroke-width:2;
  stroke-linecap:round;stroke-linejoin:round}
.mkt .sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;
  clip:rect(0 0 0 0);white-space:nowrap;border:0}

/* ---- the directory ---- */
/* the shortlist tray */


/* the eyebrow is two jumps, and it should look like it */
.mkt .eyenav{display:flex;justify-content:center;margin:0 0 18px}
.mkt .eyego{display:inline-flex;align-items:center;min-height:44px;padding:0 14px;border-radius:999px;
  text-decoration:none;font:inherit;letter-spacing:.2em;text-transform:uppercase;
  color:var(--gold-pale);border:1px solid rgba(212,168,86,.42);
  background:rgba(212,168,86,.07);
  transition:background .3s,border-color .3s,color .3s}
.mkt .eyego::after{content:"↓";margin-left:9px;font-size:11px;opacity:.75;line-height:1}
.mkt .eyego:hover{background:var(--gold);border-color:var(--gold);color:#1a1400;font-weight:700}
.mkt .eyego:focus-visible{outline:3px solid var(--gold-pale);outline-offset:3px}
@media(max-width:420px){
  .mkt .eyenav{flex-wrap:wrap}
  .mkt .eyego{padding:0 12px;letter-spacing:.14em}
}

/* the jump targets must clear the fixed header */
.mkt .rsearch{scroll-margin-top:104px}
.mkt .msec{scroll-margin-top:104px}
@media(max-width:760px){
  .mkt .rsearch,.mkt .msec{scroll-margin-top:84px}
}

/* scroll effects. every rule is gated behind .fx, which only javascript adds,
   so if the script never runs the numbers are simply there. */
.mkt.fx .unum{opacity:0}
.mkt.fx .unum.rolling,.mkt.fx .unum.done{opacity:1}
.mkt.fx .unum.rolling{color:var(--gold-mid)}
.mkt.fx .unum.done{color:#F3E4A8;transition:color .5s ease}

.mkt.fx .mstat .mnum{opacity:0;transform:rotateX(-78deg) translateY(10px);
  transform-origin:50% 90%;backface-visibility:hidden}
.mkt.fx .mstat.flip .mnum{opacity:1;transform:none;
  transition:opacity .5s ease,transform .7s cubic-bezier(.2,.9,.25,1)}
.mkt.fx .mstats{perspective:900px}

.mkt.fx .oddspct{opacity:0}
.mkt.fx .oddspct.counting,.mkt.fx .oddspct.done{opacity:1}

@media(prefers-reduced-motion:reduce){
  .mkt.fx .unum,.mkt.fx .oddspct{opacity:1}
  .mkt.fx .mstat .mnum{opacity:1;transform:none}
}

/* a reading rail: ambient, nothing hides, nothing to get stuck in */
.mkt .kxrail{position:fixed;left:clamp(14px,2.2vw,30px);top:50%;transform:translateY(-50%);
  z-index:56;pointer-events:none}
.mkt .kxrail ul{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:30px}
.mkt .kxrail li{display:flex}
.mkt .kxrail a{pointer-events:auto;display:flex;align-items:center;gap:12px;
  min-height:26px;text-decoration:none;color:var(--grey-dim)}
.mkt .kxrail i{flex:0 0 auto;width:9px;height:9px;border-radius:99px;
  background:#221f19;border:1px solid #2e2a22;
  transition:background .35s ease,border-color .35s ease,transform .35s ease,box-shadow .35s ease}
.mkt .kxrail span{font-family:var(--util);font-size:11px;letter-spacing:.12em;text-transform:uppercase;
  white-space:nowrap;color:#FFF8E8;
  padding:8px 13px;border-radius:999px;
  background:rgba(9,8,6,.96);border:1px solid rgba(212,168,86,.45);
  -webkit-backdrop-filter:blur(6px);backdrop-filter:blur(6px);
  box-shadow:0 6px 22px rgba(0,0,0,.6);
  opacity:0;transform:translateX(-10px) scale(.9);transform-origin:left center;
  pointer-events:none;
  transition:opacity .25s ease,transform .3s cubic-bezier(.2,.8,.2,1)}
.mkt .kxrail a:hover span,.mkt .kxrail a:focus-visible span{opacity:1;transform:none}
.mkt .kxrail a:focus-visible{outline:3px solid var(--gold-pale);outline-offset:4px;border-radius:6px}
.mkt .kxrail a:hover i{border-color:var(--gold)}
.mkt .kxrail a.here i{background:var(--gold);border-color:var(--gold);transform:scale(1.35);
  box-shadow:0 0 10px rgba(212,168,86,.55)}

.mkt .kxtrack{position:absolute;left:4px;top:-14px;bottom:-14px;width:1px;
  background:rgba(212,168,86,.16);overflow:hidden}
.mkt .kxfill{position:absolute;left:0;top:0;width:1px;height:0;
  background:linear-gradient(180deg,var(--gold),rgba(212,168,86,.25));transition:height .25s linear}
/* it needs room, and it earns none on a narrow screen */
@media(min-width:1180px){ .mkt{padding-left:0} }
@media(max-width:1179px){ .mkt .kxrail{display:none} }
@media(prefers-reduced-motion:reduce){
  .mkt .kxrail i,.mkt .kxrail span,.mkt .kxfill{transition:none}
}

/* the questions this page answers */
.mkt .pfaq{margin:88px 0 0}
.mkt .pfaq h2{font-family:var(--display);font-weight:600;font-size:clamp(24px,3.2vw,34px);
  line-height:1.12;color:#FFF8E8;margin:0 0 8px;text-align:left;padding-bottom:12px;
  border-bottom:1px solid rgba(205,170,99,.28)}
.mkt .pfaq details{border-bottom:1px solid rgba(212,168,86,.14)}
.mkt .pfaq summary{cursor:pointer;list-style:none;padding:20px 0;font-family:var(--body);
  font-weight:600;font-size:16.5px;line-height:1.45;color:#FFF8E8;
  display:flex;align-items:flex-start;gap:14px}
.mkt .pfaq summary::-webkit-details-marker{display:none}
.mkt .pfaq summary::before{content:"+";flex:0 0 auto;font-family:var(--util);font-size:16px;
  color:var(--gold-mid);line-height:1.35}
.mkt .pfaq details[open] summary::before{content:"\2212"}
.mkt .pfaq summary:hover{color:var(--gold-pale)}
.mkt .pfaq summary:focus-visible{outline:3px solid var(--gold-pale);outline-offset:3px}
.mkt .pfaq .pa{padding:0 0 20px 30px}
.mkt .pfaq .pa p{margin:0;font-size:15.5px;line-height:1.7;color:#B9B4AB;max-width:70ch}
@media(max-width:640px){.mkt .pfaq{margin-top:56px}.mkt .pfaq .pa{padding-left:0}}

.mkt .msec{margin:96px auto 0;text-align:left}
.mkt .msec h2{font-family:var(--display);font-weight:600;font-size:clamp(24px,3.2vw,34px);
  line-height:1.12;color:#FFF8E8;margin:0 0 8px;text-align:left;padding-bottom:12px;
  border-bottom:1px solid color-mix(in srgb,var(--c,#D4A856) 34%,transparent)}
.mkt .mbody{padding-top:0}
@media(max-width:760px){.mkt .msec{margin-top:64px}}

/* the number nobody states */
.mkt .unbuilt{margin:0 0 44px}
.mkt .unum{display:block;font-family:var(--display);font-weight:600;line-height:.92;
  font-size:clamp(56px,10vw,132px);color:#F3E4A8;letter-spacing:-.02em}
.mkt .ulab{display:block;margin-top:14px;font-size:clamp(18px,2.2vw,24px);line-height:1.35;
  color:#FFF8E8;font-weight:600}
.mkt .usub{display:block;margin-top:12px;font-size:17px;line-height:1.55;color:#B9B4AB;max-width:52ch}


/* the potential, in K marks */
.mkt .pot{margin:0}
.mkt .kgrid{display:grid;grid-template-columns:repeat(25,1fr);gap:5px;max-width:660px;margin:0 0 26px}
/* the unlit dots were #1f1c16, which is 1.2:1 against the page. 290 of the
   300 were effectively invisible, so the block read as ten floating marks
   rather than a field of 300 with ten lit. #665c4c clears 3:1 against the
   background, and the lit gold moves to #E8C97A to keep a 4.1:1 gap so the
   lit ones still clearly stand out. */
.mkt .kdot{aspect-ratio:1;min-height:9px;background:#665c4c;
  -webkit-mask:url("data:image/png;base64,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") center/contain no-repeat;
  mask:url("data:image/png;base64,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") center/contain no-repeat;
  transition:background .45s ease,filter .45s ease,transform .45s ease}
/* a mask that fails to load hides the element completely, which is how 300
   dots became an empty gap. the shape is now inlined so it cannot 404, and
   this block only applies the mask where the browser confirms support, so an
   unsupported engine shows rounded squares rather than nothing. */
.mkt .kdot{border-radius:3px}
@supports not ((-webkit-mask-image: url("")) or (mask-image: url(""))){
  .mkt .kdot{-webkit-mask:none;mask:none;border-radius:3px}
}
.mkt .kdot.on{background:linear-gradient(160deg,#F3E4A8,#E8C97A);
  filter:drop-shadow(0 0 4px rgba(161,133,62,.5))}
.mkt .kdot.new{background:linear-gradient(160deg,#FFF3CC,#F3E4A8 45%,#D4A856);
  filter:drop-shadow(0 0 12px rgba(243,228,168,.9));transform:scale(1.18)}
.mkt .klegend{display:flex;flex-wrap:wrap;gap:8px 22px;margin:0 0 12px}
.mkt .kl{display:inline-flex;align-items:center;gap:8px;font-family:var(--util);font-size:10px;
  letter-spacing:.16em;text-transform:uppercase;color:#8a8378}
.mkt .kl[hidden]{display:none}
.mkt .kl i{width:10px;height:10px;border-radius:2px}
.mkt .kl.now{color:#C9A761} .mkt .kl.now i{background:linear-gradient(160deg,#C9A761,#A1853E)}
.mkt .kl.add{color:#F3E4A8} .mkt .kl.add i{background:linear-gradient(160deg,#FFF3CC,#F3E4A8 45%,#D4A856);
  box-shadow:0 0 9px rgba(243,228,168,.8)}
.mkt .kl.off i{background:#1f1c16;border:1px solid #2a2724}
.mkt .potyrs{display:flex;flex-wrap:wrap;gap:8px}
.mkt .potyr{flex:0 0 auto;cursor:pointer;min-height:48px;padding:0 22px;border-radius:999px;
  border:1px solid rgba(212,168,86,.4);background:none;color:var(--gold-pale);
  font-family:var(--body);font-weight:600;font-size:15px;
  transition:background .3s,border-color .3s,color .3s}
.mkt .potyr:hover{background:rgba(212,168,86,.14);border-color:var(--gold)}
.mkt .potyr:focus-visible{outline:3px solid var(--gold-pale);outline-offset:3px}
.mkt .potyr[aria-pressed="true"]{background:var(--gold);border-color:var(--gold);color:#1a1400;font-weight:700}
.mkt .potout{display:flex;flex-wrap:wrap;gap:18px 56px;margin:30px 0 14px}
.mkt .gcol{display:flex;flex-direction:column}
.mkt .gcol[hidden]{display:none}
.mkt .gnum{font-family:var(--display);font-weight:600;line-height:1;
  font-size:clamp(34px,5vw,58px);color:#F3E4A8;letter-spacing:-.01em}
.mkt .gplus .gnum{color:var(--gold)}
.mkt .glab{margin-top:8px;font-size:15px;line-height:1.45;color:#B9B4AB;max-width:34ch}
.mkt .potfoot{margin:0;font-family:var(--util);font-size:10.5px;letter-spacing:.18em;
  text-transform:uppercase;color:#8a8378}
.mkt .closer{margin:48px 0 0;font-family:var(--display);font-style:italic;font-weight:600;
  font-size:clamp(22px,2.8vw,32px);line-height:1.25;color:var(--gold-mid);text-align:left}
@media(max-width:640px){
  .mkt .kgrid{grid-template-columns:repeat(15,1fr);gap:6px}
  .mkt .potout{gap:16px 32px}
  .mkt .unbuilt{margin-bottom:34px}
}

/* the odds: a hundred dots, and the number that matters */
.mkt .oddsbtns{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 40px}
.mkt .oddb{flex:0 0 auto;cursor:pointer;min-height:44px;padding:0 18px;border-radius:999px;
  border:1px solid rgba(212,168,86,.32);background:none;color:#B9B4AB;font-family:var(--util);
  font-size:10.5px;letter-spacing:.16em;text-transform:uppercase;
  transition:background .3s,color .3s,border-color .3s}
.mkt .oddb:hover{border-color:var(--gold);color:#F3E4A8}
.mkt .oddb[aria-pressed="true"]{background:#F0855A;border-color:#F0855A;color:#0b0b0c;font-weight:700}
.mkt .oddb:focus-visible{outline:3px solid var(--gold-pale);outline-offset:3px}
.mkt .odds{display:grid;grid-template-columns:448px minmax(0,1fr);
  gap:clamp(30px,3.4vw,48px);align-items:center;justify-content:start}
.mkt .dots{display:grid;grid-template-columns:repeat(20,1fr);gap:6px;width:448px}
.mkt .dot{aspect-ratio:1;min-height:14px;border-radius:99px;background:#1c1a16;border:1px solid #262320;
  transition:background .45s ease,border-color .45s ease,box-shadow .45s ease}
.mkt .dot.lit{background:#F0855A;border-color:#F0855A;box-shadow:0 0 8px rgba(240,133,90,.45)}
.mkt .oddsfig{display:block}
.mkt .oddspct{display:block;font-family:var(--display);font-weight:600;line-height:.92;
  font-size:clamp(64px,9vw,124px);color:#F0855A;letter-spacing:-.02em}
.mkt .oddslab{display:block;margin-top:16px;font-size:19px;line-height:1.4;color:#FFF8E8;font-weight:600}
.mkt .oddssub{display:block;margin-top:9px;font-size:15px;line-height:1.6;color:#B9B4AB}
/* it does not have to be that way. affects nothing but itself. */
.mkt .turn{margin:64px 0 0;padding:30px 32px;border-radius:16px;
  border:1px solid rgba(212,168,86,.32);
  background:linear-gradient(180deg,rgba(212,168,86,.07),rgba(8,8,9,.6))}
.mkt .turn h3{display:block;margin:0;font-family:var(--display);font-weight:600;
  font-size:clamp(32px,5.4vw,60px);line-height:1.04;letter-spacing:-.02em;color:#FFF8E8;
  text-align:left;opacity:0;transform:translateY(26px);
  transition:opacity .8s ease,transform .9s cubic-bezier(.2,.8,.2,1)}
.mkt .turn.lit h3{opacity:1;transform:none}
.mkt .turnp{margin:20px 0 22px;font-size:16px;line-height:1.65;color:#CFC9BE;max-width:70ch}
.mkt .turnbits{display:flex;flex-wrap:wrap;gap:8px;list-style:none;margin:0;padding:0}
.mkt .turnbits li{font-family:var(--body);font-weight:600;font-size:15px;color:#F3E4A8;
  border:1px solid rgba(212,168,86,.34);border-radius:999px;padding:9px 16px;
  background:rgba(212,168,86,.06)}
.mkt .turnlink{display:inline-flex;align-items:center;min-height:44px;margin:20px 0 0;
  font-family:var(--util);font-size:10.5px;letter-spacing:.16em;text-transform:uppercase;
  color:var(--gold-pale);text-decoration:none;border-bottom:1px solid rgba(212,168,86,.45)}
.mkt .turnlink:hover{color:#FFF8E8;border-bottom-color:var(--gold)}
@media(prefers-reduced-motion:reduce){
  .mkt .turn h3{opacity:1;transform:none;transition:none}
}
@media(max-width:640px){.mkt .turn{padding:22px 20px}}
.mkt .oddscaveat{max-width:62ch;margin:40px 0 0;font-size:15px;line-height:1.65;color:#B9B4AB}
@media(max-width:860px){
  .mkt .odds{grid-template-columns:1fr;gap:26px;justify-content:stretch}
  .mkt .dots{width:100%}
  .mkt .oddsfig{order:-1;padding-top:0}
  .mkt .oddspct{font-size:clamp(56px,16vw,96px)}
  .mkt .oddslab{margin-top:12px}
}
@media(max-width:520px){.mkt .dots{grid-template-columns:repeat(10,1fr);gap:7px}}
@media(prefers-reduced-motion:reduce){.mkt .dot{transition:none}}

/* the homepage scale on desktop, but its 68px floor never scaled down, so on
   every phone the heading was locked at 68px and a long one ran off screen. */
/* this was matched to the homepage hero, which is wrong for a content page.
   resources, glossary and tools all sit at 45px; this was rendering at 78px
   on the shortest heading on the site, two words filling two thirds of the
   container. brought in line with its siblings. */
.mkt .rhead{font-family:var(--display);font-weight:600;
  font-size:clamp(32px,5.2vw,56px);
  line-height:1.02;letter-spacing:-.012em;color:#FFF8E8;text-align:center;
  margin:0 0 40px;
  overflow-wrap:break-word;word-break:break-word;hyphens:auto;
  max-width:100%;padding:0 4px;box-sizing:border-box}
@media(min-width:820px){
  .mkt .rhead{font-size:clamp(40px,4.4vw,56px);line-height:1.02}
}
.mkt .rsearch{max-width:min(520px,100%);margin:0 auto 24px}
.mkt .rsearch input{width:100%;min-height:48px;padding:0 20px;border-radius:999px;
  border:1px solid rgba(212,168,86,.32);background:linear-gradient(180deg,#0d0b06,#070706);
  color:#FFF8E8;font-family:var(--body);font-size:16px;transition:border-color .3s}
.mkt .rsearch input::placeholder{color:#8a8378}
.mkt .rsearch input:focus{outline:3px solid var(--gold-pale);outline-offset:3px;border-color:var(--gold)}
.mkt .rfilters{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin:0 auto;
  max-width:min(860px,100%)}
.mkt .rfilt{flex:0 0 auto;font-family:var(--util);font-size:10.5px;letter-spacing:.16em;
  text-transform:uppercase;cursor:pointer;background:none;border:1px solid rgba(212,168,86,.32);
  color:#B9B4AB;border-radius:999px;padding:0 16px;min-height:44px;
  transition:background .3s,color .3s,border-color .3s}
.mkt .rfilt:hover{border-color:var(--gold);color:#F3E4A8}
.mkt .rfilt[aria-pressed="true"]{background:var(--gold);border-color:var(--gold);color:#1a1400;font-weight:700;
  box-shadow:0 6px 22px color-mix(in srgb,var(--c,#D4A856) 30%,transparent)}
.mkt .rfilt:focus-visible{outline:3px solid var(--gold-pale);outline-offset:3px}
.mkt .rfilt .n{font-size:9px;opacity:.65;margin-left:7px;letter-spacing:.08em}
.mkt .rcount{text-align:center;font-family:var(--util);font-size:10.5px;letter-spacing:.2em;
  text-transform:uppercase;color:var(--grey-dim);margin:24px 0 0;min-height:14px}
.mkt .rgrid{scroll-margin-top:104px;display:grid;
  grid-template-columns:repeat(auto-fill,minmax(min(320px,100%),1fr));gap:20px;
  max-width:1180px;margin:28px auto 0}
.mkt .rcard{border:1px solid rgba(205,170,99,.35);border-radius:11px;padding:18px;
  background:linear-gradient(180deg,#0d0b06,#070706);transition:border-color .3s,transform .3s}
.mkt .rcard:hover{border-color:color-mix(in srgb,var(--c,#D4A856) 55%,transparent);transform:translateY(-2px)}
.mkt .rcard[hidden]{display:none}
.mkt .rtype{display:inline-block;font-family:var(--util);font-size:9px;letter-spacing:.18em;
  text-transform:uppercase;color:var(--c,#C9A761);
  background:color-mix(in srgb,var(--c,#D4A856) 14%,#0b0b0c);
  border:1px solid color-mix(in srgb,var(--c,#D4A856) 34%,transparent);
  border-radius:6px;padding:5px 9px;margin-bottom:10px}
.mkt .rtop{display:block}
.mkt .rcard h3{font-family:var(--body);font-size:17px;font-weight:600;line-height:1.32;
  margin:0 0 7px;text-align:left}
.mkt .rcard h3 a{color:#FFF8E8;text-decoration:none;border-bottom:1px solid transparent}
.mkt .rcard h3 a:hover{border-bottom-color:var(--c,var(--gold))}
.mkt .rblurb{margin:0 0 12px;font-size:14.5px;line-height:1.6;color:#B9B4AB}
.mkt .rmore{cursor:pointer;background:none;border:1px solid rgba(212,168,86,.32);color:var(--grey);
  font-family:var(--util);font-size:9.5px;letter-spacing:.16em;text-transform:uppercase;
  border-radius:999px;padding:0 14px;min-height:36px;transition:color .3s,border-color .3s}
.mkt .rmore:hover{color:#F3E4A8;border-color:var(--gold)}
.mkt .rmore:focus-visible{outline:3px solid var(--gold-pale);outline-offset:2px}
.mkt .rmore[aria-expanded="true"]{color:#1a1400;background:var(--gold);border-color:var(--gold);font-weight:700}
.mkt .rdet{margin-top:14px;padding-top:14px;border-top:1px solid rgba(212,168,86,.18)}
.mkt .rdet dl{margin:0}
.mkt .rdet dt{font-family:var(--util);font-size:9.5px;letter-spacing:.16em;text-transform:uppercase;
  color:color-mix(in srgb,var(--c,#D4A856) 62%,#8a8378);margin-top:10px}
.mkt .rdet dt:first-child{margin-top:0}
.mkt .rdet dd{margin:3px 0 0;font-size:14.5px;line-height:1.58;color:#CFC9BE}
.mkt .rgo{display:inline-flex;align-items:center;min-height:44px;margin-top:14px;
  font-family:var(--util);font-size:10px;letter-spacing:.16em;text-transform:uppercase;
  color:var(--c,var(--gold-pale));text-decoration:none}
.mkt .rgo:hover{text-decoration:underline;text-underline-offset:4px}
.mkt .rnone{text-align:center;color:var(--grey);font-style:italic;padding:34px 0 0}

/* ---- figures ---- */
.mkt .msec{max-width:1180px;margin:96px auto 0;text-align:left}
.mkt .msec h2{font-family:var(--display);font-weight:600;font-size:clamp(24px,3.2vw,34px);
  line-height:1.12;color:#FFF8E8;margin:0 0 8px;text-align:left;padding-bottom:12px;
  border-bottom:1px solid color-mix(in srgb,var(--c,#D4A856) 34%,transparent)}
.mkt .mdek{font-size:16px;line-height:1.62;color:#B9B4AB;margin:16px 0 32px;max-width:62ch}
.mkt .mtabs{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 24px}
.mkt .mtab{flex:0 0 auto;cursor:pointer;background:none;border:1px solid rgba(212,168,86,.32);
  color:#B9B4AB;border-radius:999px;padding:0 18px;min-height:44px;font-family:var(--util);
  font-size:10.5px;letter-spacing:.16em;text-transform:uppercase;
  transition:background .3s,color .3s,border-color .3s}
.mkt .mtab:hover{border-color:var(--gold);color:#F3E4A8}
.mkt .mtab[aria-selected="true"]{background:var(--gold);border-color:var(--gold);color:#1a1400;font-weight:700}
.mkt .mtab[data-set="nc"]{color:#4FC3F7;border-color:color-mix(in srgb,#4FC3F7 40%,transparent)}
.mkt .mtab[data-set="nc"]:hover{border-color:#4FC3F7;background:color-mix(in srgb,#4FC3F7 12%,transparent)}
.mkt .mtab[data-set="nc"][aria-selected="true"]{background:#4FC3F7;border-color:#4FC3F7;color:#0b0b0c}
.mkt .msec[data-t="who"]:has(.mtab[data-set="nc"][aria-selected="true"]){--c:#4FC3F7}
.mkt .mtab:focus-visible{outline:3px solid var(--gold-pale);outline-offset:3px}
/* a single band across the full width, not four boxes in the middle */
.mkt .mstats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:0;
  border-top:1px solid rgba(205,170,99,.3);border-bottom:1px solid rgba(205,170,99,.3)}
.mkt .mstat{padding:20px 22px;border-left:1px solid rgba(205,170,99,.16)}
.mkt .mstat:first-child{border-left:none;padding-left:0}
.mkt .mnum{display:block;font-family:var(--display);font-weight:600;line-height:1.02;
  font-size:clamp(24px,2.5vw,32px);color:var(--c,#F3E4A8);margin-bottom:5px;word-break:break-word}
.mkt .mlab{display:block;font-size:14px;line-height:1.45;color:#FFF8E8;font-weight:600}
.mkt .mnote{display:block;margin-top:5px;font-size:12.5px;line-height:1.5;color:#B9B4AB}
@media(max-width:880px){
  .mkt .mstats{grid-template-columns:repeat(2,minmax(0,1fr))}
  .mkt .mstat{padding:18px 18px}
  .mkt .mstat:nth-child(odd){border-left:none;padding-left:0}
  .mkt .mstat:nth-child(n+3){border-top:1px solid rgba(205,170,99,.16)}
}
@media(max-width:520px){
  .mkt .mstats{grid-template-columns:1fr}
  .mkt .mstat{border-left:none;padding:16px 0}
  .mkt .mstat + .mstat{border-top:1px solid rgba(205,170,99,.16)}
}
.mkt .msrc{margin:32px 0 0;font-family:var(--util);font-size:11px;letter-spacing:.05em;color:#8a8378}
.mkt .msrc a{color:#B9B4AB;text-decoration:none;border-bottom:1px solid rgba(212,168,86,.4)}
.mkt .msrc a:hover{color:#F3E4A8;border-bottom-color:var(--gold)}
/* the credit belongs with the caveat above it, not floating below */
.mkt .msrc.tight{margin-top:12px}

.mkt .mhubs{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(260px,100%),1fr));gap:16px;
  max-width:900px;margin:96px auto 0}
.mkt .mhub{color:#E3DED2;border:1px solid rgba(212,168,86,.4);border-radius:16px;padding:26px;text-decoration:none;
  display:block;background:linear-gradient(180deg,rgba(26,20,8,.5),rgba(8,8,9,.7));
  transition:transform .3s,border-color .3s}
.mkt .mhub:hover{transform:translateY(-3px);border-color:var(--gold)}
.mkt .mhub b{display:block;font-family:var(--display);font-size:26px;color:#FFF8E8;margin-bottom:4px}
.mkt .mhub span{font-family:var(--util);font-size:10.5px;letter-spacing:.18em;text-transform:uppercase;
  color:var(--gold-mid)}
/* a footnote, not a section: full width, small type, two columns */
.mkt .mfoot{max-width:none;margin:96px 0 0;padding-top:20px;
  border-top:1px solid rgba(205,170,99,.3);
  display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:0 44px}
.mkt .mfoot h2{grid-column:1/-1;font-family:var(--util);font-weight:500;font-size:10.5px;
  letter-spacing:.2em;text-transform:uppercase;color:var(--gold-mid);margin:0 0 12px;text-align:left}
.mkt .mfoot p{font-size:13.5px;line-height:1.6;color:#8a8378;margin:0;text-align:left}
@media(max-width:760px){
  .mkt .mfoot{grid-template-columns:1fr;gap:10px;margin-top:42px}
}
@media(max-width:760px){
  .mkt .rgrid{scroll-margin-top:84px}
  .mkt .rcard{padding:16px}
  .mkt .msec{margin-top:40px}.mkt .mhub{padding:22px}.mkt .mhub b{font-size:22px}
  .mkt .rsearch input{min-height:52px;font-size:16px}
}
"""
for t,c in TYPES:
    CSS+=f'\n.mkt .rcard[data-type="{t}"]{{--c:{c}}}'
    CSS+=f'\n.mkt .rfilt[data-type="{t}"]{{--c:{c};color:{c};border-color:color-mix(in srgb,{c} 40%,transparent)}}'
    CSS+=f'\n.mkt .rfilt[data-type="{t}"]:hover{{border-color:{c};background:color-mix(in srgb,{c} 12%,transparent)}}'
    CSS+=f'\n.mkt .rfilt[data-type="{t}"][aria-pressed="true"]{{background:{c};border-color:{c};color:#0b0b0c}}'
CSS+='\n.mkt .msec[data-t="who"]{--c:#FFE7A6}\n.mkt .msec[data-t="apps"]{--c:#6FB0E0}\n.mkt .msec[data-t="surv"]{--c:#F0855A}'

JS = r"""
(function(){
  var root=document.querySelector('.mkt'); if(!root) return;

  /* ---- directory: search, filter, expand ---- */
  var cards=[].slice.call(root.querySelectorAll('.rcard')),
      btns=[].slice.call(root.querySelectorAll('.rfilt')),
      input=root.querySelector('#rq'),
      count=root.querySelector('#rcount'),
      none=root.querySelector('#rnone'),
      type='all';
  var RM=!!(window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches);
  var per={};
  cards.forEach(function(c){ var k=c.getAttribute('data-type'); per[k]=(per[k]||0)+1; });
  btns.forEach(function(b){
    var k=b.getAttribute('data-type');
    var n = k==='all' ? cards.length : (per[k]||0);
    if(!b.querySelector('.n')) b.insertAdjacentHTML('beforeend','<span class="n">'+n+'</span>');
  });
  function apply(){
    var q=(input.value||'').trim().toLowerCase(), n=0;
    cards.forEach(function(c){
      var okt = type==='all' || c.getAttribute('data-type')===type;
      var okq = !q || c.getAttribute('data-name').indexOf(q)>-1;
      var on=okt&&okq; c.hidden=!on; if(on) n++;
    });
    var idle = (type==='all' && !q);
    count.textContent = (idle||n===0) ? '' : (n===1 ? '1 match' : n+' matches');
    none.hidden = n>0;
  }
  input.addEventListener('input',apply);

  btns.forEach(function(b){
    b.addEventListener('click',function(){
      type=b.getAttribute('data-type');
      btns.forEach(function(x){ x.setAttribute('aria-pressed', x===b?'true':'false'); });
      apply();
    });
  });
  root.addEventListener('click',function(ev){
    var b=ev.target.closest && ev.target.closest('.rmore'); if(!b) return;
    var d=document.getElementById(b.getAttribute('aria-controls'));
    var open=b.getAttribute('aria-expanded')==='true';
    b.setAttribute('aria-expanded', open?'false':'true');
    b.textContent = open ? 'Details' : 'Close';
    if(d) d.hidden=open;
  });

  /* ---- the gap, drawn as one in thirty ---- */
  var rd=root.querySelector('#rdots');
  if(rd){
    for(var g=0;g<30;g++){
      var sp=document.createElement('span');
      sp.className='rdot'+(g===0?' on':'');
      rd.appendChild(sp);
    }
  }


  /* ---- three scroll effects, one per kind of number, none repeated ---- */
  if(!RM && 'IntersectionObserver' in window){
    root.classList.add('fx');
    /* whatever happens, nothing stays invisible. */
    setTimeout(function(){
      [].slice.call(root.querySelectorAll('.unum,.oddspct')).forEach(function(e){
        if(!e.classList.contains('done')) e.classList.add('done');
      });
      [].slice.call(root.querySelectorAll('.mstat')).forEach(function(c){ c.classList.add('flip'); });
    }, 6000);

    /* 1. the headline rolls its digits into place, like a ticker settling */
    var un=root.querySelector('.unum');
    if(un){
      var target=un.textContent, digits=target.replace(/[^0-9]/g,'');
      var rollIO=new IntersectionObserver(function(es){
        es.forEach(function(en){
          if(!en.isIntersecting) return;
          rollIO.disconnect();
          un.classList.add('rolling');
          var frames=0, max=26;
          var spin=setInterval(function(){
            frames++;
            var shown=target.replace(/[0-9]/g,function(){
              return String(Math.floor(Math.random()*10));
            });
            /* settle left to right */
            var keep=Math.floor((frames/max)*digits.length), k=0;
            shown=target.replace(/[0-9]/g,function(orig){
              k++; return k<=keep ? orig : String(Math.floor(Math.random()*10));
            });
            un.textContent=shown;
            if(frames>=max){ clearInterval(spin); un.textContent=target;
              un.classList.remove('rolling'); un.classList.add('done'); }
          },45);
        });
      },{threshold:.4});
      rollIO.observe(un);
    }

    /* 2. the stat band flips card by card */
    var band=[].slice.call(root.querySelectorAll('.mstat'));
    if(band.length){
      var flipIO=new IntersectionObserver(function(es){
        es.forEach(function(en){
          if(!en.isIntersecting) return;
          var cell=en.target;
          var row=[].slice.call(cell.parentNode.children);
          setTimeout(function(){ cell.classList.add('flip'); }, row.indexOf(cell)*110);
          flipIO.unobserve(cell);
        });
      },{threshold:.3});
      band.forEach(function(c){ flipIO.observe(c); });
    }

    /* 3. the survival figure counts up, unless the reader got there first */
    var pct=root.querySelector('.oddspct');
    if(pct){
      var pctIO=new IntersectionObserver(function(es){
        es.forEach(function(en){
          if(!en.isIntersecting) return;
          pctIO.disconnect();
          var end=parseFloat(pct.textContent)||0, t0=null;
          pct.classList.add('counting');
          function step(ts){
            if(!t0) t0=ts;
            var p=Math.min(1,(ts-t0)/1100), e=1-Math.pow(1-p,3);
            pct.textContent=(end*e).toFixed(1)+'%';
            if(p<1) requestAnimationFrame(step);
            else { pct.textContent=end.toFixed(1)+'%';
                   pct.classList.remove('counting'); pct.classList.add('done'); }
          }
          requestAnimationFrame(step);
        });
      },{threshold:.5});
      pctIO.observe(pct);
    }
  }

  /* ---- the reading rail: it reports position, it never changes content ---- */
  var rail=root.querySelector('.kxrail');
  if(rail){
    var rlinks=[].slice.call(rail.querySelectorAll('a')),
        fill=root.querySelector('#kxfill');
    var marks=rlinks.map(function(a){
      return {a:a, el:document.getElementById(a.getAttribute('href').slice(1))};
    }).filter(function(m){ return m.el; });
    function railScroll(){
      var y=window.pageYOffset||document.documentElement.scrollTop||0;
      var vh=window.innerHeight||800;
      var doc=Math.max(1,(document.documentElement.scrollHeight||1)-vh);
      if(fill) fill.style.height=Math.min(100,Math.max(0,(y/doc)*100))+'%';
      var cur=marks[0];
      marks.forEach(function(m){
        if(m.el.getBoundingClientRect().top < vh*0.45) cur=m;
      });
      rlinks.forEach(function(a){ a.classList.toggle('here', !!cur && a===cur.a); });
    }
    var rtick=false;
    window.addEventListener('scroll',function(){
      if(rtick) return; rtick=true;
      requestAnimationFrame(function(){ railScroll(); rtick=false; });
    },{passive:true});
    window.addEventListener('resize',railScroll,{passive:true});
    railScroll();
  }

  /* ---- the statement rises when its section opens. it changes nothing else. ---- */
  var turn=root.querySelector('#turn');
  if(turn){
    if(RM || !('IntersectionObserver' in window)){ turn.classList.add('lit'); }
    else {
      var tio=new IntersectionObserver(function(es){
        es.forEach(function(en){ if(en.isIntersecting){ turn.classList.add('lit'); tio.disconnect(); } });
      },{threshold:.4});
      tio.observe(turn);
    }
  }

  /* ---- the potential, compounding year on year ---- */
  var kgrid=root.querySelector('#kgrid');
  if(kgrid){
    var N=300, BACKLOG=168285699, TODAY=5600000, RATE=17388570, NOW=10;
    for(var k=0;k<N;k++){ var sp=document.createElement('span'); sp.className='kdot'; kgrid.appendChild(sp); }
    var kdots=[].slice.call(kgrid.children);
    var yrs=[].slice.call(root.querySelectorAll('.potyr')),
        built=root.querySelector('#g_built'), builtlab=root.querySelector('#g_builtlab'),
        more=root.querySelector('#g_more'), col2=root.querySelector('#g_col2'),
        foot=root.querySelector('#potfoot'), kladd=root.querySelector('#kl_add'),
        morelab=root.querySelector('#g_morelab');
    function mils(v){ return (v/1e6).toFixed(1).replace(/\.0$/,'')+' million'; }
    var order=[]; for(var i=0;i<N;i++) order.push(i);
    var seed=7; order.sort(function(){ seed=(seed*9301+49297)%233280; return seed/233280-0.5; });
    var nowSet=order.slice(0,NOW);
    var cur=NOW;
    function paint(total){
      var add=order.slice(NOW,total);
      kdots.forEach(function(d){ d.classList.remove('new'); });
      nowSet.forEach(function(i){ kdots[i].classList.add('on'); });
      if(total<=NOW){ cur=NOW; return; }
      add.forEach(function(i,k){
        if(RM){ kdots[i].classList.add('new'); return; }
        setTimeout(function(){ kdots[i].classList.add('new'); }, k*7);
      });
      cur=total;
    }
    function climb(el,from,to){
      if(RM){ el.textContent=(el===more?'+':'')+mils(to); return; }
      var t0=null;
      function step(ts){
        if(!t0) t0=ts;
        var p=Math.min(1,(ts-t0)/1400), e=1-Math.pow(1-p,3);
        var pre=(el===more?'+':'');
        el.textContent=pre+mils(from+(to-from)*e);
        if(p<1) requestAnimationFrame(step); else el.textContent=pre+mils(to);
      }
      requestAnimationFrame(step);
    }
    var lastTotal=TODAY, lastDelta=0;
    function setYear(y){
      var total = y===0 ? TODAY : RATE*y;
      var delta = y===0 ? 0 : (RATE-TODAY)*y;
      var marks = Math.min(N, Math.round(total/(BACKLOG/N)));
      paint(marks);
      climb(built,lastTotal,total); lastTotal=total;
      col2.hidden=(y===0); kladd.hidden=(y===0);
      if(y>0){ climb(more,lastDelta,delta); lastDelta=delta; }
      else { more.textContent=''; lastDelta=0; }
      var base=TODAY*y;
      builtlab.textContent = y===0 ? 'businesses started a year'
                                   : 'built in '+y+' year'+(y>1?'s':'')+', in total';
      var psr=root.querySelector('#pot_sr');
      if(psr) psr.textContent = y===0
        ? mils(TODAY)+' businesses started a year'
        : mils(total)+' built in '+y+' year'+(y>1?'s':'')+', of which '+mils(delta)+
          ' are new on top of the '+mils(base)+' today\u2019s pace would produce';
      if(morelab) morelab.textContent = y===0 ? 'that would not exist otherwise'
        : 'of those are new, on top of the '+mils(base)+' today\u2019s pace would produce anyway';
      var pct=Math.min(100,Math.round(total/BACKLOG*100));
      foot.textContent = y===0
        ? 'Three of every hundred people with an idea act on it in a year.'
        : (pct>=100 ? 'The entire 168 million, built.' : pct+'% of the 168 million ideas, built.');
    }
    yrs.forEach(function(b){
      b.addEventListener('click',function(){
        yrs.forEach(function(x){ x.setAttribute('aria-pressed', x===b?'true':'false'); });
        setYear(parseInt(b.getAttribute('data-y'),10));
      });
    });
    paint(NOW);
  }

  /* ---- the odds, one dot per hundred ---- */
  var dots=root.querySelector('#dots');
  if(dots){
    for(var i=0;i<100;i++){ var s=document.createElement('span'); s.className='dot'; dots.appendChild(s); }
    var all=[].slice.call(dots.children);
    var TOTAL=677876;
    var COHORT={1:{pct:79.6,n:539701,word:'a year later'},
                2:{pct:69.1,n:468293,word:'two years later'},
                5:{pct:50.2,n:340281,word:'five years later'},
                10:{pct:34.7,n:235071,word:'ten years later'}};
    var pctEl=root.querySelector('#oddspct'),
        labEl=root.querySelector('#oddslab'),
        subEl=root.querySelector('#oddssub');
    var oddb=[].slice.call(root.querySelectorAll('.oddb'));
    function light(years){
      var c=COHORT[years], n=Math.round(c.pct);
      all.forEach(function(dd,k){
        if(RM){ dd.classList.toggle('lit',k<n); return; }
        setTimeout(function(){ dd.classList.toggle('lit',k<n); }, k*9);
      });
      pctEl.textContent=c.pct+'%';
      labEl.textContent='still open '+c.word;
      subEl.textContent=c.n.toLocaleString('en-US')+' of the '+TOTAL.toLocaleString('en-US')+' that opened';
      var sr=root.querySelector('#oddspct_sr');
      if(sr) sr.textContent=c.pct+'% still open '+c.word+', '+
        c.n.toLocaleString('en-US')+' of the '+TOTAL.toLocaleString('en-US')+' that opened';
    }
    var picked=false;
    oddb.forEach(function(b){
      b.addEventListener('click',function(){
        picked=true;
        oddb.forEach(function(x){ x.setAttribute('aria-pressed', x===b?'true':'false'); });
        light(parseInt(b.getAttribute('data-y'),10));
      });
    });
    light(2);
  }

  /* ---- figures: swap between the country and the state ---- */
  var tabs=[].slice.call(root.querySelectorAll('.mtab'));
  tabs.forEach(function(t,gi){
    t.addEventListener('keydown',function(ev){
      var n=null;
      if(ev.key==='ArrowRight'||ev.key==='ArrowDown') n=(gi+1)%tabs.length;
      else if(ev.key==='ArrowLeft'||ev.key==='ArrowUp') n=(gi-1+tabs.length)%tabs.length;
      if(n===null) return;
      ev.preventDefault(); tabs[n].click(); tabs[n].focus();
    });
    t.addEventListener('click',function(){
      var k=t.getAttribute('data-set');
      tabs.forEach(function(x){
        var on=x===t;
        x.setAttribute('aria-selected', on?'true':'false');
        if(on) x.removeAttribute('tabindex'); else x.setAttribute('tabindex','-1');
      });
      [].slice.call(root.querySelectorAll('[data-panel]')).forEach(function(p){
        p.hidden = p.getAttribute('data-panel')!==k;
      });
    });
  });

  /* ---- the topic colour washes behind the page ---- */
  var wash=document.getElementById('reswash');
  if(!wash){ wash=document.createElement('div'); wash.id='reswash'; document.body.appendChild(wash); }
  var off=null;
  function washTo(c){ clearTimeout(off); wash.style.setProperty('--wash',c); wash.classList.add('on'); }
  function washOff(){ off=setTimeout(function(){ wash.classList.remove('on'); },260); }
  if(!RM){
    cards.concat(btns).forEach(function(el){
      el.addEventListener('pointerenter',function(){
        var c=getComputedStyle(el).getPropertyValue('--c');
        washTo((c&&c.trim())||'#D4A856');
      });
      el.addEventListener('pointerleave',washOff);
    });
  }
  apply();
})();
"""

crumbs={"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
 {"@type":"ListItem","position":1,"name":"Home","item":f"{SITE}/"},
 {"@type":"ListItem","position":2,"name":"Resources","item":f"{SITE}/resources.html"},
 {"@type":"ListItem","position":3,"name":"Market data","item":f"{SITE}/market-data.html"}]}
itemlist={"@context":"https://schema.org","@type":"ItemList",
 "name":"Free government resources for people starting a business",
 "numberOfItems":len(R),
 "itemListElement":[{"@type":"ListItem","position":i+1,
   "url":u,"name":n,"description":b} for i,(n,t,u,b,c,w,note) in enumerate(R)]}
dataset={"@context":"https://schema.org","@type":"Dataset",
 "name":"US and North Carolina small business figures","description":DESC,
 "url":f"{SITE}/market-data.html","creator":{"@id":f"{SITE}/#organization"},
 "isBasedOn":["https://www.census.gov/econ/bfs/index.html","https://www.bls.gov/bdm/",
   "https://data.sba.gov/en/dataset/state-small-business-statistics-2025"],
 "license":"https://www.usa.gov/government-works"}

MAIN=f"""<main id="maincontent">
<section class="wrap res mkt">
  <p class="kx-backrow"><a class="kx-bk" href="resources.html">
    <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M15 5l-7 7 7 7"/></svg>
    Back to resources</a></p>
  <p class="eyebrow eyenav">
    <a class="eyego" href="#sec-apps">Skip to the market data</a>
  </p>

  <h1 class="rhead">Help yourself.</h1>

  <nav class="kxrail" aria-label="Where you are on this page">
    <span class="kxtrack" aria-hidden="true"><span class="kxfill" id="kxfill"></span></span>
    <ul>
      <li><a href="#rq" data-w="help"><i></i><span>Help</span></a></li>
      <li><a href="#sec-apps" data-w="apps"><i></i><span>Potential Entrepreneurs</span></a></li>
      <li><a href="#sec-surv" data-w="surv"><i></i><span>Failing over time</span></a></li>
      <li><a href="#sec-who" data-w="who"><i></i><span>Existing Entrepreneurs</span></a></li>
    </ul>
  </nav>
  <h2 class="sr-only">Help by category</h2>

  <div class="rsearch" id="rq-top">
    <label class="sr-only" for="rq">Search the resources</label>
    <input id="rq" type="search" placeholder="Search, for example EIN or mentor" autocomplete="off">
  </div>
  <div class="rfilters">{pills}</div>
  <p class="rcount" id="rcount" aria-live="polite"></p>
  <div class="rgrid">{"".join(cards)}</div>
  <p class="rnone" id="rnone" hidden>Nothing matches that. Try a shorter word.</p>


  <div class="msec" data-t="apps" id="sec-apps">
    <h2>Potential Entrepreneurs</h2>
    <div class="mbody">
    <p class="mdek">174 million Americans aged 15 and over have had an idea for a business.
    Three in every hundred act on one in a given year.</p>

    <div class="unbuilt">
      <span class="sr-only">168 million</span><span class="unum" aria-hidden="true">168 million</span>
      <span class="ulab">ideas that never became anything</span>
      <span class="usub">Not a shortage of talent. A shortage of one place to go.</span>
    </div>


    <div class="pot">
      <p class="klegend">
        <span class="kl now"><i></i>Acting today</span>
        <span class="kl add" id="kl_add" hidden><i></i>Would act</span>
        <span class="kl off"><i></i>Still waiting</span>
      </p>
      <div class="kgrid" id="kgrid" aria-hidden="true"></div>
      <div class="potyrs" role="group" aria-label="How long">
        <button class="potyr" type="button" data-y="0" aria-pressed="true">Today</button>
        <button class="potyr" type="button" data-y="1" aria-pressed="false">1 year</button>
        <button class="potyr" type="button" data-y="2" aria-pressed="false">2 years</button>
        <button class="potyr" type="button" data-y="5" aria-pressed="false">5 years</button>
        <button class="potyr" type="button" data-y="10" aria-pressed="false">10 years</button>
      </div>
      <div class="potout">
        <span class="sr-only" id="pot_sr" aria-live="polite">5.6 million businesses started a year</span>
        <div class="gcol" aria-hidden="true">
          <span class="gnum" id="g_built">5.6 million</span>
          <span class="glab" id="g_builtlab">businesses started a year</span>
        </div>
        <div class="gcol gplus" id="g_col2" aria-hidden="true" hidden>
          <span class="gnum" id="g_more">&nbsp;</span>
          <span class="glab" id="g_morelab">that would not exist otherwise</span>
        </div>
      </div>
      <p class="potfoot" id="potfoot">Three of every hundred people with an idea act on it in a year.</p>
    </div>

    <p class="closer">Talent is everywhere. Opportunity is for all.</p>

    <p class="msrc tight">Sources: <a href="https://zapier.com/blog/potential-entrepreneurs-report/" target="_blank" rel="noopener">Harris Poll for Zapier</a>, 2,001 US adults &middot;
    <a href="https://fred.stlouisfed.org/series/SPPOP0014TOZSUSA" target="_blank" rel="noopener">World Bank age structure</a> &middot;
    <a href="https://www.census.gov/econ/bfs/index.html" target="_blank" rel="noopener">Census Business Formation Statistics</a> &middot;
    <a href="https://www.census.gov/data/tables/time-series/demo/popest/2020s-national-detail.html" target="_blank" rel="noopener">Census population estimates</a>. The potential figure is a goal, not a measurement.</p>
    </div>
  </div>

  <div class="msec" data-t="surv" id="sec-surv">
    <h2>Failing over time</h2>
    <div class="mbody">
    <p class="mdek">One group of businesses, followed the whole way. The BLS tracked every private
    establishment that opened in the year ended March 2015 and counted how many were still open each
    year after.</p>
    <div class="oddsbtns" role="group" aria-label="Choose a milestone">
      <button class="oddb" type="button" data-y="1" aria-pressed="false">1 year</button>
      <button class="oddb" type="button" data-y="2" aria-pressed="true">2 years</button>
      <button class="oddb" type="button" data-y="5" aria-pressed="false">5 years</button>
      <button class="oddb" type="button" data-y="10" aria-pressed="false">10 years</button>
    </div>
    <div class="odds">
      <div class="dots" id="dots" aria-hidden="true"></div>
      <div class="oddsfig">
        <span class="sr-only" id="oddspct_sr" aria-live="polite">69.1% still open two years later</span><span class="oddspct" id="oddspct" aria-hidden="true">69.1%</span>
        <span class="oddslab" id="oddslab" aria-hidden="true">still open two years later</span>
        <span class="oddssub" id="oddssub" aria-hidden="true">468,293 of the 677,876 that opened</span>
      </div>
    </div>
    <div class="turn" id="turn">
      <h3>It doesn&rsquo;t have to be that way.</h3>
      <p class="turnp">Closing is not the same as failing, and the ones that did fail rarely failed for
      want of effort. What was missing was everything below, and most of it was already funded and
      open to them before they ever started.</p>
      <ul class="turnbits">
        <li>Guidance</li><li>Support</li><li>Community</li><li>Advice</li>
        <li>Events</li><li>Resources</li><li>Training</li>
      </ul>
      <a class="turnlink" href="#rq">Find it, all in one place</a>
    </div>

    <p class="oddscaveat">An establishment stops counting once it stops reporting employment, which
    also captures owners who sell, merge or retire. Read it as churn rather than failure.</p>
    <p class="msrc tight">Source: <a href="https://www.bls.gov/bdm/us_age_naics_00_table7.txt" target="_blank" rel="noopener">BLS Business Employment Dynamics, Table 7, total private</a>, data through March 2025</p>
    </div>
  </div>

  <div class="msec" data-t="who" id="sec-who">
    <h2>Existing Entrepreneurs</h2>
    <div class="mbody">
    <p class="mdek">The SBA Office of Advocacy assembles federal data into a profile each year.
    Switch between the country and the state.</p>
    <div class="mtabs" role="tablist" aria-label="Choose a geography">
      <button class="mtab" type="button" role="tab" id="geo-us" data-set="us" aria-selected="true" aria-controls="panel-us">United States</button>
      <button class="mtab" type="button" role="tab" id="geo-nc" data-set="nc" aria-selected="false" aria-controls="panel-nc" tabindex="-1">North Carolina</button>
    </div>
    <div class="mstats" data-panel="us" id="panel-us" role="tabpanel" aria-labelledby="geo-us">{US}</div>
    <div class="mstats" data-panel="nc" id="panel-nc" role="tabpanel" aria-labelledby="geo-nc" hidden>{NC}</div>
    <p class="msrc">Sources: <a href="https://advocacy.sba.gov/2025/06/30/new-advocacy-report-shows-the-number-of-small-businesses-in-the-u-s-exceeds-36-million/" target="_blank" rel="noopener">SBA Office of Advocacy, 2025 Small Business Profiles</a> &middot;
    <a href="https://www.census.gov/library/stories/2026/05/small-business-week.html" target="_blank" rel="noopener">US Census Bureau, Nonemployer Statistics 2023</a></p>
    </div>
  </div>

  <section class="pfaq" aria-labelledby="pfaq-h">
    <h2 id="pfaq-h">Questions this page answers</h2>
    <details><summary>How many business ideas never get acted on?</summary>
      <div class="pa"><p>About 168 million. Roughly 174 million Americans aged 15 and over have had an
      idea for a business, and around 5.6 million business applications are filed in a year.</p></div></details>
    <details><summary>How many business ideas are buried every day?</summary>
      <div class="pa"><p>Around 5,000, or one every 17 seconds. That figure comes from the 3,072,666 US
      deaths registered in 2024, the share of adults who have had a business idea, and the share who
      never acted on one.</p></div></details>
    <details><summary>What percentage of new businesses survive?</summary>
      <div class="pa"><p>Of the 677,876 US establishments that opened in the year ended March 2015,
      79.6% were still operating after one year, 69.1% after two, 50.2% after five and 34.7% after ten.
      An establishment stops counting once it stops reporting employment, which also captures owners
      who sell, merge or retire.</p></div></details>
    <details><summary>How many US businesses have no employees?</summary>
      <div class="pa"><p>78.4% of all US establishments in 2023, which is 30,427,808 businesses turning
      over nearly $1.8 trillion between them.</p></div></details>
    <details><summary>Where can I get help starting a business at no cost?</summary>
      <div class="pa"><p>SCORE mentoring, Small Business Development Centers, Women's Business Centers
      and Veterans Business Outreach Centers are all SBA-funded and carry no charge, and are searchable by
      zip code. The Help tab above lists 29 of them with what each costs and who it is for.</p></div></details>
    <details><summary>How many small businesses are in North Carolina?</summary>
      <div class="pa"><p>1.1 million, which is 99.6% of all businesses in the state. They employ 1.8
      million people, or 44.2% of the state's workforce.</p></div></details>
  </section>

  <div class="mfoot">
    <h2>Where this comes from</h2>
    <p>Everything here is published by a US federal or state agency. Works of the federal government
    are in the public domain, and facts cannot be copyrighted, so anyone may use this material. We have written every description ourselves and linked every source.</p>
    <p>Application figures update monthly, employment and survival figures quarterly or annually.
    Follow any source link for the current release rather than trusting this page to be fresh.</p>
  </div>

  <div class="mhubs">
    <a class="mhub" href="tools.html"><b>Calculators</b><span>Four numbers, worked out</span></a>
    <a class="mhub" href="glossary.html"><b>Glossary</b><span>59 terms, plainly</span></a>
    <a class="mhub" href="resources.html"><b>Resources</b><span>Everything, all of it</span></a>
  </div>
</section>
</main>"""

PFAQ=[
 ("How many business ideas never get acted on?",
  "About 168 million. Roughly 174 million Americans aged 15 and over have had an idea for a business, and around 5.6 million business applications are filed in a year."),
 ("How many business ideas are buried every day?",
  "Around 5,000, or one every 17 seconds. That figure comes from the 3,072,666 US deaths registered in 2024, the share of adults who have had a business idea, and the share who never acted on one."),
 ("What percentage of new businesses survive?",
  "Of the 677,876 US establishments that opened in the year ended March 2015, 79.6% were still operating after one year, 69.1% after two, 50.2% after five and 34.7% after ten. An establishment stops counting once it stops reporting employment, which also captures owners who sell, merge or retire."),
 ("How many US businesses have no employees?",
  "78.4% of all US establishments in 2023, which is 30,427,808 businesses turning over nearly $1.8 trillion between them."),
 ("Where can I get help starting a business at no cost?",
  "SCORE mentoring, Small Business Development Centers, Women's Business Centers and Veterans Business Outreach Centers are all SBA-funded and carry no charge, and all are searchable by zip code. This page lists 29 of them with what each costs and who it is for."),
 ("How many small businesses are in North Carolina?",
  "1.1 million, which is 99.6% of all businesses in the state. They employ 1.8 million people, or 44.2% of the state's workforce."),
]
faqschema={"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
  {"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in PFAQ]}

out=page("market-data.html","Small Business Help & Data: US and North Carolina | SideKix",
         DESC, MAIN, extra_css=CSS, extra_js=JS, schema=(itemlist,dataset,faqschema,crumbs))
open("/home/claude/site/market-data.html","w",encoding="utf-8").write(out)
print("rebuilt:",len(out)//1024,"KB |",len(R),"resources |",len(TYPES),"categories")
