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
    if token[0] == Token.CODE:
      self.parser.writeCode(token[1])
    elif token[0] == Token.MULTILINE:
      if token[1] is None:
        # This token is more like a flag, nothing is output
        self.parser.skip_new_line = True
      else:
        self.parser.writeCode(token[1])
    elif token[0] == Token.ONELINE:
      self.parser.writeCode(token[1])
    elif token[0] == Token.TEXT:
      self.parser.writeText(token[1])
    elif token[0] == Token.PARENEXPRESSION:
      self.parser.writeExpression(token[1])
    elif token[0] == Token.ESCAPED:
      self.parser.writeText(token[1])
    elif token[0] == Token.EXPRESSION:
      self.parser.writeExpression(token[1])
    elif token[0] == Token.INDENT:
      self.parser.writeText(token[1])
    elif token[0]== Token.NEWLINE:
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

class ViewIO(StringIO):
  """Subclass of StringIO which can write a line"""

  def __init__(self):
    StringIO.__init__(self)
    self.scope = 0

  def setscope(self, scope):
    self.scope = scope

  def __writescope(self):
    self.write("  " * self.scope)

  def writescope(self, text):
    """Writes the text prepending the scope"""
    self.__writescope()
    self.write(text)

  def scopeline(self, text):
    """Writes a line of text prepending the scope"""
    self.__writescope()
    self.writeline(text)

  def writeline(self, text):
    """Writes the text followed by a \n if needed"""
    self.write(text)
    if text[-1] != '\n':
      self.write('\n')

class ViewBuilder(object):
  def __init__(self):
    self.buffer = ViewIO()
    self.cache = None
    self.skip_new_line = False
    self.buffer.setscope(1)
    self._writeHeader()

  def _writeHeader(self):
    """Writes the function header"""
    # The last line here must not have a trailing \n
    self.buffer.writeline("def template(self, model=None):")
    self.buffer.scopeline("view = self")
    self.buffer.scopeline("__io = StringIO()")

  def writeCode(self, code):
    """Writes a line of code to the view buffer"""
    self.buffer.scopeline(code)
    self.skip_new_line = True

  def writeText(self, token):
    """Writes a token to the view buffer"""
    self.buffer.writescope("__io.write('")
    self.buffer.write(token)
    self.buffer.writeline("')")

  def writeExpression(self, expression):
    """Writes an expression to the current line"""
    self.buffer.writescope("__io.write(")
    self.buffer.write(expression)
    self.buffer.writeline(")")

  def getTemplate(self):
    """Retrieves the templates text"""
    if not self.cache:
      self.close()
    return self.cache

  def handleNewLine(self, scope):
    """Handles a new line"""
    if not self.skip_new_line:
      self.buffer.scopeline("__io.write('\\n')")
    else:
      self.skip_new_line = False
    # Sets the scope (our minimum scope is 1)
    self.buffer.setscope(scope+1)

  def close(self):
    if not self.cache:
      self.buffer.scopeline("__out = __io.getvalue()")
      self.buffer.scopeline("__io.close()")
      self.buffer.scopeline("return __out")
      self.cache = self.buffer.getvalue()
      self.buffer.close()
