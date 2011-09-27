# pyRazor
## Pure python razor template engine implementation
----------------------
The Razor engine is a view renderer for ASP.net MVC3 that displays html views in a simple an intuitive manor.  It is a very lightweight engine which interferes very little with the view code.  The engine does take advantage of some of the structural aspects of html making it slightly wordy for non html/xml structured documents.

That said the goal of this implementation is to implement as much of the razor template engine as make sense in pure python code to be used to render pyr files on the fly.  Optionally these templates should be compilable into py files for simplified/faster execution.  Some minor modifications to the sytax can be afforded especially considering python and c# differences when it comes to indent levels and code block designation but on the whole the concepts and tokens are directly ported when possible.  Any variation is reported in the remaining portions of this document.

### @model
@model is used in razor to denote the model a view is expecting.  This is expecailly important in statically type languages such as csharp so that accurate type checking can be performed on view code.  In a dynamic language such as python this is not near as important so by default this directive is not required and defaults to any object (similar to how c# 4.0 defaults to @model dynamic).  We do however provide support for model in two ways:
    @model SomeClass
This method basically wraps the template with a call to isinstance throwing an exception if the model is not of the specified type.  This prevents any model being used that isnt the exact type.

In some cases it may be beneficial to allow subclasses of the specified type, in that case a variation of the model syntax is allowed:
    @model extends SomeClass
This basically wraps the template with a call to issubclass instead of isinstance.

Regardless of rather an explicit model is specified access to the model in the view is provided via a model parameter passed into the view at render time:
    <div>
      @model.someParameter
    </div>

### @import and @from
View code will likely access python library or even custom code so it will need to be imported into the view similar to a standard python file.  This is provided via the @import and @from directives:
    @import something
    @from something_else import *
These statements should be placed at the top of your view before any code is accessed that uses the import.  NOTE: these are really just shorthand the identical functionality can be achieved using the code block directive:
    @:
      import something
      from something_else import *

### Indentation vs Brackets
The razor engine was originally designed for C# code which requires brackets to denote code blocks.  pyRazor adopts the methodology of python and makes multiline razor directives indent sensitive.  For example the multiline code block:
    @{
      name = "csharp example";
    }
In pyrazor this is implemented using the `@:` directive:
    @:
      name = "csharp example";
Note that the code must not start on the same line as the @: directive and must be indented at least 2 spaces or 1 tab relative to the @:.

If/loop statements are treated similarly to designate scope:
    @if name == "alex":
      <p>this is a tag that is only printed if name == alex</p>
    <p> this tag is always printed</p>

### Nested Templates and Section Syntax
-------------------
Razor supports nested templates and the rendering of sections in view templates.  This mvc3 implementation looks like the following:
    <div>
      @RenderSection("name", optional: true)
    </div>
This syntax assumes a few things, one that optional is the rare case, and two that if the section is not defined in the nested template that nothing should be printed out (in realty there is a syntax to handle an optional section not existing but it is a few extra lines of boilerplate).

pyRazor handles these sections slightly differently, first assuming that sections are optional by default and second by making it very easy to define behavior if a section doesn't exist.  Note: if a section is required and doesn't exist a parsing exception is thrown.
    <div>
      @section("name"):
        <p>This paragraph is rendered if no section is in the nested template</p>
      @section("somethingRequired": required=true)
    </div>
In case you were curious the `@RenderBody()` syntax is not valid in pyRazor either instead:
    @body
In a template that provides these sections we just specify a similar section directive:
    @section("name"):
      <p>This is a paragraph that is provided by the child</p>
    @section("somethingRequired"):
      <p>If this is not implemented an exception is thrown<p>
    <div>
      This this element would be rendered in place of the body directive
    </div>

pyRazor also uses a slightly different syntax for specifing parent templates similar to the jquery syntax.  In standard razor the LayoutPage variable is included in all views and is set in the template:
    @{
      LayoutPage = "../some/relative/path.cshtml";
    }
pyRazor provides the `@wrap` directive to achieve the same thing:
    @wrap ../some/relative/path.pyr
Importantly the template to wrap the current template in can be choosen dynamically by the view:
    @if Model.something:
      @wrap ../something.pyr
    else:
      @wrap ../else.pyr
Wrap can be called anywhere in the template without performance penalty.  In the case where multiple wrap statements are encountered the last one wins.

pyRazor also defines the `@render` directive to directly render another template inline into the current template.  This is sort of the opposite of wrap and analgous to the mvc directive `@RenderPartial`.  The `@render` directive renders the specified template at the current position passing in an optional model.  This is useful for reusable components that you can define in a template.
    @render ../some/template
    @render Model.childModel ../some/path/to.template
    @render Model.childModel "../some/template with/spaces.template"

### Text output
All razor output that is printed is automagically html-escaped.  If for some reason this is not what you want add an ! immediately following the @ symbol to indicate that escaping should not be performed:
    @model.someText
    @!model.someHtml

There is also a @debug that is only visible if the debug:true paramter is passed into the template:
    @debug("Some text to be written to the document")
    @!debug("<p>Some html to be written to the document")

The @() syntax evaluates whatever single expression is in the () and prints it out:
    @("something simple")
    @!("<p>Non-Escaped" + Model.space + "hhahahaha</p>")

### Helper Syntax
MVC3 includes helpers which are basically functions declared in markup that output markup.  They effectively function as a mini template.  The syntax for helper in pyRazor is similar to mvc3:
    @helper listrow(text):
      @{
        length = len(text);
        mod = length % 6;
      }
      <div>
        <div>Item</div>
        <div>@text</div>
        <div>meaningless: @mod
        <div>@text.islower()</div>
      </div>
This method could be called elsewhere in the DOM:
    <div id="container">
      @for p in products:
        @listrow(p.text)
    </div>

Note: these helpers may only be accessed by the current template or any nested templates or wrapped templates.  Do not however declare a template in some parent template then expect a child that calls @wrap to be able to use it.

### Strangeness with non-xml/html documents
----------------
A typical c# razor template my look similar to the following. Notice how it takes advantage of the <p> tag to allow for the lines immediately following the if statement be parsed as c# code.
    @if (name == "alex") {
      name = "hi";
      <p>Non Python text: @name</p>
    } else {
      <p>Somethign else: @name</p>
    }

This approch works incredibly well for xml/html structured documents; however, it breaks down for other formats such as json:
    {
      @if (name == "alex") {
        "tag": "alex",
        "blah": "@name"
      }
    }

This will fail to parse due to the two lines after if statement being interpreted as python code instead of json code.  This case is handled in the standard implementation by wrapping any content in a <text></text> tag.
    {
      @if (name == "alex") {
        <text>
        "tag": "alex",
        "blah": "@name",
        </text>
      }
    }

To generalize the templates pyRazor assumes all if/else/loop statements are a single line unless explicitly indicated using an optional multi-line syntax.  First the standard implementation using single line assumptions: @if name == "alex":
      "tag": "alex",
    else:
      name = "john"; *// will be printed out as view text*
      "tag": "not important",

To handle the fairly common case of a single line of code after the for statement use the razor syntax:
    @if name == "alex":
      @name *# this will print the name out*
      <p>Something of note</p>

To better handle the (much rarer) case of multi-line code we reuse the explicit multiline code syntax of razor
    @if name == "alex":
      @: 
        name = "john";
        t = "test";
      "tag": "alex",
      "blah": "@t",
    else: 
      "something": "else"

### Escaping the @ sign
---------------------
Ideally this thing should have some intelligence (i.e. mvc razor does a good job of figuring out when you mean @ literally vs as a directive), unfortunately this is not a high priority so if you mean to use a literal @ ensure you write @@ to escape it.

### Rendering templates from code
---------------------
When not compiled you must import the pyRazor library and call render:

    import pyRazor

    # Render template without giving a model
    pyRazor.render("../path/to.template")

    # In this case the model is a string we specify
    pyRazor.render("../path/to.template", "The model is a string")

    # In this case we also specify a few extra paramters
    pyRazor.render("../path/to.template", "The model is a string", debug=true)

In the case where a template is compiled, just import the template directly and call its render method minus the template path:
    import myTemplate

    myTemplate.render("My Model", debug=true)

#### Named parameters include:
  * debug - boolean - defaults to false removing @debug directives.
  * nocache - boolean - defaults to false, allowing the engine to cache templates by compiling them.

### Unsupported Stuff
--------------
The weird passing of inline template stuff is not supported in pyRazor. It will likely not be missed.

### Example
------------------
Here is an example showing a few of the features off:

    @from datetime import datetime
    <html>
      <head>
        <title>@Model.title</title>
      </head>
      <body>
        @for p in products:
          <div>We have @p.stockCount @p.Name<div>
          <div>We @("apologize" if p.stockCount <= 0 else "hope we can help")</div>
          @if p.isNeat:
            <div>This product is really neat</div>
          else
            <div>Really this product is bad</div>
          <div>Rendered @@ @datetime.now()</div>
      </body>
    </html>

