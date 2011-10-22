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
    return None
  else:
    return token[1:]

def escaped(scanner, token):
  global template
  """Escapes the @ token directly"""
  print_line("print '@'")
  return "@"

def expression(scanner, token):
  return token[1:]

def oneline(scanner, token):
  buzzword = token[:token.index(' ')]
  if buzzword == "model":
    return "IDK"
  else:
    return token[1:]
  return token

def text(scanner, token):
  return token.replace("'","\\'")

def indent_handler(level):
  global template
  indenter.handler(level)

def print_line(template, text):
  global indenter
  template += " " * indenter.getIndent()
  template += text
  template += "\n"
  return template

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

def render(text):
  global template;
  template = ""
  l = sexylexer.Lexer(rules,indent_handler)
  for token in l.scan(text):
    # hacky hacky hacky
    if token[0] == "LINE":
      template = print_line(template, token[1])
    elif token[0] == "MULTILINE" and token[1] is not None:
      template = print_line(template, token[1])
    elif token[0] == "TEXT":
      template = print_line(template, "print '" + token[1] + "'")
    elif token[0] == "PAREN":
      template = print_line(template, "print " + token[1])
    elif token[0] == "ESCAPED":
      template = print_line(template, "print '" + token[1] + "'")
    elif token[0] == "EXPRESSION":
      template = print_line(template, "print " + token[1])

  print template
