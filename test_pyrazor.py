# Alex Lusco
"""
  Unit tests which just shotgun a bunch of templates
  at the problem and make sure they render correctly.
"""

import unittest
import pyrazor
import cgi
import tempfile
import textwrap
import os

class RenderTests(unittest.TestCase):

  def testSimple(self):
    """Tests a simple rendering case."""
    template = "test"
    self.assertEquals(template, pyrazor.Render(template))

  def testIgnoreMultiline(self):
    """Tests that the @: does not affect output."""
    self.assertEquals("", pyrazor.Render("@:\n\ta=3"))

  def testSimpleModel(self): 
    class test:
      pass

    model = test()
    model.a = 3
    model.b = 5
    self.assertEquals("3", pyrazor.Render("@model.a", model))
    self.assertEquals("3 5", pyrazor.Render("@model.a @model.b", model))
    self.assertEquals("8", pyrazor.Render("@(model.a + model.b)", model))

  def testModelInstaceOf(self):
    m = dict()
    m['test'] = 3
    self.assertEquals("3", pyrazor.Render("@model dict\n@model['test']", m))

  def testModelSubclassOf(self):
    class subdict(dict):
      pass
    m = subdict()
    m['test'] = 3
    self.assertEquals("3", pyrazor.Render("@model dict\n@model['test']", m))

  def testHtmlEscape(self):
    class test:
      pass

    model = test()
    model.a = "<html>"
    self.assertEquals("<html>", pyrazor.Render("@!model.a", model))
    self.assertEquals(cgi.escape("<html>"), pyrazor.Render("@model.a", model))
    self.assertEquals("<html>", pyrazor.Render("@!(model.a)", model))
    self.assertEquals(cgi.escape("<html>"), pyrazor.Render("@(model.a)", model))

  def testHtml(self):
    html = textwrap.dedent("""\
        <html>
          <head>
            <title>Alex</title>
          </head>
          <body>
            <span>Alex</span>
          </body>
        </html>""")
    self.assertEquals(html, pyrazor.Render(html))

  def testIgnoreWhitespace(self):
    """Tests that ignoring whitespace will strip all tab/spaces prefix on a line"""
    self.assertEquals("test\ntest", pyrazor.Render("test\n\ttest", ignore_whitespace=True))
    self.assertEquals("test", pyrazor.Render("  test", ignore_whitespace=True))
    self.assertEquals("test", pyrazor.Render("\t test", ignore_whitespace=True))
    self.assertEquals("test\ntest", pyrazor.Render("\t test\n\t\ttest", ignore_whitespace=True))

  def testCommentIgnored(self):
    self.assertEquals("<html></html>", pyrazor.Render("<html>@# Comment! #@</html>"))
    self.assertEquals("<html>\n</html>", pyrazor.Render("<html>\n@#A whole line is commented!\n</html>"))

  def testHelperFunction(self):
    self.assertEquals("viewtext\n<s>helper</s>\nviewtext", pyrazor.Render("@helper test(name):\n\t<s>@name</s>\nviewtext\n@test('helper')\nviewtext"))

  def testMultilineIf(self):
    """Tests that an if statement works"""
    # The renderer will output True\n and False\n due to new line chars.... theres currently no good way around this.
    # Though it's not really a huge issue except when testing for an exact match.
    template = "@if model:\n\tTrue\n@else:\n\tFalse"
    self.assertEquals("True\n", pyrazor.Render(template, True)) 
    self.assertEquals("False", pyrazor.Render(template, False)) 

  def testTmpl(self):
    """Tests that the tmpl directive renders correctly"""
    class model:
      pass

    tmpl_file = RenderTests.__writeTemplateToFile("Test")
    try:
      template = '@view.tmpl("' + tmpl_file + '")'
      self.assertEquals("Test", pyrazor.Render(template))
    finally:
      os.remove(tmpl_file)

    tmpl_file = RenderTests.__writeTemplateToFile("<head>\n\t@model.title\n</head>")
    try:
      template = '@view.tmpl("' + tmpl_file + '")'
      m = model()
      m.title = "test"
      self.assertEquals("<head>\n\ttest\n</head>", pyrazor.Render(template, m))
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
      self.assertEquals("Top title\n<head>\n\tSub Title\n</head>", pyrazor.Render(template, m))
    finally:
      os.remove(tmpl_file)

  @staticmethod
  def __writeTemplateToFile(template):
    """Writes a template out to a temporary file.  

       The file is closed and the file name returned.
       The file is automatically deleted if an exception occurs
    """
    file = tempfile.NamedTemporaryFile(delete=False)
    path = file.name
    try:
      file.write(bytes(template , 'UTF-8'))
      file.close()
      return path
    except:
      os.remove(path)
      raise

if __name__ == '__main__':
      unittest.main()

