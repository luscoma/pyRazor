# Implementation Details
--------------------------
This section describes some of the implementation details and reasoning behind some decisions.

### Lexer implementation
--------------------------
Ive debated between using a a proper lexer and a more straightforward loop.  The lexer is a more 
proper structure for parsing a complex document but in our case we're only interested in finding one
of two types of code, either a single line of python code prefixed with the *@* sign (in some cases 
multiple lines denoted by ident) or view code which we straight copy in a print statement.

Lexer's can also improve error handling when the syntax is invalid since yacc or similar can be used
to verify the token content.  So though it does seem a bit more complicated to implement a lexer will
be used to implement the pyRazor parser.

Currently sexy lexing looks like a easily extensible, easy to use lexing system
http://www.evanfosmark.com/2009/02/sexy-lexing-with-python/

### RE Tokens
---------------------------
Goals: Attempt to figure out the user's intentions and do our best to translate that to python code
Non-Goals: Perform python syntax checking
* .+?(?=@) - Matches any text upto the @ identifier, this is view text
* @@ - Matches the @@ so it can be replaced with a literal @ in the code
* ^@(\w*).*:$ - Handle @Somecode: This also matches @: multiline code designator
* @(!)?\(- Handles finding a python expression within the ()
* @(!)?(\w+(?:(?:\[.+\])|(?:\(.*\)))?(?:\.[a-zA-Z]+(?:(?:\[.+\])|(?:\(.*\)))?)?) - Makes our best guess to figure out a single python identifier (http://docs.python.org/reference/lexical_analysis.html)
* @#.*(?:#@) - Matches comment text either @#blah#@ or @#something

### Indentation
---------------------------
To figure out indent each line should have it's indent calculated so we can keep track of the ident level.
The python docs say that they keep a stack of indent/dedent levels and push a new level on the stack when
seeing an indent increase (usually after ':') and whenever the indent decreases they pop levels off the stack
until they find something on the stack at that level.  If they do not find anything they throw an error.

This sort of scheme should work pretty well but it does enforce some constraints on the user in that they
must follow these rules when laying out their view code.  This would probably look something like this
    <html>
      <head>
        <title>Test</title>
      </head>
      <body>
        @if Model.m == 3:
          <span>This must be on a line explicitly indented</span>
          <span>If you hard return a line 
          It can't wrap all the way back which may be an issue</span>
        <span>Something</span>
        @:
          # Multiline code blocks have the same constraint
          <span>This is now interpretted as python code!</span>
      </body>
    </html>
This means we should probably keep track of indentation on every line but only throw parsing errors if
we find that you screwed up indent on a multi-line control statement.