# Based off the lexer implementation available at
# http://www.evanfosmark.com/2009/02/sexy-lexing-with-python/

import re

class TokenError(Exception):
  """A base exception for use in desginated that an error ocurred
     when parsing.
  """
  def __init__(self, token, lineno):
    self.token = token
    self.lineno = lineno

  def __str__(self):
    return "Line #%s, Found token: %s" % (self.lineno, self.token)

class InvalidTokenError(TokenError):
  """This exception is for use by parsing functions to designate an
     error has occurred when parsing out a token.  When thrown within
     a parsing function it will be caught by the parser and rethrown
     with lineno and the matched portion of the token.
  """
  def __init__(self, token = None, lineno = None):
    """A constructor that can be used by callbacks to signify an
       error.  This will be caught and reraised with position and
       line number information"""
    TokenError.__init__(self, token, lineno)

class UnknownTokenError(TokenError):
  """ This exception is for use to be thrown when an unknown token is
      encountered in the token stream. It holds the line number and the
      offending token.
  """
  pass

class ScannerMode:
    Text = "TEXT"
    CODE = "CODE"

class _InputScanner(object):
  """ This class manages the scanning of a specific input. An instance of it is
      returned when scan() is called. It is built to be great for iteration. This is
      mainly to be used by the Lexer and ideally not directly.
  """

  def __init__(self, lexer, input):
    """ Put the lexer into this instance so the callbacks can reference it 
        if needed.
    """
    self._position = 0
    self.lexer = lexer
    self.input = input
    self.Mode = ScannerMode.Text


  def __iter__(self):
    """ All of the code for iteration is controlled by the class itself.
        This and next() (or __next__() in Python 3.0) are so syntax
        like `for token in Lexer(...):` is valid and works.
    """
    return self

  def __next__(self):
    value = self._next()
    while value[1] is None:
      value = self._next()
    return value


  def _next(self):
    if not self.done_scanning():
      return self.scan_next()
    raise StopIteration

  def done_scanning(self):
    """ A simple boolean function that returns true if scanning is
        complete and false if it isn't.
    """
    return self._position >= len(self.input)

  def scan_next(self):
    """ Retreive the next token from the input. If the
        flag `omit_whitespace` is set to True, then it will
        skip over the whitespace characters present.
    """
    if self.done_scanning():
        return None

    # Try to match a token
    if self.Mode == ScannerMode.CODE:
      match = self.lexer.regex_line.match(self.input, self._position)
    else:
      match = self.lexer.regexc.match(self.input, self._position)

    if match is None:
      lineno = self.input[:self._position].count("\n") + 1
      raise UnknownTokenError(self.input[self._position], lineno)

    self._position = match.end()
    value = match.group(match.lastgroup)

    # Callback
    if match.lastgroup in self.lexer._callbacks:
      try:
        value = self.lexer._callbacks[match.lastgroup](self, value)
      except InvalidTokenError:
        # raise with some actual information
        lineno = self.input[:self._position].count("\n") + 1
        raise InvalidTokenError(self.input[self._position], lineno)
    return match.lastgroup, value

class Lexer(object):
  """ A lexical scanner. It takes in an input and a set of rules based
      on reqular expressions. It then scans the input and returns the
      tokens one-by-one. It is meant to be used through iterating.
  """

  def __init__(self, rules, mrules, case_sensitive=False):
    """ Set up the lexical scanner. Build and compile the regular expression
        and prepare the whitespace searcher.
    """
    self._callbacks = {}
    self.case_sensitive = case_sensitive
    parts = []
    mparts = []
    for name, rule in rules:
      if not isinstance(rule, str):
        rule, callback = rule
        self._callbacks[name] = callback
      parts.append("(?P<%s>%s)" % (name, rule))

    for name, mrule in mrules:
      if not isinstance(mrule, str):
        mrule, callback = mrule
        self._callbacks[name] = callback
      mparts.append("(?P<%s>%s)" % (name, mrule))

    if self.case_sensitive:
      flags = re.M
    else:
      flags = re.M|re.I

    self.regex_line = re.compile("|".join(mparts), flags)
    self.regexc = re.compile("|".join(parts), flags)

  def scan(self, input):
    """ Return a scanner built for matching through the `input` field. 
        The scanner that it returns is built well for iterating.
    """
    return _InputScanner(self, input)
