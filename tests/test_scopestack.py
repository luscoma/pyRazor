# Alex Lusco

import unittest
from scopestack import ScopeStack
import logging

STEP = "     "

class CallbackCounter:
  count = 0

class ScopeStackTest(unittest.TestCase):

  def setUp(self):
    self.scope = ScopeStack()

  def testScopeStartsAtZero(self):
    self.assertEqual(0, self.scope.getScope(), "Scope didn't start at zero")

  def testCallback(self):
    """Tests that the scope stack will callback when not in a scope"""
    counter = CallbackCounter()
    def scopeCallback(counter):
      counter.count += 1
    callback = lambda: scopeCallback(counter)

    # Push a callback onto stack
    self.scope.handleIndentation("")
    self.scope.indentstack.markScope(callback)

    # Calls the stack with a deeper indent
    self.scope.handleIndentation(STEP)
    self.assertEqual(0, self.scope.getScope())
    self.assertEqual(0, counter.count)

    # Falls back to the original scope
    self.scope.handleIndentation("")
    self.assertEqual(1, counter.count)

  def testSingleScope(self):
    """Tests that a single scope is registered correctly"""
    self.scope.handleIndentation("")
    self.scope.enterScope()
    self.scope.handleIndentation(STEP)
    self.assertEqual(1, self.scope.getScope())

    self.scope.handleIndentation(2*STEP)
    self.assertEqual(1, self.scope.getScope())

    self.scope.handleIndentation(STEP)
    self.assertEqual(1, self.scope.getScope())

    self.scope.handleIndentation("")
    self.assertEqual(0, self.scope.getScope())

  def testMultiScope(self):
    """Tests a multiscope callback is called correctly"""
    self.scope.handleIndentation("")
    self.assertEqual(0, self.scope.getScope())
    self.scope.enterScope()

    self.scope.handleIndentation(STEP)
    self.assertEqual(1, self.scope.getScope())
    self.scope.enterScope()

    self.scope.handleIndentation(2*STEP)
    self.assertEqual(2, self.scope.getScope())
    self.scope.enterScope()

    self.scope.handleIndentation(2*STEP)
    self.assertEqual(2, self.scope.getScope())

    self.scope.handleIndentation(STEP)
    self.assertEqual(1, self.scope.getScope())

    self.scope.handleIndentation("")
    self.assertEqual(0, self.scope.getScope())

if __name__ == '__main__':
      logging.basicConfig(level=logging.ERROR)
      unittest.main()
