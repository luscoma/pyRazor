# Alex Lusco

import unittest
from razorview import ViewIO
import logging

class ScopeStackTest(unittest.TestCase):

  def setUp(self):
    self.io = ViewIO()

  def teardown(self):
    self.io.close()

  def testWriteLine(self):
    self.io.writeline("test")
    self.io.writeline("test")
    self.assertEqual("test\ntest\n", self.io.getvalue())

  def testWriteScope(self):
    self.io.setscope(0)
    self.io.writescope("test")

    self.io.setscope(1)
    self.io.writescope("test")

    self.io.setscope(2)
    self.io.writescope("test")
    self.assertEqual("test  test    test", self.io.getvalue())

  def testSetScope(self):
    self.io.setscope(0)
    self.io.scopeline("test")
    self.assertEqual("test\n", self.io.getvalue())

    self.io.setscope(1)
    self.io.scopeline("test")
    self.io.setscope(2)
    self.io.scopeline("test")
    self.assertEqual("test\n  test\n    test\n", self.io.getvalue())

if __name__ == '__main__':
      logging.basicConfig(level=logging.ERROR)
      unittest.main()
