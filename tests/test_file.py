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
    nf.set("42", {"x": 42})
    nf.close()

    f = open("test.nexus", "r")
    for line in f.readlines():
        pass
    assert re.match(r"^N \d+ 42 x=42\n$", line)

def test_inc_number():
    nf = NexusFile("test.nexus", "w")
    nf.set("42", {"x": 42})
    nf.inc("42", {"x": 1})
    nf.close()

    nf = NexusFile("test.nexus", "r")
    nf.readAll()
    assert nf.records["42"]["x"] == 43


def test_inc_new_number():
    nf = NexusFile("test.nexus", "w")
    nf.set("42", {"x": 42})
    nf.inc("42", {"z": 1})
    nf.close()

    nf = NexusFile("test.nexus", "r")
    nf.readAll()
    assert nf.records["42"]["x"] == 42
    assert nf.records["42"]["z"] == 1


def test_dec_number():
    nf = NexusFile("test.nexus", "w")
    nf.set("42", {"x": 42})
    nf.dec("42", {"x": 1})
    nf.close()

    nf = NexusFile("test.nexus", "r")
    nf.readAll()
    assert nf.records["42"]["x"] == 41


def test_dec_new_number():
    nf = NexusFile("test.nexus", "w")
    nf.set("42", {"x": 42})
    nf.dec("42", {"z": 1})
    nf.close()

    nf = NexusFile("test.nexus", "r")
    nf.readAll()
    assert nf.records["42"]["x"] == 42
    assert nf.records["42"]["z"] == -1


def test_delete_key():
    nf = NexusFile("test.nexus", "w")
    nf.set("42", {"x": 42, "z": 10})
    nf.delete("42", ["x"])
    nf.close()

    nf = NexusFile("test.nexus", "r")
    nf.readAll()
    assert nf.records["42"] == {"z": 10}


def test_delete_record():
    nf = NexusFile("test.nexus", "w")
    nf.set("42", {"x": 42, "z": 10})
    nf.delete("42")
    nf.close()

    nf = NexusFile("test.nexus", "r")
    nf.readAll()
    assert "42" not in nf.records
    

def test_write_string():
    nf = NexusFile("test.nexus", "w")
    nf.set("7", {"lucky": "Number Seven"})
    nf.close()

    f = open("test.nexus", "r")
    for line in f.readlines():
        pass

    assert re.match(r'N \d+ 7 lucky="Number Seven"\n', line)

def test_write_string_w_quote():
    nf = NexusFile("test.nexus", "w")
    nf.set("8", {"mobster": 'Billy "The Big One" McGee'})
    nf.close()

    f = open("test.nexus", "r")
    for line in f.readlines():
        pass
    assert re.match(r'N \d+ 8 mobster="Billy \"The Big One\" McGee"\n', line)
