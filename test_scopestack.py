# Alex Lusco

import unittest
from scopestack import ScopeStack

STEP = 5

class CallbackCounter:
  count = 0

class ScopeStackTest(unittest.TestCase):

  def setUp(self):
    self.scope = ScopeStack()

  def testScopeStartsAtZero(self):
    self.assertEquals(0, self.scope.getScope(), "Scope didn't start at zero")

  def testCallback(self):
    """Tests that the scope stack will callback when not in a scope"""
    counter = CallbackCounter()
    def scopeCallback(counter):
      counter.count += 1
    callback = lambda: scopeCallback(counter)

    # Push a callback onto stack
    self.scope.handleIndentation(0)
    self.scope.indentstack.markScope(callback)

    # Calls the stack with a deeper indent
    self.scope.handleIndentation(STEP)
    self.assertEquals(0, self.scope.getScope())
    self.assertEquals(0, counter.count)

    # Falls back to the original scope
    self.scope.handleIndentation(0)
    self.assertEquals(1, counter.count)

  def testSingleScope(self):
    """Tests that a single scope is registered correctly"""
    self.scope.handleIndentation(0)
    self.scope.enterScope()
    self.scope.handleIndentation(STEP)
    self.assertEquals(1, self.scope.getScope())

    self.scope.handleIndentation(2*STEP)
    self.assertEquals(1, self.scope.getScope())

    self.scope.handleIndentation(STEP)
    self.assertEquals(1, self.scope.getScope())

    self.scope.handleIndentation(0)
    self.assertEquals(0, self.scope.getScope())

  def testMultiScope(self):
    """Tests a multiscope callback is called correctly"""
    self.scope.handleIndentation(0)
    self.assertEquals(0, self.scope.getScope())
    self.scope.enterScope()

    self.scope.handleIndentation(STEP)
    self.assertEquals(1, self.scope.getScope())
    self.scope.enterScope()

    self.scope.handleIndentation(2*STEP)
    self.assertEquals(2, self.scope.getScope())
    self.scope.enterScope()

    self.scope.handleIndentation(2*STEP)
    self.assertEquals(2, self.scope.getScope())

    self.scope.handleIndentation(STEP)
    self.assertEquals(1, self.scope.getScope())

    self.scope.handleIndentation(0)
    self.assertEquals(0, self.scope.getScope())

if __name__ == '__main__':
      unittest.main()
