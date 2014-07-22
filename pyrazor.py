__author__ = 'hoseinyeganloo@gmail.com'

import re
import lex
import logging
from razorview import ViewBuilder
from razorview import View

def __Load(name):
    f = open(name)
    view = re.sub("@#.*#@","",f.read(),flags= re.S)
    f.close()
    return view

def __ParseView(text, ignore_whitespace):
    """Creates a razorview from template text.

    Args:
    text: The template text to render
    ignore_whitespace: If true whitespace at the beghning of each line is
    stripped when parsing.
    """
    lexer = lex.RazorLexer.create(ignore_whitespace)
    builder = ViewBuilder(lexer.scope)
    for token in lexer.scan(text):
        #logging.debug('Token scanned: %s', token)
        builder.parse(token)
    return View(builder.Build(), ignore_whitespace)


def Render(text, model=None, ignore_whitespace=False):
    view = __ParseView(text, ignore_whitespace)
    return view.Render(model)


def RenderFile(address, model=None, ignore_whitespace=False):
    view = __ParseView(__Load(address), ignore_whitespace)
    return view.Render(model)

def RenderLayout(address, body, model=None, ignore_whitespace=False):
    view = __ParseView(__Load(address), ignore_whitespace)
    view._body = body
    return view.Render(model)