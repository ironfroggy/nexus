from enum import Enum, auto
from re import compile, match, I

R_WS = compile(r'[\t ]+')
R_TOKEN_EQ = compile(r'(=)')
R_TOKEN_ID = compile(r'([a-z0-9\.\-_]+)', I)
R_TOKEN_KEY = compile(r'([a-z_][a-z0-9\.\-_]*)', I)
R_TOKEN_STRING = compile(r'((?<!\\)".*?(?<!\\)")', I)
R_TOKEN_NUMBER = compile(r'(\d+(\.\d+)?(?=\s|$))', I)
R_TOKEN_LINEEND = compile(r'(\n|$)')


class ParserError(ValueError):
    pass


class TOKEN_TYPE(Enum):
    STOP = auto()
    LINEEND = auto()

    OP_EQ = auto()
    OP_NE = auto()
    OP_LT = auto()
    OP_GT = auto()
    OP_PRE = auto()
    OP_POST = auto()
    OP_IN = auto()

    ID = auto()
    KEY = auto()
    STRING = auto()
    NUMBER = auto()


EVAL_TOKEN_TYPES = [
    TOKEN_TYPE.KEY,

    TOKEN_TYPE.OP_EQ,
    TOKEN_TYPE.OP_NE,
    TOKEN_TYPE.OP_LT,
    TOKEN_TYPE.OP_GT,
    TOKEN_TYPE.OP_PRE,
    TOKEN_TYPE.OP_POST,
    TOKEN_TYPE.OP_IN,

    TOKEN_TYPE.STRING,
    TOKEN_TYPE.NUMBER,
]


TOKENS = {
    TOKEN_TYPE.OP_EQ: R_TOKEN_EQ,
    TOKEN_TYPE.OP_NE: compile(r'(!=)'),
    TOKEN_TYPE.OP_LT: compile(r'(<)'),
    TOKEN_TYPE.OP_GT: compile(r'(>)'),
    TOKEN_TYPE.OP_PRE: compile(r'(~=)'),
    TOKEN_TYPE.OP_POST: compile(r'(=~)'),
    TOKEN_TYPE.OP_IN: compile(r'(~)'),

    TOKEN_TYPE.ID: R_TOKEN_ID,
    
    TOKEN_TYPE.KEY: R_TOKEN_KEY,
    TOKEN_TYPE.NUMBER: R_TOKEN_NUMBER,
    TOKEN_TYPE.STRING: R_TOKEN_STRING,
    TOKEN_TYPE.LINEEND: R_TOKEN_LINEEND,
}


class Parser:
    def __init__(self, text):
        self.text = text
        self.index = 0
        self.lastToken = None
    
    @property
    def remaining(self):
        return self.text[self.index:]
    
    @property
    def char(self):
        return self.text[self.index]
    
    def stopAtToken(self):
        while m := match(R_WS, self.char):
            self.index += m.end()

    def readToken(self, acceptTokenTypes=None, advance=True):
        try:
            self.stopAtToken()
        except IndexError:
            return TOKEN_TYPE.STOP, ''

        for tokenType, tokenPattern in TOKENS.items():
            m = match(tokenPattern, self.remaining)
            if m is not None:
                if acceptTokenTypes:
                    if tokenType not in acceptTokenTypes:
                        continue
                if advance:
                    self.index += m.end()
                return tokenType, m.groups()[0]
        snippet = self.remaining
        if len(snippet) > 20:
            snippet += '...'
        raise ParserError(f"No token found at {self.index} ({snippet!r})")
    
    def readUntilEnd(self, acceptTokenTypes=None):
        tokens = []
        tokenType, token = self.readToken(acceptTokenTypes)
        while tokenType != TOKEN_TYPE.STOP:
            tokens.append((tokenType, token))
            tokenType, token = self.readToken(acceptTokenTypes)
        return tokens
    
    def parseStringLiteral(self, literal):
        idx = 0
        buffer = []
        quote = literal[idx]
        idx += 1
        while True:
            char = literal[idx]
            if char == '"':
                break
            elif char == '\\':
                idx += 1
                esc = literal[idx]
                if esc == 'r':
                    char = '\r'
                elif esc == 'n':
                    char = '\n'
                elif esc == '\\':
                    char = '\\'
                elif esc == '"':
                    char = '"'
            buffer.append(char)
            idx += 1
        return ''.join(buffer)
