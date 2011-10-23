# pyRazor.py
# Python Razor Template Implementation

from lex import RazorLexer, Token
from razorview import View

def render(text, debug=False):
  lex = RazorLexer.create()
  view = View()
  for token in lex.scan(text):
    if debug:
      print token
    view.parseToken(lex.getScope(), token)
  view.build(debug=debug)
  view.render()
