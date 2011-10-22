# pyRazor.py
# Python Razor Template Implementation

from lex import RazorLexer, Token

def print_line(lexer, template, text):
  template += " " * lexer.getIndent()
  template += text
  template += "\n"
  return template

def render(text):
  global template;
  template = ""
  lex = RazorLexer.create();
  for token in lex.scan(text):
    # hacky hacky hacky
    if token[0] == "LINE":
      template = print_line(lex, template, token[1])
    elif token[0] == "MULTILINE" and token[1] is not None:
      template = print_line(lex, template, token[1])
    elif token[0] == "TEXT":
      template = print_line(lex, template, "print '" + token[1] + "'")
    elif token[0] == "PAREN":
      template = print_line(lex, template, "print " + token[1])
    elif token[0] == "ESCAPED":
      template = print_line(lex, template, "print '" + token[1] + "'")
    elif token[0] == "EXPRESSION":
      template = print_line(lex, template, "print " + token[1])

  print template
