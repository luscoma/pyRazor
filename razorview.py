# Alex Lusco

from lex import Token
from types import MethodType
from StringIO import StringIO

class View(object):
  """A razor view"""
  def __init__(self):
    self.parser = ViewBuilder()

  def parseToken(self, scope, token):
    """Internal function used to add a token to the view"""
    if token[0] == Token.LINE:
      self.parser.writeCode(token[1])
    elif token[0] == Token.MULTILINE and token[1] is not None:
      self.parser.writeCode(token[1])
    elif token[0] == Token.TEXT:
      self.parser.writeText(token[1])
    elif token[0] == Token.PARENEXPRESSION:
      self.parser.writeExpression(token[1])
    elif token[0] == Token.ESCAPED:
      self.parser.writeText(token[1])
    elif token[0] == Token.EXPRESSION:
      self.parser.writeExpression(token[1])
    elif token[0]== Token.INDENT:
      self.parser.handleNewLine(scope)

  def build(self, debug = False):
    # Build our code and indent it one
    code = self.parser.getTemplate()

    # Compile this code
    if debug:
      print code
    block = compile(code, "view", "exec")
    exec(block)

    # Bind the render function to this instance
    self._render = MethodType(template, self)

  def render(self, model=None):
    self.model = model
    self._render(model)

class ViewBuilder(object):
  def __init__(self):
    self.buffer = StringIO()
    self.cache = None
    self.lineHasText = False
    self._writeHeader()
    self.handleNewLine(0)

  def _writeHeader(self):
    """Writes the function header"""
    self.buffer.write("def template(self, model=None):\n")
    self.buffer.write("  view = self")

  def _writeLineLeader(self):
    """Might write the concat symbol depending on state"""
    if self.lineHasText:
      self.buffer.write(" + ")
    else:
      self.lineHasText = True
      # TODO(alusco): Graduate from using print
      self.buffer.write("print ")

  def writeCode(self, code):
    """Writes a line of code to the view buffer"""
    self.buffer.write(code)

  def writeText(self, token):
    """Writes a token to the view buffer"""
    self._writeLineLeader()
    self.buffer.write("'")
    self.buffer.write(token)
    self.buffer.write("'")

  def writeExpression(self, expression):
    """Writes an expression to the current line"""
    self._writeLineLeader()
    self.buffer.write("str(")
    self.buffer.write(expression)
    self.buffer.write(")")

  def handleNewLine(self, scope):
    """Handles a new line"""
    self.buffer.write("\n  ")
    self.buffer.write(" " * scope)
    self.lineHasText = False

  def getTemplate(self):
    if not self.cache:
      self.cache = self.buffer.getvalue()
      self.buffer.close()
    return self.cache
