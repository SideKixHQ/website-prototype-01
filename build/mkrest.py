# -*- coding: utf-8 -*-
import os, sys, json, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from toolgen import page, crumbs, webapp, faqpage, SITE
def e(s): return html.escape(str(s), quote=True)

# ════════════════════════ 1. structure comparator ════════════════════════
CMP_CSS = """
/* ---- structure comparator ----
   Reference, not advice. Every row states what the three structures do
   differently and none of them says which to pick, because that turns on facts
   about a particular business that a web page does not have. */
.bs{max-width:1000px;margin:0 auto}
.bs-tw{overflow-x:auto;-webkit-overflow-scrolling:touch;margin:0 0 24px}
.bs-t{width:100%;min-width:720px;border-collapse:collapse;font-size:15.5px}
.bs-t th,.bs-t td{text-align:left;vertical-align:top;padding:18px 18px 18px 0;
  border-top:1px solid rgba(255,255,255,.08)}
.bs-t thead th{border-top:none;padding-bottom:14px}
.bs-t thead th span{display:block;font-family:var(--display);font-size:24px;color:#FFF8E8;margin:0 0 4px}
.bs-t thead th small{font-family:var(--util);font-size:9.5px;letter-spacing:.16em;
  text-transform:uppercase;color:var(--gold);font-weight:400}
.bs-t tbody th{font-family:var(--util);font-size:10.5px;letter-spacing:.16em;text-transform:uppercase;
  color:var(--gold);font-weight:400;width:170px;padding-right:22px}
.bs-t td{color:#CEC9BC;line-height:1.7}
.bs-t td b{color:#F1ECE2;font-weight:600}
.bs-cards{display:none}
.bs-ref{border:1px solid rgba(212,168,86,.22);border-radius:12px;padding:18px 20px;
  font-size:14.5px;line-height:1.75;color:#9C968D;margin:28px 0 0}
.bs-ref b{color:#E8DEC4;font-weight:600}
.bs-ref a{color:#EBD08C;text-decoration:none;border-bottom:1px solid rgba(212,168,86,.3)}
.bs-ref a:hover{color:#FFF6DC}
@media(max-width:760px){
  .bs-tw{display:none}
  .bs-cards{display:grid;gap:18px}
  .bs-c{border:1px solid rgba(212,168,86,.24);border-radius:16px;padding:22px 20px;
    background:radial-gradient(120% 120% at 50% 0,rgba(33,26,10,.5),rgba(12,11,8,.7))}
  .bs-c > h2{font-family:var(--display);font-size:24px;color:#FFF8E8;margin:0 0 2px}
  .bs-c > p.k{font-family:var(--util);font-size:9.5px;letter-spacing:.16em;text-transform:uppercase;
    color:var(--gold);margin:0 0 16px}
  .bs-c dl{margin:0}
  .bs-c dt{font-family:var(--util);font-size:10px;letter-spacing:.16em;text-transform:uppercase;
    color:var(--gold);margin:14px 0 4px}
  .bs-c dd{margin:0;font-size:15px;line-height:1.65;color:#CEC9BC}
}
"""
COLS = [("Sole proprietor", "No filing to exist"),
        ("LLC", "Filed with the state"),
        ("S corporation", "A tax election, not a structure")]
ROWS = [
 ("What it is", [
  "The default. If you start working for yourself and file nothing, this is what you are.",
  "A separate legal entity created by filing a formation document with a state.",
  "An election made with the IRS about how an existing entity is taxed. An LLC or a corporation elects it."]),
 ("Liability", [
  "No separation. Business debts and claims reach personal assets.",
  "Separation, as long as the entity is kept separate in practice: its own account, its own records, no mixing of funds.",
  "Follows whatever entity made the election. Electing S status changes tax treatment, not liability."]),
 ("How it is taxed", [
  "Profit is reported on the owner's personal return. Self employment tax applies to all of it.",
  "By default the same as a sole proprietor for one owner, or a partnership for several. The entity itself pays no federal income tax.",
  "Profit still flows to the owners' personal returns, but an owner working in the business is paid a wage, and only that wage carries employment tax."]),
 ("Ownership", [
  "One owner. Adding a second changes what it is.",
  "Any number, and members can be people, companies or trusts.",
  "Limits apply: a capped number of shareholders, and shareholders have to be US individuals or certain trusts and estates."]),
 ("What it costs", [
  "Nothing to exist. Local licences may still apply.",
  "A state filing fee, and in most states a periodic report fee after that.",
  "Nothing to elect, but it adds a separate business return and a payroll obligation, which usually means paying someone to run it."]),
 ("Ongoing work", [
  "Records for your own tax return.",
  "Keep the entity current with the state, keep money separate, file the periodic report where one is required.",
  "Everything the underlying entity requires, plus payroll, plus its own annual return."]),
 ("Where it tends to fit", [
  "Testing something, or a business with little to lose in a claim.",
  "Anything with customers, contracts, premises or staff, where a claim reaching personal assets would matter.",
  "Businesses already profitable enough that the employment tax saved is larger than the cost of running the payroll and the extra return."]),
]
tbl = ['<div class="bs-tw"><table class="bs-t"><thead><tr><th></th>']
for nm, kk in COLS:
    tbl.append('<th scope="col"><span>%s</span><small>%s</small></th>' % (e(nm), e(kk)))
tbl.append('</tr></thead><tbody>')
for label, cells in ROWS:
    tbl.append('<tr><th scope="row">%s</th>' % e(label))
    for c in cells:
        tbl.append("<td>%s</td>" % c)
    tbl.append("</tr>")
tbl.append("</tbody></table></div>")
cards = ['<div class="bs-cards">']
for i, (nm, kk) in enumerate(COLS):
    cards.append('<article class="bs-c"><h2>%s</h2><p class="k">%s</p><dl>' % (e(nm), e(kk)))
    for label, cells in ROWS:
        cards.append("<dt>%s</dt><dd>%s</dd>" % (e(label), cells[i]))
    cards.append("</dl></article>")
cards.append("</div>")
BS_BODY = ("<div class=\"bs\">" + "".join(tbl) + "".join(cards) +
  '<p class="bs-ref"><b>This is reference, not advice.</b> Which structure fits turns on facts about '
  'one particular business, and on state law that differs from the general position above. The '
  'authorities are '
  '<a href="https://www.irs.gov/businesses/small-businesses-self-employed/business-structures" rel="noopener nofollow" target="_blank">the IRS on business structures</a>, '
  '<a href="https://www.sba.gov/business-guide/launch-your-business/choose-business-structure" rel="noopener nofollow" target="_blank">the SBA guide</a>, '
  'and your own state, which is on our <a href="state-filing.html">state filing lookup</a>. '
  'A tax professional or an attorney is the person who can apply any of it to your situation.</p></div>')

BS_FAQ = [
 ("What is the difference between an LLC and a sole proprietorship?",
  "A sole proprietorship is what you are by default if you work for yourself and file nothing, and there is no separation between you and the business, so business debts and claims can reach personal assets. An LLC is a separate legal entity created by filing with a state, and that separation holds as long as the entity is genuinely kept separate in practice."),
 ("Is an S corporation a type of company?",
  "No. It is an election made with the IRS about how an existing entity is taxed. An LLC or a corporation can elect it. Electing S status changes tax treatment and does not change liability."),
 ("When does an S corporation election start to make sense?",
  "It is an arithmetic question rather than a stage question: the employment tax saved has to be larger than the cost of running payroll and filing a separate business return. That comparison depends on profit, on a reasonable wage for the work, and on what a preparer charges, which is why an accountant is the person who can answer it for a specific business."),
 ("Does forming an LLC protect my personal assets?",
  "The separation is real but it is not automatic. It depends on the entity being kept genuinely separate: its own bank account, its own records, no mixing of personal and business money. Courts look at whether the separation was observed in practice."),
]
n = page("business-structures.html",
  "Sole Proprietor vs LLC vs S Corp: Side by Side | SideKix",
  "Sole proprietor, LLC and S corporation compared on what differs: liability, taxes, ownership limits, cost and ongoing work. Reference, not advice.",
  "Business structures",
  "Sole proprietor, LLC, <em>S corp</em>.",
  "Seven rows on what actually differs between them. No recommendation, because which one fits turns on facts about your business and your state that this page does not have.",
  BS_BODY, css=CMP_CSS,
  schema=(webapp("Business Structure Comparison","business-structures.html",
            "Sole proprietor, LLC and S corporation compared row by row.",
            ["Liability","Taxation","Ownership limits","Cost","Ongoing work"]),
          faqpage(BS_FAQ), crumbs("Business structures","business-structures.html")))
print("business-structures.html %.0f KB" % (n/1024))
