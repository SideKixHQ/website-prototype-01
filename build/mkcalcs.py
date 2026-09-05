import io, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from toolgen import page, crumbs, webapp, faqpage, SITE

P = os.path.join(os.path.dirname(os.path.abspath(__file__)), "parts")
def part(n): return io.open(os.path.join(P, n), encoding="utf-8").read()

CALCS = [
 dict(cid="startup", file="startup-cost-calculator.html",
      title="Startup Cost Calculator: What It Costs to Start | SideKix",
      name="Startup Cost Calculator",
      eyebrow="Startup costs",
      h1="What will it cost <em>to start</em>?",
      lede="One-off costs to open the doors, plus the months of running costs you need behind you. Change any figure and the answer moves. Nothing is saved and nothing is sent.",
      desc="Free startup cost calculator. Add your one-off costs and monthly running costs and see what you need before you open. Nothing saved, nothing sent, no account.",
      feats=["One-off setup costs","Monthly running costs","Runway in months","Total to open"],
      faqs=[("What does it cost to start a business?","It depends far more on the shape of the business than on the industry. The honest number is your one-off costs to open plus enough months of running costs to reach the point where revenue covers them. This calculator adds both."),
            ("How many months of running costs should I have?","There is no single answer. The calculator lets you set the number so you can see what three months costs against six, and decide with the figure in front of you.")]),
 dict(cid="breakeven", file="breakeven-calculator.html",
      title="Breakeven Calculator: Units and Revenue | SideKix",
      name="Breakeven Calculator",
      eyebrow="Breakeven",
      h1="When do you <em>break even</em>?",
      lede="Fixed costs divided by what each sale contributes. The answer is in units and in revenue, because those are two different conversations.",
      desc="Free breakeven calculator. Enter fixed costs, price and variable cost per sale to see the units and the revenue you need to cover them. Nothing saved, nothing sent.",
      feats=["Breakeven in units","Breakeven in revenue","Contribution margin"],
      faqs=[("How do I work out my breakeven point?","Divide your fixed costs by the contribution each sale makes, which is your price minus the variable cost of delivering it. This page does that arithmetic and shows the revenue figure it corresponds to."),
            ("What counts as a fixed cost?","Anything you pay whether or not you sell anything: rent, software, insurance, a salary. Variable costs are the ones that only happen because a sale happened.")]),
 dict(cid="hourly", file="hourly-rate-calculator.html",
      title="Hourly Rate Calculator for Freelancers | SideKix",
      name="Hourly Rate Calculator",
      eyebrow="Hourly rate",
      h1="What should you <em>charge an hour</em>?",
      lede="Start from the income you want, add what the business costs to run, then divide by the hours you can actually bill. That last part is where most rates go wrong.",
      desc="Free hourly rate calculator for freelancers and consultants. Works back from the income you want and the hours you can actually bill, not the hours you work.",
      feats=["Rate from target income","Billable versus worked hours","Day rate"],
      faqs=[("How do I set a freelance hourly rate?","Start from the income you want, add your business costs, then divide by the hours you can actually bill, which is always fewer than the hours you work. This page shows both the raw figure and what it becomes once unbillable time is accounted for."),
            ("Why is my billable percentage lower than I think?","Selling, admin, invoicing, learning and the gaps between projects are all real hours that nobody pays for. Sixty percent billable is a common reality for people working alone.")]),
 dict(cid="pricing", file="product-pricing-calculator.html",
      title="Product Pricing Calculator: Margin and Fees | SideKix",
      name="Product Pricing Calculator",
      eyebrow="Product pricing",
      h1="What should you <em>price a product</em> at?",
      lede="Works back from the margin you want rather than marking up a cost and hoping. Materials, labour, overhead and payment fees all come out of the same number.",
      desc="Free product pricing calculator. Works back from the margin you want, with materials, labour, overhead and payment fees included. Nothing saved, nothing sent.",
      feats=["Price from target margin","Materials, labour and overhead","Payment fees","Profit per sale"],
      faqs=[("How should I price a product?","Decide the margin you need first, then work backwards to the price that produces it once materials, labour, overhead and payment fees are taken out. Marking a cost up by a round percentage tends to hide the fees."),
            ("Should payment fees come out of the price?","They come out of every sale whether or not you planned for them, so a price set without them is a margin that is smaller than it looks. This calculator takes them off the top.")]),
]

for c in CALCS:
    body = ('<div class="calcs">' + part("calc_%s.html" % c["cid"]) + "</div>")
    sch = (webapp(c["name"], c["file"], c["desc"], c["feats"]),
           faqpage(c["faqs"]), crumbs(c["name"], c["file"]))
    n = page(c["file"], c["title"], c["desc"], c["eyebrow"], c["h1"], c["lede"],
             body, schema=sch)
    print("%-34s %6.0f KB" % (c["file"], n/1024))
