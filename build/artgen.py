"""Generate a SideKix blog article on the existing article template."""
import json, html, os, re

SITE="https://sidekixhq.com"
TAIL=open("/home/claude/build/_art_tail.html",encoding="utf-8").read() if os.path.exists("/home/claude/build/_art_tail.html") else None

def words(body_html):
    return len(re.sub(r"<[^>]+>"," ",body_html).split())

def article(slug,title,og_title,desc,cat,standfirst,body,faq,related,published="2026-08-27",read=None):
    wc=words(body)
    read=read or max(4,round(wc/225))
    url=f"{SITE}/blog/{slug}/"
    blog={"@context":"https://schema.org","@type":"BlogPosting","headline":og_title,
      "description":desc,"datePublished":published,"dateModified":published,
      "author":{"@type":"Organization","name":"SideKix","url":SITE+"/"},
      "publisher":{"@type":"Organization","name":"SideKix",
        "logo":{"@type":"ImageObject","url":SITE+"/assets/k-mark.png"}},
      "mainEntityOfPage":{"@type":"WebPage","@id":url},
      "articleSection":cat,"wordCount":wc}
    crumbs={"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
      {"@type":"ListItem","position":1,"name":"Home","item":SITE+"/"},
      {"@type":"ListItem","position":2,"name":"Resources","item":SITE+"/resources.html"},
      {"@type":"ListItem","position":3,"name":og_title,"item":url}]}
    faqschema={"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
      {"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer",
       "text":re.sub(r"<[^>]+>","",a)}} for q,a in faq]}
    faqhtml="".join(
      f'      <details>\n        <summary>{html.escape(q)}</summary>\n'
      f'        <div class="a"><p>{a}</p></div>\n      </details>\n' for q,a in faq)
    relhtml="".join(f'        <li><a href="{h}">{html.escape(t)}<span>{c}</span></a></li>\n'
                    for t,h,c in related)
    S=json.dumps
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{url}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta property="og:type" content="article">
<meta property="og:site_name" content="SideKix">
<meta property="og:title" content="{html.escape(og_title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/assets/k-mark.png">
<meta property="article:published_time" content="{published}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#050505">
<link rel="icon" href="../../favicon.ico">
<link rel="preload" href="../../assets/fonts.css" as="style">
<link rel="stylesheet" href="../../assets/fonts.css">
<link rel="stylesheet" href="../../assets/article.css">
<script type="application/ld+json">{S(blog,ensure_ascii=False)}</script>
<script type="application/ld+json">{S(crumbs,ensure_ascii=False)}</script>
<script type="application/ld+json">{S(faqschema,ensure_ascii=False)}</script>
</head>
<body>
<div id="progress" aria-hidden="true"></div>
<a class="skip-link" href="#maincontent">Skip to content</a>

<header class="abar">
  <a class="home" href="../../index.html" aria-label="SideKix home">
    <img src="../../assets/sidekix-wordmark.png" alt="SideKix">
  </a>
  <a class="acta" href="../../membership.html">Build the Future</a>
</header>

<main id="maincontent">
<div class="artgrid">
  <article>
    <div class="ahead">
      <a class="backlink" href="../../resources.html">
        <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M15 5l-7 7 7 7"/></svg>
        Back to the blog
      </a>
      <span class="cat" data-cat="{cat}">{cat}</span>
      <h1>{html.escape(og_title)}</h1>
      <p class="standfirst">{standfirst}</p>
      <div class="meta">
        <span><b>Published</b> 27 August 2026</span>
        <span><b>Reading time</b> {read} minutes</span>
        <span><b>Category</b> {cat}</span>
      </div>
    </div>

    <div class="body">
{body}
    </div>

    <section class="faqs" aria-labelledby="faq-h">
      <h2 id="faq-h" class="faqhead">Frequently asked questions</h2>
{faqhtml}    </section>

    <section class="cta" aria-labelledby="cta-h">
      <h2 id="cta-h">Rather have this <em>sequenced for you</em>?</h2>
      <p>SideKix turns reading like this into a path: the next step surfaced one at a time, with the people and resources you need at the point you need them.</p>
      <div class="row">
        <a class="go" href="../../how-it-works.html">See how it works</a>
        <a class="alt" href="../../resources.html">More free guides</a>
      </div>
    </section>

    <section class="related" aria-labelledby="rel-h">
      <h2 id="rel-h">Related reading</h2>
      <ul>
{relhtml}      </ul>
    </section>
  </article>

  <nav class="toc" aria-labelledby="toc-h">
    <h2 id="toc-h">On this page</h2>
    <ol id="toc-list"></ol>
  </nav>
</div>
</main>

{{FOOTER}}
</body>
</html>
"""

def write(slug,**kw):
    footer=re.search(r'<footer class="sk-fo.*?</footer>',
        open("/home/claude/site/blog/how-to-get-help-starting-a-business/index.html",encoding="utf-8").read(),re.S).group(0)
    scripts=re.findall(r'<script src="[^"]*article\.js"></script>',
        open("/home/claude/site/blog/how-to-get-help-starting-a-business/index.html",encoding="utf-8").read())
    out=article(slug,**kw).replace("{FOOTER}", footer+"\n"+"\n".join(scripts))
    d=f"/home/claude/site/blog/{slug}"
    os.makedirs(d,exist_ok=True)
    open(f"{d}/index.html","w",encoding="utf-8").write(out)
    return words(kw["body"])
