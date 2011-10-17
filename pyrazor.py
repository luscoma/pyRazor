# pyRazor.py
# Python Razor Template Implementation

import sexylexer
import re

PAREN_MATCH = re.compile(r"[()\n]", re.MULTILINE)

def paren_expression(scanner, token):
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
  return scanner.input[start-2:end]

# Parsing rules
rules = (
  (r"ESCAPED", r"@@"),
  (r"COMMENT", r"@#.*#@"),
  (r"LINECOMMENT", r"@#.*"),
  (r"ONELINE", r"@(?:import|from|model) .+$"),
  (r"MULTILINE", r"@\w*.*:$"),
  (r"PAREN", (r"@!?\(", paren_expression)),
  (r"EXPRESSION", r"@!?(\w+(?:(?:\[.+\])|(?:\(.*\)))?(?:\.[a-zA-Z]+(?:(?:\[.+\])|(?:\(.*\)))?)*)"),
  (r"TEXT", r"[^@\n]+")
)

# Debug stuff
l = sexylexer.Lexer(rules)
def doScan(text):
  for token in l.scan(text):
    print token
  
