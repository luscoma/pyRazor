# Alex Lusco
# Handles managing the indent stack for multiline tokens

class IndentStack(object):
  def __init__(self):
    self.stack = [0]
    self.handlers = {}

  def popIndention(self, level):
    """Pops down the indention levels and calls handler until we reach a sane place in the stack"""
    while len(self.stack) > 0 and self.stack[-1] >= level:
      scope = self.stack.pop()
      if self.handlers.has_key(scope):
        self.handlers.pop(scope)()
    self.stack.append(level)

  def getIndent(self):
    return self.stack[-1]
  
  def registerScopeListener(self, listener):
    """Registers a scope listener that will be called back when this scope is exited.
    
       The registered listener will effectivly be called back as soon as this same
       level or less of indentation.
    """
    self.handlers[self.stack[-1]] = listener

  def handler(self, level):
    """Handles indentenion level updates pushing new levels onto the scope"""
    if level > self.stack[-1]:
      self.stack.append(level)
    elif level < self.stack[-1]:
      self.popIndention(level)
