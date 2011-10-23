# Alex Lusco
# Handles managing the indent stack for multiline tokens

class ScopeStack(object):
  def __init__(self):
    self.stack = []
    self.handlers = {}
    self.last_indent = 0

  def getScope(self):
    return len(self.stack)

  def pushCallback(self, scope_callback = None):
    """Pushes a callback onto the scope stack without increasing
       the scope.  This callback will be called when the logical scope
       returns to this indent level.  This does not increase the
       overall scope depth.
    """
    if scope_callback:
      self.handlers[self.last_indent] = scope_callback

  def pushScope(self, scope_callback = None):
    """Pushes a scope onto the stack"""
    self.pushCallback(scope_callback)
    self.stack.append(self.last_indent)

  def handler(self, indent):
    """Handles indention level"""
    while len(self.stack) > 0 and self.stack[-1] >= indent:
      self.stack.pop()
      scope = len(self.stack)
      self._tryPopScope(scope)

    # We have to pop the scope just in case we had a callback
    # at indent 0, very special case, but common.
    self._tryPopScope(indent)
    self.last_indent = indent

  def _tryPopScope(self, scope):
    """Attempts to pop any scope handlers"""
    if self.handlers.has_key(scope):
      self.handlers.pop(scope)()
