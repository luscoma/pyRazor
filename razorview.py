# Alex Lusco

from lex import Token
from types import MethodType
from StringIO import StringIO

class View(object):
  """A razor view"""
  def __init__(self):
    self.parser = ViewBuilder()
    # TODO(alusco): Make this settable
    self.keepNewLines = True

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
    return self._render(model)

class ViewBuilder(object):
  def __init__(self):
    self.buffer = StringIO()
    self.cache = None
    # TODO(alusco): This should be configurable
    self.stripWhitespace = False

    self._writeHeader()
    self._writeScope(0)

  def _writeHeader(self):
    """Writes the function header"""
    # The last line here must not have a trailing \n
    self.buffer.write("def template(self, model=None):\n")
    self.buffer.write("  view = self\n")
    self.buffer.write("  __io = StringIO()")

  def writeCode(self, code):
    """Writes a line of code to the view buffer"""
    self.buffer.write(code)

  def writeText(self, token):
    """Writes a token to the view buffer"""
    self.buffer.write("__io.write('")
    self.buffer.write(token)
    self.buffer.write("')")

  def writeExpression(self, expression):
    """Writes an expression to the current line"""
    self.buffer.write("__io.write(")
    self.buffer.write(expression)
    self.buffer.write(")")

  def getTemplate(self):
    """Retrieves the templates text"""
    if not self.cache:
      self.close()
    return self.cache

  def _writeScope(self, scope):
    self.buffer.write("\n  ")
    self.buffer.write(" " * scope)

  def handleNewLine(self, scope):
    """Handles a new line"""
    if not self.stripWhitespace:
      self._writeScope(scope)
      self.buffer.write("__io.write('\\n')")
    self._writeScope(scope)

  def close(self):
    if not self.cache:
      self.buffer.write("\n  __out = __io.getvalue()\n")
      self.buffer.write("  __io.close()\n")
      self.buffer.write("  return __out")
      self.cache = self.buffer.getvalue()
      self.buffer.close()
