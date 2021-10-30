import re

from nexus.file import Record, NexusFile


def test_read_string():
    f = open("test.nexus", "w")
    f.write('N 0 1 foo="Hello, World!"')
    f.close()

    nf = NexusFile("test.nexus", "r")
    record = nf.readRecord()
    assert record.id == "1"
    assert record["foo"] == "Hello, World!"
    assert nf.records["1"]["foo"] == "Hello, World!"

def test_read_multiple():
    f = open("test.nexus", "w")
    f.write('N 0 1 foo="Hello, World!" bar="Goodbye, World!"')
    f.close()

    nf = NexusFile("test.nexus", "r")
    record = nf.readRecord()
    assert record.id == "1"
    assert record["foo"] == "Hello, World!"
    assert record["bar"] == "Goodbye, World!"
    assert nf.records["1"]["foo"] == "Hello, World!"
    assert nf.records["1"]["bar"] == "Goodbye, World!"

def test_read_string_esc_quote():
    f = open("test.nexus", "w")
    f.write('N 0 1 foo="Hello, \\"Bob\\"!"')
    f.close()

    nf = NexusFile("test.nexus", "r")
    record = nf.readRecord()
    assert record.id == "1"
    assert record["foo"] == 'Hello, "Bob"!'
    assert nf.records["1"]["foo"] == 'Hello, "Bob"!'

def test_read_number():
    f = open("test.nexus", "w")
    f.write('N 0 1 x=42')
    f.close()

    nf = NexusFile("test.nexus", "r")
    record = nf.readRecord()
    assert record.id == "1"
    assert record["x"] == 42
    assert nf.records["1"]["x"] == 42

def test_read_all():
    f = open("test.nexus", "w")
    f.write('N 0 1 x=42\n')
    f.write('N 0 2 x=10\n')
    f.close()

    nf = NexusFile("test.nexus", "r")
    nf.readAll()
    assert nf.records["1"]["x"] == 42
    assert nf.records["2"]["x"] == 10

def test_write_number():
    nf = NexusFile("test.nexus", "w")
    nf.writeRecord("42", {"x": 42})
    nf.close()

    f = open("test.nexus", "r")
    for line in f.readlines():
        pass
    assert re.match(r"^N \d+ 42 x=42\n$", line)

def test_write_string():
    nf = NexusFile("test.nexus", "w")
    nf.writeRecord("7", {"lucky": "Number Seven"})
    nf.close()

    f = open("test.nexus", "r")
    for line in f.readlines():
        pass

    assert re.match(r'N \d+ 7 lucky="Number Seven"\n', line)

def test_write_string_w_quote():
    nf = NexusFile("test.nexus", "w")
    nf.writeRecord("8", {"mobster": 'Billy "The Big One" McGee'})
    nf.close()

    f = open("test.nexus", "r")
    for line in f.readlines():
        pass
    assert re.match(r'N \d+ 8 mobster="Billy \"The Big One\" McGee"\n', line)
