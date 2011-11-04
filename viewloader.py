"""
Loads a view either via dynamically loading its pyr file or building a pyr file.
"""

__author__ = "Alex Lusco"

# Imports
from lex import RazorLexer, Token
from razorview import View

def buildview(text, ignore_whitespace = False, debug=False):
  """Parses text building a view"""
  lex = RazorLexer.create(ignore_whitespace)
  view = View(lex.scope)
  for token in lex.scan(text):
    if debug:
      print token
    view.parseToken(token)
  view.build(debug=debug)
  return view

def loadfile(file):
  """Loads a file from disk and returns a view"""
  with open(file, 'r') as f:
    viewdata = f.readlines()
    return buildview(viewdata)
