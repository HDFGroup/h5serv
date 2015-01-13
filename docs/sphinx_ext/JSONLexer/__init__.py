def setup(sphinx):
    print "sphinx_ext setup for json"
    from pygson.json_lexer import JSONLexer
    sphinx.add_lexer("json", JSONLexer())
