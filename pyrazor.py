# pyRazor.py
# Python Razor Template Implementation

from lex import RazorLexer, Token
from razorview import View

def render(text, model=None, debug=False):
  """Renders a template given the template text"""
  view = _buildView(text, debug)
  return view.render(model)

def _buildView(text, debug=False):
  """Parses text building a view"""
  lex = RazorLexer.create()
  view = View()
  for token in lex.scan(text):
    if debug:
      print token
    view.parseToken(lex.getScope(), token)
  view.build(debug=debug)
  return view
