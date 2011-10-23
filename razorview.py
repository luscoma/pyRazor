# Alex Lusco

from lex import Token
from types import MethodType

class View(object):
  """A razor view"""
  def __init__(self):
    self.lines = []

  def _outputLine(self, scope, text):
    line = " " * scope
    line += text
    self.lines.append(line)

  def parseToken(self, scope, token):
    """Internal function used to add a token to the view"""
    if token[0] == Token.LINE:
      template = self._outputLine(scope-2, token[1])
    elif token[0] == Token.MULTILINE and token[1] is not None:
      template = self._outputLine(scope, token[1])
    elif token[0] == Token.TEXT:
      template = self._outputLine(scope, "print '" + token[1] + "'")
    elif token[0] == Token.PARENEXPRESSION:
      template = self._outputLine(scope, "print " + token[1])
    elif token[0] == Token.ESCAPED:
      template = self._outputLine(scope, "print '" + token[1] + "'")
    elif token[0] == Token.EXPRESSION:
      template = self._outputLine(scope, "print " + token[1])

  def build(self, debug = False):
    if debug:
      print self.lines

    # Build our code and indent it one
    code = """
def template(self, model=None):
  view = self"""
    code += "\t" + "\n\t".join(self.lines)

    # Compile this code
    if debug:
      print code
    block = compile(code, "view", "exec")
    exec(block)

    # Set the render function to this instance
    self._render = MethodType(template, self)

  def render(self, model=None):
    self.model = model
    self._render(model)
