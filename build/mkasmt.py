# -*- coding: utf-8 -*-
"""The Twelve Energies assessment, rebuilt on the current shell.

The zip arrived built against an older snapshot of the site: its nav still
said Library rather than Resources and its back link pointed there. Rather
than patch the chrome, the page's own three parts are lifted out and rebuilt
through toolgen, so it inherits whatever the rest of the site currently has,
including the focus rules, the form border contrast and the visible FAQ.
"""
import os, sys, io, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from toolgen import page, crumbs, SITE

HERE = os.path.dirname(os.path.abspath(__file__))
PARTS = os.path.join(HERE, "parts")
CSS  = io.open(os.path.join(PARTS, "asmt.css"), encoding="utf-8").read()
JS   = io.open(os.path.join(PARTS, "asmt.js"),  encoding="utf-8").read()
BODY = io.open(os.path.join(PARTS, "asmt.html"), encoding="utf-8").read()

TITLE = "The Energy Discovery: Which Twelve Do You Run On? | SideKix"
DESC  = ("Forty eight statements, about six minutes, and a read on which of the twelve "
         "energies you run on. Nothing is stored and nothing is sent.")
H1    = "Twelve energies.<br/>You have all of them."
LEDE  = ("In about six minutes, discover how your 12 energies show up in the way you work, "
         "think, and respond. See which ones you rely on most, when others come forward, "
         "and the value each one brings.")

FAQ = [
 ("How long does the Energy Discovery take?",
  "About six minutes. It is forty eight statements over eight pages, four statements for each "
  "of the twelve energies, answered on a four point scale with no neutral option."),
 ("Is this a personality test?",
  "No. It is a self-report reflection tool built on established assessment practice, and it has "
  "not been through the reliability and validity testing that would let it be used for hiring, "
  "clinical or diagnostic purposes. The result is a distribution across all twelve energies "
  "rather than a label, because everyone runs on all of them in different proportions."),
 ("What happens to my answers?",
  "Nothing leaves the browser. The scoring runs on the device, there is no account, no email "
  "and no server involved, and closing the tab ends it."),
 ("Why twelve energies and not a type?",
  "A type puts you in one box and leaves you there. A distribution shows which energies you "
  "lean on, which ones come forward under pressure and which ones are quiet, which is the part "
  "that changes as a business grows."),
]

SCHEMA = (
  crumbs("The Energy Discovery", "assessment.html"),
  {"@context":"https://schema.org","@type":"WebApplication",
   "@id":f"{SITE}/assessment.html#app","url":f"{SITE}/assessment.html",
   "name":"The Energy Discovery","applicationCategory":"BusinessApplication",
   "operatingSystem":"Any","browserRequirements":"Requires JavaScript",
   "description":DESC,
   "offers":{"@type":"Offer","price":"0","priceCurrency":"USD"},
   "publisher":{"@type":"Organization","name":"SideKix","url":SITE}},
  {"@context":"https://schema.org","@type":"FAQPage",
   "mainEntity":[{"@type":"Question","name":q,
                  "acceptedAnswer":{"@type":"Answer","text":a}} for q,a in FAQ]},
)

n = page("assessment.html", TITLE, DESC, "Energy Discovery", H1, LEDE, BODY,
         css=CSS, js=JS, schema=SCHEMA, wrapcls="wrap res asmt")
print(f"assessment.html {n//1024} KB")
