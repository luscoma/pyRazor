# pyRazor.py
# Python Razor Template Implementation

import sexylexer
import re
from indentstack import IndentStack

indenter = IndentStack()
template = ""

def paren_expression(scanner, token):
  global template
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
  print_line("print '" + scanner.input[start:end-1] + "'")
  return scanner.input[start-2:end]

def multiline(scanner, token):
  global template
  """Handles multiline expressions"""
  if token == "@:":
    scanner.ignoreRules = True
    def pop_multiline():
      scanner.ignoreRules = False
    indenter.registerScopeListener(pop_multiline)
    #TODO(alusco): Handle this case
  else:
    print_line(token[1:])
  return token

def escaped(scanner, token):
  global template
  """Escapes the @ token directly"""
  print_line("print '@'")
  return "@"

def expression(scanner, token):
  global template
  print_line("print " + token[1:])
  return token

def oneline(scanner, token):
  global template
  buzzword = token[:token.index(' ')]
  if buzzword == "model":
    print_line("print '# Model'")
  else:
    # Other One Line
    print_line(token[1:])
  return token

def text(scanner, token):
  global template
  print_line("print '" + token.replace("'","\\'") + "'")
  return token

def indent_handler(level):
  global template
  indenter.handler(level)

def print_line(text):
  global indenter
  global template
  template += " " * indenter.getIndent()
  template += text
  template += "\n"

# Parsing rules
rules = (
  (r"ESCAPED", (r"@@", escaped)),
  (r"COMMENT", r"@#.*#@"),
  (r"LINECOMMENT", r"@#.*"),
  (r"ONELINE", (r"@(?:import|from|model) .+$", oneline)),
  (r"MULTILINE", (r"@\w*.*:$", multiline)),
  (r"PAREN", (r"@!?\(", paren_expression)),
  (r"EXPRESSION", (r"@!?(\w+(?:(?:\[.+\])|(?:\(.*\)))?(?:\.[a-zA-Z]+(?:(?:\[.+\])|(?:\(.*\)))?)*)", expression)),
  (r"TEXT", (r"[^@\n]+", text))
)

class View(object):
  """A base razor view class.  All razor templates inherit from this class"""
  pass

def render(text):
  global template;
  template = ""
  l = sexylexer.Lexer(rules,indent_handler)
  for token in l.scan(text):
    pass
  print template
