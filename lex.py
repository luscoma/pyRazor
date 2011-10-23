# Alex Lusco
import sexylexer
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
  LINE = "LINE"

def bind(handler):
  """Simple binding function"""
  return lambda scanner, token: handler(scanner, token);

class RazorLexer(object):
  """Encapsulates the razor token logic"""
  @staticmethod
  def create():
    """Creates the rules bound to a new lexer instance"""
    lex = RazorLexer()
    lex.rules = (
        (Token.ESCAPED, (r"@@", bind(lex.escaped))),
        (Token.COMMENT, r"@#.*#@"),
        (Token.LINECOMMENT, r"@#.*"),
        (Token.ONELINE, (r"@(?:import|from|model) .+$", bind(lex.oneline))),
        (Token.MULTILINE, (r"@\w*.*:$", bind(lex.multiline))),
        (Token.PARENEXPRESSION, (r"@!?\(", bind(lex.paren_expression))),
        (Token.EXPRESSION, (r"@!?(\w+(?:(?:\[.+\])|(?:\(.*\)))?(?:\.[a-zA-Z]+(?:(?:\[.+\])|(?:\(.*\)))?)*)", bind(lex.expression))),
        (Token.TEXT, (r"[^@\n]+", bind(lex.text)))
    )
    lex.lexer = sexylexer.Lexer(lex.rules, lambda level: lex.indent_handler(level))
    return lex

  def __init__(self):
    # Track Indention
    self.scope = ScopeStack()

  def scan(self, text):
    """Tokenize an input string"""
    return self.lexer.scan(text)

  def getScope(self):
    """Returns the current indention level"""
    return self.scope.getScope()

  # Token Parsers
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
    return scanner.input[start:end-1]

  def multiline(self, scanner, token):
    """Handles multiline expressions"""
    if token == "@:":
      #TODO(alusco): Actually implement multiple rules instead of this
      #sketchy situation here.
      scanner.ignoreRules = True
      def pop_multiline():
        print "Popped"
        scanner.ignoreRules = False
      #TODO(alusco): Handle this case
      self.scope.pushCallback(pop_multiline)
      return None
    else:
      self.scope.pushScope()
      return token[1:]

  def escaped(self, scanner, token):
    """Escapes the @ token directly"""
    return "@"

  def expression(self, scanner, token):
    return token[1:]

  def oneline(self, scanner, token):
    buzzword = token[:token.index(' ')]
    if buzzword == "model":
      # TODO(alusco): implement model stuff
      return "IDK"
    else:
      return token[1:]

  def text(self, scanner, token):
    return token.replace("'","\\'")

  def indent_handler(self, level):
    self.scope.handler(level)
