# Alex Lusco
# Handles managing the indent stack for multiline tokens

class IndentStack(object):
  """
  Handles indention, tracking python scope by block.  Important points are marked so that 
  they can be referenced later to determine the appropriate level of indention.

  @param nowhitespace  causes getRelativeIndentation to always return 0
  """
  def __init__(self, nowhitespace = False):
    self._nowhitespace = nowhitespace
    # Indentation Tracking
    self.stack = []
    self.indentation = 0
    # Handler Tracking
    self.handlers = {}
    # Mark
    self.markHandler = None
    self.mark = False

  def markScope(self, handler = None):
    """Marks the next indent level as a scope boundary"""
    self.mark = True
    self.markHandler = handler

  def getScopeIndentation(self):
    """Returns the level of indentation for the this scope"""
    if len(self.stack) > 0:
      return self.stack[-1]
    return ['', 0]

  def getRelativeIndentation(self):
    """Returns the relative indent of this line relative to its scope"""
    if not self._nowhitespace:
      return self.indentation - self.getScopeIndentation()
    else:
      return 0

  def handleIndentation(self, indent):
    """Updates the current indention level"""
    il = len(indent)
    self._popIndentation(il)
    if self.mark:
      self._pushIndentation(indent, il)
      self.mark = False
    self.indentation = il

  def _popIndentation(self, indent):
    """Tries to pop any indents greater than this one"""
    # Pop any indents higher than our current level
    while len(self.stack) > 0 and self.stack[-1][1] > indent:
      self._tryPopHandler(self.stack.pop()[1])

  def _tryPopHandler(self, indent):
    """Attempts to pop any scope handlers"""
    if indent in self.handlers:
      self.handlers.pop(indent)()

  def _pushIndentation(self, indent, il):
    """Pushes this identation onto the stack"""
    # Check if we need to push this indent on the stack
    if il > self.getScopeIndentation()[1]:
      self.stack.append((indent, il))
      self.handlers[il] = self.markHandler
    elif self.markHandler is not None:
      # This was a case where a multiline token has no 
      self.markHandler()


class ScopeStack(object):
  """
  Manages scope based on tokens on top of an indentstack.
  The indentstack will track underlying scope indent and
  can be used to determine indentation levels for output.
  """
  def __init__(self, nowhitespace = False):
    self.scope = 0
    self.indentstack = IndentStack(nowhitespace)

  def getScope(self):
    """Returns the current scope depth"""
    return self.scope

  def enterScope(self):
    """Enters a new scope level"""
    def _leaveScope():
      self.scope -= 1
    self.scope += 1
    self.indentstack.markScope(_leaveScope)

  def handleIndentation(self, indent):
    """Handles indention level"""
    self.indentstack.handleIndentation(indent)

