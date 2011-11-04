# pyRazor.py
# Python Razor Template Implementation

import viewloader

def render(text, model=None, ignore_whitespace=False, debug=False):
  """Renders a template given the template text"""
  if debug:
    print text
  view = viewloader.buildview(text, ignore_whitespace, debug)
  return view.render(model)

