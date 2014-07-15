# Alex Lusco

import cgi
import logging

import lex
import types

from ViewLoader import ViewLoader

from lex import Token
from io import StringIO

  
def ParseView(text, ignore_whitespace):
  """Creates a razorview from template text.

  Args:
    text: The template text to render
    ignore_whitespace: If true whitespace at the beghning of each line is
        stripped when parsing.
  """
  lexer = lex.RazorLexer.create(ignore_whitespace)
  builder = ViewBuilder(lexer.scope)
  for token in lexer.scan(text):
    logging.debug('Token scanned: %s', token)
    builder.parse(token)
  return View(builder, ignore_whitespace)


class View(object):
  """A razor view"""
  
  def __init__(self, builder, ignore_whitespace):
    self.renderer = types.MethodType(builder.Build(), self)
    self.ignore_whitespace = ignore_whitespace
    self._tmplFile = None
    self._tmplModel = None
    self._value = ''
    self._body = ''
    self._Section = dict()

  def Render(self, model=None):
    io = StringIO()
    self.RenderTo(io, model)
    self._value = io.getvalue()
    io.close()
    if(self._tmplFile != None):
        view = ParseView(ViewLoader.Load(self._tmplFile), self.ignore_whitespace)
        self._value = view._tmplRender(self._value,self._tmplModel)
    return self._value

  def _tmplRender(self,body,model=None):
      """ Render view as a template(layout). this method enables body method! """
      self._body = body
      return self.Render(model)

  def RenderTo(self, io, model=None):
    self.model = model
    self.io = io
    self.renderer(self.io, model)

  ## Methods below here are expected to be called from within the template
  def tmpl(self, file, submodel=None):
    self._tmplModel = submodel if submodel is not None else self.model
    self._tmplFile = file

  def wrap(self, file, submodel=None):
    chModel = submodel if submodel is not None else self.model
    view = ParseView(ViewLoader.Load(file), self.ignore_whitespace)
    view.RenderTo(self.io,chModel)

  def section(self, name):
    # TODO(alusco): Output a section
    raise NotImplementedError("Section isn't implemented yet")

  def body(self):
    self.io.write(self._body)



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

  def __init__(self, scope):
    self.buffer = ViewIO()
    self.cache = None
    self.lasttoken = (None,)
    self.scope = scope
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
    self.buffer.writescope("__e = ")
    self.buffer.writeline(expression)
    self.buffer.scopeline("if __e != 'None':")
    self.buffer.scope += 1
    self.buffer.scopeline("__io.write(__e)")
    # We rely on a hack in maybePrintNewline to determine
    # that the last token was an expression and to output the \n at scope+1
    self.buffer.scope -= 1

  def getTemplate(self):
    """Retrieves the templates text"""
    if not self.cache:
      self.close()
    return self.cache

  def parse(self, token):
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
      self.buffer.setscope(self.scope.getScope()+1)

    self.lasttoken = token

  def maybePrintIndent(self):
    """Handles situationally printing indention"""
    if self.lasttoken[0] != Token.NEWLINE:
      return

    if len(self.lasttoken[1]) > 0:
      self.buffer.scopeline("__io.write('" + self.lasttoken[1] + "')")

  def maybePrintNewline(self):
    """Handles situationally printing a new line"""
    if self.lasttoken is None:
      return

    # Anywhere we writecode does not need the new line character
    no_new_line = (Token.CODE, Token.MULTILINE, Token.ONELINE)
    up_scope = (Token.EXPRESSION, Token.PARENEXPRESSION)
    if not self.lasttoken[0] in no_new_line:
      if self.lasttoken[0] in up_scope:
        self.buffer.scope += 1
      self.buffer.scopeline("__io.write('\\n')")
      if self.lasttoken[0] in up_scope:
        self.buffer.scope -= 1

  def close(self):
    if not self.cache:
      self.cache = self.buffer.getvalue()
      self.buffer.close()

  def Build(self):
    # Build our code and indent it one
    code = self.getTemplate()

    # Compile this code
    logging.debug('Parsed code: %s', code)
    block = compile(code, "view", "exec")
    exec(block,globals(),locals())

    # Builds a method which can render a template
    return locals()['template']
