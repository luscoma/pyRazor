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