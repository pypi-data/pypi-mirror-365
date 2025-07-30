from pygments.lexer import RegexLexer, bygroups, include
from pygments.token import Keyword, Text, Comment, String, Number, Operator, Name, Literal


__all__ = ['SimStmLexer']


class SimStmLexer(RegexLexer):
    name = "Pygments Plugin SimStm Language"
    aliases = ["simstm"]
    filenames = ["*.stm"]
    mimetypes = ["text/x-stm"]

    keywords = ["writable",
                "writeable",  # grammar error writeable/writable
                "readable",
                "appendable",
                "write",
                "append",
                "read",
                "pointer",
                "end",
                "all",
                "copy",
                "insert",
                "append",
                "delete",
                "size",
                "array",
                "message",
                "get",
                "set",
                "lines"]

    number_or_pseudo = r'(\$[a-zA-Z_]\w*|0x[0-9a-fA-F](_?[0-9a-fA-F])*|0b[01](_?[01])*|\d(_*\d)*)'

    tokens = {
        'root': [
            # Newlines as Text
            (r'\n', Text),

            # Whitespace (excluding newlines)
            (r'[ \t\r]+', Text.Whitespace),

            include('special'),

            # commnets
            (r'(\s+)(--.*$)', bygroups(Text.Whitespace, Comment.Single)),
            (r'(--.*$)', Comment.Single),

            # Stings
            (r'"[^"]*"', Literal.String),

            ##########################################################################
            # This section captures and processes keywords consisting of three words
            (r'file\s+(?:read)\s+(?:all|end)', Keyword),
            (r'lines\s+(?:get)\s+(?:array)', Keyword),
            (r'lines\s+(?:set|insert|append)\s+(?:array|message)', Keyword),
            (r'(?:array|file|lines)\s+(?:pointer)\s+(?:copy)', Keyword),
            (r'(?:bus|signal)\s+(?:pointer)\s+(?:copy|get|set)', Keyword),
            (r'bus\s+(?:timeout)\s+(?:get|set)', Keyword),

            ##########################################################################
            # This section captures and processes keywords consisting of two words
            (r'var\s+(?:verify)', Keyword),
            (r'array\s+(?:set|get|verify|size)', Keyword),
            (r'end\s+(?:proc|interrupt)', Keyword),
            (r'file\s+(?:writeable|readable|appendable|write|append|read)', Keyword),
            (r'lines\s+(?:delete|size)', Keyword),
            (r'linloges\s+(?:message|lines)', Keyword),
            (r'(?:signal|bus)\s+(?:write|read|verify)', Keyword),

            ##########################################################################
            # This section captures and processes keywords consisting of one words
            (r'\b(array|bus|file|lines|signal|var)\b', Keyword.Declaration),
            (r'\b(log|proc|interrupt)\b', Keyword),
            (r'\b(equ|add|sub|mul|div|and|or|xor|shl|shr|inv|ld)\b', Operator),


            ##########################################################################
            # This section captures and processes special keywords
            (r'(include)(\s+)("[^"]+")',
             bygroups(Keyword.Namespace, Text.Whitespace, Name.Namespace)),

            (r'(const)(\s+)([a-zA-Z_]\w*)',
             bygroups(Keyword.Declaration, Text.Whitespace,
                      Name.Constant)),

            # function
            (r'\b([a-zA-Z_]\w*)(:)',
             bygroups(Name.Function, Keyword.Pseudo)),

            (r'\b(if|elsif|else|end if|loop|end loop)\b', Keyword),
            (r'(<|>|=)', Operator),

            (r'\b(random|return|abort|finish|call|trace|resume|seed|wait|marker|verbosity)\b', Name.Function.Magic),

            # parce other words as variables
            (r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', Name.Variable),

            # finally catch-all anything else as Text
            (r'.+', Text),

        ],
        'special': [
            include('numbers'),
            include('references'),
        ],
        'numbers': [
            # Hex numbers
            (r'0x[0-9a-fA-F](_?[0-9a-fA-F])*', Number.Hex),

            # Bin numbers
            (r'0b[01](_?[01])*', Number.Bin),

            # Integers
            (r'\d(_*\d)*', Number.Integer),
        ],

        'references': [
            (r'(\$)(?=[a-zA-Z0-9_]*[a-zA-Z])([a-zA-Z_][a-zA-Z0-9_]*)', bygroups(Keyword.Pseudo, Name.Variable))

        ]
    }
