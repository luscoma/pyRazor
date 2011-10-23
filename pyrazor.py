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
    view.parseToken(lex.getIndent(), token)
  view.build(debug=True)
  view.render()
