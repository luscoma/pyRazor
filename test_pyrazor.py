# Alex Lusco
"""
  Unit tests which just shotgun a bunch of templates
  at the problem and make sure they render correctly.
"""

import unittest
import pyrazor
import cgi
import tempfile
import os

class RenderTests(unittest.TestCase):

  def testSimple(self):
    """Tests a simple rendering case."""
    template = "test"
    self.assertEquals(template, pyrazor.render(template))

  def testIgnoreMultiline(self):
    """Tests that the @: does not affect output."""
    self.assertEquals("", pyrazor.render("@:\n\ta=3"))

  def testSimpleModel(self): 
    class test:
      pass

    model = test()
    model.a = 3
    model.b = 5
    self.assertEquals("3", pyrazor.render("@model.a", model))
    self.assertEquals("3 5", pyrazor.render("@model.a @model.b", model))
    self.assertEquals("8", pyrazor.render("@(model.a + model.b)", model))

  def testModelInstaceOf(self):
    m = dict()
    m['test'] = 3
    self.assertEquals("3", pyrazor.render("@model dict\n@model['test']", m))

  def testModelSubclassOf(self):
    class subdict(dict):
      pass
    m = subdict()
    m['test'] = 3
    self.assertEquals("3", pyrazor.render("@model dict\n@model['test']", m))

  def testHtmlEscape(self):
    class test:
      pass

    model = test()
    model.a = "<html>"
    self.assertEquals("<html>", pyrazor.render("@!model.a", model))
    self.assertEquals(cgi.escape("<html>"), pyrazor.render("@model.a", model))
    self.assertEquals("<html>", pyrazor.render("@!(model.a)", model))
    self.assertEquals(cgi.escape("<html>"), pyrazor.render("@(model.a)", model))
  def testHtml(self):
    html = """<html>
  <head>
    <title>Alex</title>
  </head>
  <body>
    <span>Alex</span>
  </body>
</html>"""
    self.assertEquals(html, pyrazor.render(html))

  def testIgnoreWhitespace(self):
    """Tests that ignoring whitespace will strip all tab/spaces prefix on a line"""
    self.assertEquals("test\ntest", pyrazor.render("test\n\ttest", ignore_whitespace=True))
    self.assertEquals("test", pyrazor.render("  test", ignore_whitespace=True))
    self.assertEquals("test", pyrazor.render("\t test", ignore_whitespace=True))
    self.assertEquals("test\ntest", pyrazor.render("\t test\n\t\ttest", ignore_whitespace=True))

  def testCommentIgnored(self):
    self.assertEquals("<html></html>", pyrazor.render("<html>@# Comment! #@</html>"))
    self.assertEquals("<html>\n</html>", pyrazor.render("<html>\n@#A whole line is commented!\n</html>"))

  def testHelperFunction(self):
    self.assertEquals("viewtext\n<s>helper</s>\nviewtext", pyrazor.render("@helper test(name):\n\t<s>@name</s>\nviewtext\n@test('helper')\nviewtext"))

  def testMultilineIf(self):
    """Tests that an if statement works"""
    # The renderer will output True\n and False\n due to new line chars.... theres currently no good way around this.
    # Though it's not really a huge issue except when testing for an exact match.
    template = "@if model:\n\tTrue\n@else:\n\tFalse"
    self.assertEquals("True\n", pyrazor.render(template, True)) 
    self.assertEquals("False", pyrazor.render(template, False)) 

  def testTmpl(self):
    """Tests that the tmpl directive renders correctly"""
    class model:
      pass

    tmpl_file = RenderTests.__writeTemplateToFile("Test")
    try:
      template = '@view.tmpl("' + tmpl_file + '")'
      self.assertEquals("Test", pyrazor.render(template))
    finally:
      os.remove(tmpl_file)

    tmpl_file = RenderTests.__writeTemplateToFile("<head>\n\t@model.title\n</head>")
    try:
      template = '@view.tmpl("' + tmpl_file + '")'
      m = model()
      m.title = "test"
      self.assertEquals("<head>\n\ttest\n</head>", pyrazor.render(template, m))
    finally:
      os.remove(tmpl_file)

    # Tests that we pass the appropriate part of a model
    tmpl_file = RenderTests.__writeTemplateToFile("<head>\n\t@model.title\n</head>")
    try:
      template = '@model.title\n@view.tmpl("' + tmpl_file + '", model.sub)'
      m = model()
      m.title = "Top title"
      m.sub = model()
      m.sub.title = "Sub Title"
      self.assertEquals("Top title\n<head>\n\tSub Title\n</head>", pyrazor.render(template, m))
    finally:
      os.remove(tmpl_file)

  @staticmethod
  def __writeTemplateToFile(template):
    """Writes a template out to a temporary file.  
       The file is closed and the file name returned.

       The file is automatically deleted if an exception occurs
    """
    file = tempfile.NamedTemporaryFile(delete = False)
    path = file.name
    try:
      file.write(template)
      file.close()
      return path
    except:
      os.remove(path)
      raise

if __name__ == '__main__':
      unittest.main()

