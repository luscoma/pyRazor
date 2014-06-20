# pyRazor
### A python implementation of the razor engine
--------------------------------
The Razor engine is a view renderer for ASP.net MVC3 that displays html views in a simple an intuitive manor.  It is a very lightweight engine which interferes very little with the view code.  The engine does take advantage of some of the structural aspects of html making it slightly wordy for non html/xml structured documents.

That said the goal of this implementation is to implement a view template engine that is based on the razor engine but suitable for python and simplifies some of the sharp corners of razor when working on non-xml/html.  Ideally these templates should be compilable into py files for simplified/faster execution.  Some minor modifications to the sytax can be afforded especially considering python and c# differences when it comes to indent levels and code block designation but on the whole the concepts and tokens are directly ported when possible.  Any variation from mvc's razor is reported in the remaining portions of this document.

### @model
---------------------------------
In razor a view has access to a model parameter which has a handful of properties useful in view construction.  This is especially important in statically type languages such as csharp so that accurate type checking can be performed on view code.  In pyRazor the model is accessed via the @model directive:

    <div>
      @model.someParameter
    </div>

In python static type checking is not an issue but we still support the model directive since it allows you to better structure your view's expectations.  A model can be explicitly declared in two different ways:

    @model SomePackage.SomeClass

By specifing this directive a model must be passed in and it must be an instance of the given type.  This is checked via a call to isinstance.  If the model fails this check the template will fail to render and throw an exception.

If no model is specified via a `@model` directive any object can be passed into the view as it's model including the default of None.

### @view
----------------------------------
The view object is an instance of RazorView and is available to all views at render time.  This object holds any relevant view objects and serves as a way to extends the razor system in the future.

### Razor ViewBag
----------------------------------
In mvc3 razor each view also has a ViewBag which is effectively a dictionary of key/values that are passed into the view at runtime.  In a statically typed language this is a great way to provide one off properties out-of-band from the model.  In python the model class is dynamic so we don't provide a view.data field (though there's nothing preventing a user from setting a data field and referencing it themselves). The user is encouraged to attach all properties to the model.

### @import and @from
-----------------------------------
View code will likely access the python library or even custom library code so it will need to be imported into the built view similar to a standard python file.  This is provided via the @import and @from directives:

    @import something
    @from something_else import *

These statements should be placed at the top of your view before any code that uses the import.  NOTE: these are really just shorthand the identical functionality can be achieved using the code block directive:

    @:
      import something
      from something_else import *

### Comments
-----------------------------
Comments are supported in a few forms, first the `@#` syntax which can be used in two ways:

    @# This line is a comment
    <p>Some Text@#only this is a comment#@ other than the comment</p>

In addition the multiline syntax can be used to specify multi-line comments

    @:
        # Comment line one
        # Comment Line two

### Indentation vs Brackets
----------------------------
The razor engine was originally designed for C# code which requires brackets to denote code blocks.  pyRazor adopts the methodology of python and makes multiline razor directives indent sensitive.  For example the pyRazor multiline code block:

    @:
      name = "csharp example";
      # A comment

Note that the code must not start on the same line as the @: directive and must be indented at least 2 spaces or 1 tab relative to the @:.

If/loop statements are treated similarly to designate scope:

    @if name == "alex":
      <p>this is a tag that is only printed if name == alex</p>
    <p> this tag is always printed</p>

### Nested Templates and Section Syntax
-----------------------------------------
Razor supports nested templates and the rendering of sections in view templates via wrapping and template rendering.

Wrapped templates are implemented similar to the jQuery wrap method and very useful in defining template heirarchies.  

When using `@wrap` the currently executing template specifies its parent template to render itself within.  That is to say the current template is rendered, then the specified parent template is rendered and the child template is put into the parent.  The syntax for `@wrap` is fairly straight forward:

    @view.wrap("../some/relative/path.pyr")

Importantly the template to wrap the current template in can be choosen dynamically by the view and can be declared at any place in the child template.  In the case where multiple wrap statements are encountered the last one wins.

    @if Model.something:
      @view.wrap("../something.pyr")
    @else:
      @view.wrap("../else.pyr")

When wrapping a template the parent template must specify a `@body()` to desginate where to render the wrapped template's output.  In addition pyRazor allows for sections to allow child templates to render data in multiple areas of a parent template.  These sections can either be required or optional can be rendered by child templates. Note: if a section is required and doesn't exist in the child template a parsing exception is thrown.

    @# Parent Template
    <div>
      @view.section("optional section"):
        <p>This paragraph is rendered if no section is in the nested template</p>
        <p>This one too, actually by specifing this default implementation this section became optional!</p>
      @view.section("required section")
      @view.body()
    </div>

In a wrapped child template these sections are implemented using the same syntax. NOTE: A parsing exception is thrown if a section defined in a child template is not present in the parent template:

    @# Child Template
    @view.section("name"):
      <p>This is a paragraph that is provided by the child and will override the parents implementation</p>
    @view.section("somethingRequired"):
      <p>If this was not implemented an exception is thrown<p>
    <div>
      This this element would be rendered in place of the body directive
    </div>
    <div>Really @@view.body() stands for anything not in a section</div>

pyRazor also defines the `@view.tmpl` directive to directly render another template inline into the current template.  This is the opposite of wrap and is useful for creating and rendering reusable components into a parent template.  Unlike the `@wrap` directive the `@render` directive renders the specified template at the current position passing in an optional model:

    @view.tmpl("../some/temp.late")
    @view.tmpl("../some/temp.late",model.someOtherModel)
    
### Text output
All razor output that is printed is automagically html-escaped.  If for some reason this is not what you want add an ! immediately following the @ symbol to indicate that escaping should not be performed:

    @model.someText
    @!model.someHtml

The @() syntax evaluates whatever single expression is in the () and prints it out:

    @("something simple")
    @!("<p>Non-Escaped" + Model.space + "hhahahaha</p>")

### Helper Syntax
Razor defines helpers which are basically functions declared in markup that output markup.  They effectively function as a mini template.  The syntax for helper in pyRazor is similar to mvc3:

    @helper listrow(text):
      @:
        length = len(text)
        mod = length % 6
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

Note: these helpers may only be accessed by the current template. If you need to reuse a helper function create a view that takes in a model of your parameters and call @tmpl(view, model)

### Notes on overcoming strangeness with non-xml/html documents
----------------
A typical c# mvc3 razor template my look similar to the following. Notice how it takes advantage of the <p> tag to determine what is c# code and what should be interpreted as view code:

    @if (name == "alex") {
      name = "hi";
      <p>Non Python text: @name</p>
    } else {
      <p>Somethign else: @name</p>
    }

This approach works incredibly well for xml/html structured documents; however, it breaks down for other formats such as json:

    {
      @if (name == "alex") {
        "tag": "alex",
        "blah": "@name"
      }
    }

This will fail to parse due to the two lines after the if statement being interpreted as code instead of json output.  This case is handled in the mvc3 razor implementation by wrapping any non xml/html content in a <text></text> tag.

    {
      @if (name == "alex") {
        <text>
        "tag": "alex",
        "blah": "@name",
        </text>
      }
    }

To generalize razor templates, pyRazor assumes all if/else/loop statements are a single line and that anything at the appropriate indention level should be intepreted as view code.  This does not preclude multiline code blocks as shown below:

    @if name == "alex":
      "tag": "alex",
    @elif name == "bob:
        @:
            name = "john"
            l = len(name)
        "tag": "@name",
        "length": "@l",
    @else:
      "tag": "@name",
      name = "john"; *// will be printed out as view text*
      "tag": "not important",

### Escaping the @ sign
---------------------
Ideally this thing should have some intelligence (i.e. mvc razor does a good job of figuring out when you mean @ literally vs as a directive), unfortunately this is not a high priority so if you mean to use a literal @ ensure you write @@ to escape it.

### Rendering templates from code
---------------------
When not compiled you must import the pyRazor library and call compile or render.  Compile parses and compiles a template into a python function that can be rendered via the templates render method.  pyRazor.render compiles a template internally then renders it without returning the compiled model

    import pyrazor

    # Render template without a model
    pyrazor.Render("hello")  # hello

    # Render a simple template with a model
    pyRazor.Render("@Model", "The model is a string")

    # Just compile the template for repeated rendering
    view = pyRazor.Parse("@Model")
    view.Render("the model is a string")


### Unsupported Stuff
--------------
The weird passing of inline template stuff is not supported in pyRazor. It will likely not be missed.

### Example
------------------
Here is an example showing a few of the features off:

    @from datetime import datetime
    <html>
      <head>
        <title>@model.title</title>
      </head>
      <body>
        @for p in products:
          <div>We have @p.stockCount @p.Name<div>
          <div>We @("apologize" if p.stockCount <= 0 else "hope we can help")</div>
          @if p.isNeat:
            <div>This product is really neat</div>
          @else
            <div>Really this product is bad</div>
          <div>Rendered @@ @datetime.now()</div>
      </body>
    </html>

