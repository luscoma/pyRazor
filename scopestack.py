# Alex Lusco
# Handles managing the indent stack for multiline tokens

class ScopeStack(object):
  """
  Manages scope based on indentation.
  
  One quirk is that increases in scope are delayed one call to handler.
  This allows the line increasing the scope to be written at the old scope depth.
  In contrast decreases in scope are immediate allowing the new line to be immediately
  written at the decreased scope depth.
  """
  def __init__(self):
    self.scope = 0
    self.indentblock = []
    self.handlers = {}

  def getScope(self):
    """Returns the current scope depth"""
    return scope

  def getIndent(self):
    """Returns the indention value that set the last scope"""
    if len(self.indentblock) == 0:
      return 0
    return self.indentblock[-1]

  def pushCallback(self, scope_callback = None):
    """Pushes a callback onto the scope stack without increasing
       the scope.  This callback will be called when the logical scope
       returns to this indent level.  This does not increase the
       overall scope depth.
    """
    if scope_callback:
      self.handlers[self.getIndent()] = scope_callback

  def pushScope(self):
    """Pushes a scope onto the stack"""
    self.scope += 1

  def handler(self, indent):
    """Handles indention level"""
    if self.scope > len(self.indentblock):
      self.stack.append(indent)

    while len(self.indentblock) > 0 and self.indentblock[-1] >= indent:
      self._tryPopScope(self.indentblock.pop())

    # We have to pop the scope just in case we had a callback
    # at indent 0, very special case, but common.
    self._tryPopScope(indent)
    self.last_indent = indent

  def _tryPopScope(self, scope):
    """Attempts to pop any scope handlers"""
    if self.handlers.has_key(scope):
      self.handlers.pop(scope)()
