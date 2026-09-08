# -*- coding: utf-8 -*-
"""The Declaration, rebuilt on the current shell.

Same treatment the Energy Discovery got: the page arrived built against an
older snapshot of the site, so its three parts are lifted out and rebuilt
through toolgen. The artwork is the one James drew, re-encoded to webp, and
the phantom 1600 entry in the srcset is gone because that file was a byte for
byte copy of the 1024 and would have had browsers download the same pixels
believing they were getting more.
"""
import os, sys, io
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from toolgen import page, crumbs, SITE

P = os.path.join(os.path.dirname(os.path.abspath(__file__)), "parts")
CSS  = io.open(os.path.join(P, "decl.css"), encoding="utf-8").read()
JS   = io.open(os.path.join(P, "decl.js"),  encoding="utf-8").read()
BODY = io.open(os.path.join(P, "decl.html"), encoding="utf-8").read()

BACK = ('<p class="kx-backrow"><a class="kx-bk" href="back-room.html">'
        '<svg aria-hidden="true" focusable="false" viewbox="0 0 24 24">'
        '<path d="M15 5l-7 7 7 7"></path></svg> Back to the Back Room</a></p>')

TITLE = "A Declaration of Independence for Builders | SideKix"
DESC  = ("A declaration for anyone who has decided to build something of their own, "
         "written to be read and signed. Add your name and keep your copy.")
LEDE  = ("Written for anyone who has decided to stop waiting for permission. Read it, and "
         "if it says what you would have said, put your name to it.")

SCHEMA = (
  crumbs("The Declaration", "declaration.html"),
  {"@context":"https://schema.org","@type":"WebPage",
   "@id":f"{SITE}/declaration.html#page","url":f"{SITE}/declaration.html",
   "name":"A Declaration of Independence","description":DESC,
   "publisher":{"@type":"Organization","name":"SideKix","url":SITE}},
)

n = page("declaration.html", TITLE, DESC, "The Declaration",
         "There is <em>Another Way</em>.", LEDE, BODY,
         css=CSS, js=JS, schema=SCHEMA, wrapcls="wrap res decl", back=BACK)
print(f"declaration.html {n//1024} KB")
