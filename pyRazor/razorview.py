# Alex Lusco

import html
import logging
import re
import types
from pyRazor import lex
import hashlib
import os

from io import StringIO


class View(object):
  """A razor view"""
  
  def __init__(self, builder, ignore_whitespace):
    self.renderer = types.MethodType(builder, self)
    self.ignore_whitespace = ignore_whitespace
    self.__layout = None
    self.__layoutModel = None
    self._value = ''
    self._body = ''
    self._Section = dict()

  def Render(self, model=None):
    io = StringIO()
    self.RenderTo(io, model)
    self._value = io.getvalue()
    io.close()
    if(self.__layout != None):
        self._value = pyRazor.RenderLayout(self.__layout, self._value, self.__layoutModel, self.ignore_whitespace)
    return self._value

  def RenderTo(self, io, model=None):
    self.model = model
    self.io = io
    self.renderer(self.io, model)

  ## Methods below here are expected to be called from within the template
  def tmpl(self, file, submodel=None):
    chModel = submodel if submodel is not None else self.model
    view = pyRazor.RenderFile(file, chModel, self.ignore_whitespace)
    self.io.write(view)

  def wrap(self, file, submodel=None):
    self.__layoutModel = submodel if submodel is not None else self.model
    self.__layout = file

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
    self.buffer.scopeline(code.lstrip(' \t'))

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
    self.buffer.scopeline("if __e != None and __e != 'None':")
    self.buffer.scope += 1
    self.buffer.scopeline("__io.write(str(__e))")
    # We rely on a hack in maybePrintNewline to determine
    # that the last token was an expression and to output the \n at scope+1
    self.buffer.scope -= 1

  def getTemplate(self):
    """Retrieves the templates text"""
    if not self.cache:
      self.close()
    return self.cache

  def parse(self, token):
    if token[0] == lex.Token.CODE:
      self.writeCode(token[1])
    elif token[0] == lex.Token.MULTILINE:
      self.writeCode(token[1])
    elif token[0] == lex.Token.ONELINE:
      self.writeCode(token[1])
    elif token[0] == lex.Token.TEXT:
      self.writeText(token[1])
    elif token[0] == lex.Token.PRINTLINE:
      self.writeText(token[1])
    elif token[0] == lex.Token.XMLFULLSTART:
      self.writeText(token[1])
    elif token[0] == lex.Token.XMLSTART:
      self.writeText(token[1])
    elif token[0] == lex.Token.XMLEND:
      self.writeText(token[1])
    elif token[0] == lex.Token.XMLSELFCLOSE:
      self.writeText(token[1])
    elif token[0] == lex.Token.PARENEXPRESSION:
      self.writeExpression(token[1])
    elif token[0] == lex.Token.ESCAPED:
      self.writeText(token[1])
    elif token[0] == lex.Token.EXPRESSION:
      self.writeExpression(token[1])
    elif token[0]== lex.Token.NEWLINE:
      self.maybePrintNewline()
      self.buffer.setscope(self.scope.getScope()+1)

    self.lasttoken = token

  def maybePrintIndent(self):
    """Handles situationally printing indention"""
    if self.lasttoken[0] != lex.Token.NEWLINE:
      return

    if len(self.lasttoken[1]) > 0:
      self.buffer.scopeline("__io.write('" + self.lasttoken[1] + "')")

  def maybePrintNewline(self):
    """Handles situationally printing a new line"""
    if self.lasttoken is None:
      return

    # Anywhere we writecode does not need the new line character
    no_new_line = (lex.Token.CODE, lex.Token.MULTILINE, lex.Token.ONELINE)
    up_scope = (lex.Token.EXPRESSION, lex.Token.PARENEXPRESSION)
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


class pyRazor:
    __mem = dict()
    ViewRoot = [""]

    @staticmethod
    def __Load(name):
        for path in pyRazor.ViewRoot:
            p = os.path.join(path, name)
            if os.path.exists(p):
                f = open(p)
                view = f.read()
                f.close()
                return view
        error = ""
        for path in pyRazor.ViewRoot:
            error += os.path.join(path, name) + " -->  Not Found!\r\n"
        raise FileNotFoundError(error)



    @staticmethod
    def __ParseView(text, ignore_whitespace):
        text = re.sub("@#.*#@", "", text, flags=re.S)
        lexer = lex.RazorLexer.create(ignore_whitespace)
        builder = ViewBuilder(lexer.scope)
        for token in lexer.scan(text):
            builder.parse(token)
        return builder.Build()

    @staticmethod
    def __GetView(name, ignore_whitespace):
        if name not in pyRazor.__mem.keys():
            pyRazor.__mem[name] = pyRazor.__ParseView(pyRazor.__Load(name), ignore_whitespace)
        return View(pyRazor.__mem[name], ignore_whitespace)

    @staticmethod
    def Render(text, model=None, ignore_whitespace=False):
        key = hashlib.md5(text.encode('utf-8')).hexdigest()
        if str(key) not in pyRazor.__mem.keys():
            pyRazor.__mem[key] = pyRazor.__ParseView(text, ignore_whitespace)
        return View(pyRazor.__mem[key], ignore_whitespace).Render(model)


    @staticmethod
    def RenderFile(address, model=None, ignore_whitespace=False):
        view = pyRazor.__GetView(address,ignore_whitespace)
        return view.Render(model)

    @staticmethod
    def RenderLayout(address, body, model=None, ignore_whitespace=False):
        view = pyRazor.__GetView(address,ignore_whitespace)
        view._body = body
        return view.Render(model)