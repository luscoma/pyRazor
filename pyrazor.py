# pyRazor.py
# Python Razor Template Implementation

import sexylexer
import re

PAREN_MATCH = re.compile(r"[()\n]", re.MULTILINE)

def paren_expression(scanner, token):
  """Performs paren matching to find the end of a parenthesis expression"""
  start = scanner._position
  match = PAREN_MATCH.search(scanner.input, start)
  plevel = 1
  end = 0
  while match is not None:
    if match.group() == "(":
      plevel += 1
    elif match.group() == ")":
      plevel -= 1
    else:
      # halt at new line
      break
    end = match.end()
    match = PAREN_MATCH.search(scanner.input, end+1)
  # parse exception
  if plevel != 0:
    print "parse exception"
  scanner._position = end
  return scanner.input[start-2:end]

# Parsing rules
rules = (
  (r"ESCAPED", r"@@"),
  (r"COMMENT", r"@#.*#@"),
  (r"LINECOMMENT", r"@#.*"),
  (r"MULTILINE", r"@\w*.*:$"),
  (r"PAREN", (r"@!?\(", paren_expression)),
  (r"EXPRESSION", r"@!?(\w+(?:(?:\[.+\])|(?:\(.*\)))?(?:\.[a-zA-Z]+(?:(?:\[.+\])|(?:\(.*\)))?)?)"),
  (r"TEXT", r"[^@\n]+")
)

# Debug stuff
l = sexylexer.Lexer(rules)
def doScan(text):
  for token in text:
    print token
  
