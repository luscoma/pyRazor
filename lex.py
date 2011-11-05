# Alex Lusco
import sexylexer
import cgi
from scopestack import ScopeStack

class Token:
  """Simple list of token names"""
  ESCAPED = "ESCAPED"
  COMMENT = "COMMENT"
  LINECOMMENT = "LINECOMMENT"
  ONELINE = "ONELINE"
  MULTILINE = "MULTILINE"
  PARENEXPRESSION = "PARENEXPRESSION"
  EXPRESSION = "EXPRESSION"
  TEXT = "TEXT"
  CODE = "CODE"
  NEWLINE = "NEWLINE"
  INDENT = "INDENT"

def bind(handler):
  """Simple binding function"""
  return lambda scanner, token: handler(scanner, token);

class RazorLexer(object):
  """Encapsulates the razor token logic"""
  @staticmethod
  def create(ignore_whitespace = False):
    """Creates the rules bound to a new lexer instance"""
    lex = RazorLexer(ignore_whitespace)
    lex.rules = (
        (Token.NEWLINE, (r"[\r]?[\n][ \t]*", bind(lex.newline))),
        (Token.ESCAPED, (r"@@", bind(lex.escaped))),
        (Token.COMMENT, (r"@#.*#@", bind(lex.comment))),
        (Token.LINECOMMENT, (r"@#.*$", bind(lex.linecomment))),
        (Token.ONELINE, (r"@(?:import|from|model) .+$", bind(lex.oneline))),
        (Token.MULTILINE, (r"@\w*.*:$", bind(lex.multiline))),
        (Token.PARENEXPRESSION, (r"@!?\(", bind(lex.paren_expression))),
        (Token.EXPRESSION, (r"@!?(\w+(?:(?:\[.+\])|(?:\(.*\)))?(?:\.[a-zA-Z]+(?:(?:\[.+\])|(?:\(.*\)))?)*)", bind(lex.expression))),
        (Token.TEXT, (r"[^@\r\n]+", bind(lex.text))),
    )
    lex.lexer = sexylexer.Lexer(lex.rules)
    return lex

  def __init__(self, ignore_whitespace):
    self.scope = ScopeStack(ignore_whitespace)
    self.ignore_whitespace = ignore_whitespace

  def scan(self, text):
    """Tokenize an input string"""
    if self.ignore_whitespace:
      return self.lexer.scan(text.lstrip())
    return self.lexer.scan(text)

  # Token Parsers
  def shouldEscape(self, token):
    """Returns false if this token should not be html escaped"""
    return token[1] != '!'

  def paren_expression(self, scanner, token):
    """Performs paren matching to find the end of a parenthesis expression"""
    start = scanner._position
    plevel = 1
    end = start
    for c in scanner.input[start:]:
      if plevel == 0:
        # Halt when we close our braces
        break;
      elif c == '(':
        plevel += 1
      elif c == ')':
        plevel -= 1
      elif c == '\n':
        # Halt at new line
        break
      end += 1
    # parse exception
    if plevel != 0:
      raise sexylexer.InvalidTokenError()
    scanner._position = end

    # Our token here is either @!( or @(
    if not self.shouldEscape(token):
      return scanner.input[start:end-1]
    # We wrap the expression in a call to cgi.escape
    return "cgi.escape(str(" + scanner.input[start:end-1] + "))"

  def multiline(self, scanner, token):
    """Handles multiline expressions"""
    if token == "@:":
      #TODO(alusco): Actually implement multiple rules instead of this
      #sketchy situation here.
      scanner.ignoreRules = True
      def pop_multiline():
        scanner.ignoreRules = False
      self.scope.indentstack.markScope(pop_multiline)
      # We have to move past the end of line (this is a special case)
      # $ matches at the end of a line so it should be just +1
      scanner._position += 1
      return None
    else:
      # Convert helper syntax to a real python function
      if token.lower().startswith("@helper"):
        token = token.lower().replace("helper", "def", 1)
      self.scope.enterScope()
      return token[1:]

  def escaped(self, scanner, token):
    """Escapes the @ token directly"""
    return "@"

  def expression(self, scanner, token):
    if not self.shouldEscape(token):
      return token[2:]
    return "cgi.escape(str(" + token[1:] + "))"

  def oneline(self, scanner, token):
    lower_token = token.lower()
    if lower_token.startswith("@model"):
      return "isinstance(model, " + token[token.rindex(' '):] + ")"
    else:
      return token[1:]

  def comment(self, scanner, token):
    """Ignores inline comments returning None"""
    return None

  def linecomment(self, scanner, token):
    """Ignores comments by returning None"""
    # Move the parser past the newline character
    scanner._position += 1
    return None

  def text(self, scanner, token):
    """Returns text escaped with ' escaped"""
    return token.replace("'","\\'")

  def newline(self, scanner, token):
    """Handles indention scope"""
    nline = token.index('\n')+1
    token = token[nline:]
    self.scope.handleIndentation(len(token))
    if self.ignore_whitespace:
      return ""
    return token[self.scope.indentstack.getScopeIndentation():]
