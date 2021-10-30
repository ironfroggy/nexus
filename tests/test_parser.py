import pytest

from nexus.parser import Parser, ParserError, TOKEN_TYPE


@pytest.mark.parametrize("string,expectedType,valid", (
    ('=', TOKEN_TYPE.OP_EQ, True),
    ('word', TOKEN_TYPE.KEY, True),
    ('word123', TOKEN_TYPE.KEY, True),
    ('123word', TOKEN_TYPE.KEY, 'error'),
    ('CamelCase', TOKEN_TYPE.KEY, True),
    ('with_underscore', TOKEN_TYPE.KEY, True),
    ('dotted.name', TOKEN_TYPE.KEY, True),
    ('_underscore', TOKEN_TYPE.KEY, True),
    ('dashed-name', TOKEN_TYPE.KEY, True),
    ('-dash-prefixed', TOKEN_TYPE.KEY, 'error'),
    ('.dot.prefixed', TOKEN_TYPE.KEY, 'error'),
    ('\n', TOKEN_TYPE.LINEEND, True),
))
def test_parse_basic_token(string, expectedType, valid):
    p = Parser(string)
    
    if valid == 'error':
        with pytest.raises(ParserError):
            tokenType, token = p.readToken([expectedType])
            assert 0, (tokenType, token)

    else:
        tokenType, token = p.readToken([expectedType])

        if valid:
            assert tokenType == expectedType
            assert token == string
        else:
            assert tokenType != expectedType
            assert token != string


@pytest.mark.parametrize("input,output", (
    ('"Hello"', '"Hello"'),
    ('"Hello," she said.', '"Hello,"'),
    (r'"Ted \"Big Man\" Kazinsky"', r'"Ted \"Big Man\" Kazinsky"'),
    (r'"Single \" Quote"', r'"Single \" Quote"'),
))
def test_parse_string_token(input, output):
    p = Parser(input)
    
    tokenType, token = p.readToken([TOKEN_TYPE.STRING])

    assert tokenType == TOKEN_TYPE.STRING
    assert token == output


@pytest.mark.parametrize("input,output", (
    ('123', '123'),
    ('123 ', '123'),
    ('3.14', '3.14'),
    ('1.0.3', None),
    ('123abc456', None),
    ('.438', None),
))
def test_parse_number_token(input, output):
    p = Parser(input)
    
    if output:
        tokenType, token = p.readToken([TOKEN_TYPE.NUMBER])
        assert token == output
    else:
        with pytest.raises(ParserError):
            tokenType, token = p.readToken([TOKEN_TYPE.NUMBER])


seqStrings = pytest.mark.parametrize("string,count", (
    ('key=123', 3),
    ('key=123\n', 4),
    ('    key=123', 3),
    ('\tkey=123', 3),
    ('key = 123', 3),
    ('key=123\n', 4),
))


@seqStrings
def test_read_until_end(string, count):
    p = Parser(string)
    tokens = p.readUntilEnd()

    assert len(tokens) == count


@seqStrings
def test_parse_token_sequence(string, count):
    p = Parser(string)
    type1, token1 = p.readToken([TOKEN_TYPE.KEY])
    type2, token2 = p.readToken([TOKEN_TYPE.OP_EQ])
    type3, token3 = p.readToken([TOKEN_TYPE.NUMBER])

    assert type1 == TOKEN_TYPE.KEY
    assert type2 == TOKEN_TYPE.OP_EQ
    assert type3 == TOKEN_TYPE.NUMBER

    assert token1 == 'key'
    assert token2 == '='
    assert token3 == '123'

    if count == 4:
        type4, token4 = p.readToken()
        assert type4 == TOKEN_TYPE.LINEEND
        assert token4 == '\n'

CHAR_DBL_QUOTE = '\x22'
CHAR_SING_QUOTE = '\x27'
CHAR_SLASH = '\x5c'

@pytest.mark.parametrize("literal,value", (
    ('"Bob"', "Bob"),
    ('"A single \\" symbol."', "A single \x22 symbol."),
))
def test_string_literal_parsing(literal, value):
    p = Parser(literal)
    assert value == p.parseStringLiteral(literal)
