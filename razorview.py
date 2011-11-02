# Alex Lusco

import cgi
import viewloader
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
    self.parser.parse(scope, token)

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

  def tmpl(self, file, submodel=None):
    tmplModel = submodel if submodel is not None else self.model
    # Render this template into our io
    viewloader.loadfile(file)._render(self.io, tmplModel)

  def wrap(self, file):
    # TODO(alusco): Wrap the template
    raise NotImplementedError("Wraps not implemented yet")

  def section(self, name):
    # TODO(alusco): Output a section
    raise NotImplementedError("Section isn't implemented yet")

  def body(self):
    # TODO(alusco): print out a wrapped body
    raise NotImplementedError("Body isn't implemented yet")

  def render(self, model=None):
    self.model = model
    self.io = StringIO()
    self._render(self.io, model)
    template_data = self.io.getvalue()
    self.io.close()
    return template_data

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
    self.lasttoken = (None,)
    self.buffer.setscope(1)
    self._writeHeader()

  def _writeHeader(self):
    """Writes the function header"""
    # The last line here must not have a trailing \n
    self.buffer.writeline("def template(self, __io, model=None):")
    self.buffer.scopeline("view = self")

  def writeCode(self, code):
    """Writes a line of code to the view buffer"""
    self.buffer.scopeline(code)

  def writeText(self, token):
    """Writes a token to the view buffer"""
    self.maybePrintIndent()
    self.buffer.writescope("__io.write('")
    self.buffer.write(token)
    self.buffer.writeline("')")

  def writeExpression(self, expression):
    """Writes an expression to the current line"""
    self.maybePrintIndent()
    self.buffer.writescope("__io.write(")
    self.buffer.write(expression)
    self.buffer.writeline(")")

  def getTemplate(self):
    """Retrieves the templates text"""
    if not self.cache:
      self.close()
    return self.cache

  def parse(self, scope, token):
    if token[0] == Token.CODE:
      self.writeCode(token[1])
    elif token[0] == Token.MULTILINE:
      self.writeCode(token[1])
    elif token[0] == Token.ONELINE:
      self.writeCode(token[1])
    elif token[0] == Token.TEXT:
      self.writeText(token[1])
    elif token[0] == Token.PARENEXPRESSION:
      self.writeExpression(token[1])
    elif token[0] == Token.ESCAPED:
      self.writeText(token[1])
    elif token[0] == Token.EXPRESSION:
      self.writeExpression(token[1])
    elif token[0]== Token.NEWLINE:
      self.maybePrintNewline()
      self.buffer.setscope(scope+1)

    self.lasttoken = token

  def maybePrintIndent(self):
    """Handles situationally printing indention"""
    if self.lasttoken[0] != Token.NEWLINE:
      return

    # TODO(alusco): remove indentation thats part of the scope
    if len(self.lasttoken[1]) > 0:
      self.buffer.scopeline("__io.write('" + self.lasttoken[1] + "')")

  def maybePrintNewline(self):
    """Handles situationally printing a new line"""
    if self.lasttoken is None:
      return

    print "last"
    print self.lasttoken
    # Anywhere we writecode does not need the new line character
    no_new_line = (Token.CODE, Token.MULTILINE, Token.ONELINE)
    if not self.lasttoken[0] in no_new_line:
      self.buffer.scopeline("__io.write('\\n')")

  def close(self):
    if not self.cache:
      self.cache = self.buffer.getvalue()
      self.buffer.close()
