import os
import re
from tempfile import TemporaryDirectory

from nexus.file import Record, NexusFile
from nexus.db import NexusDB

def test_single_db_entry():
    with TemporaryDirectory() as tempdir:
        f = open(os.path.join(tempdir, "1.nexus"), "w")
        f.write('N 0 1 foo="Hello, World!"')
        f.close()

        db = NexusDB(tempdir)
        db.readAll()
        db.get("1", "foo")
        assert db.get("1", "foo") == "Hello, World!"

def test_simple_combination_entry():
    with TemporaryDirectory() as tempdir:
        f = open(os.path.join(tempdir, "1.nexus"), "w")
        f.write('N 0 1 foo="Hello, World!"')
        f.close()

        f = open(os.path.join(tempdir, "2.nexus"), "w")
        f.write('N 0 1 bar="Goodbye, World!"')
        f.close()

        db = NexusDB(tempdir)
        db.readAll()
        assert db.get("1", "foo") == "Hello, World!"
        assert db.get("1", "bar") == "Goodbye, World!"

def test_multi_order_entry():
    with TemporaryDirectory() as tempdir:
        f = open(os.path.join(tempdir, "1.nexus"), "w")
        f.write('N 100 1 foo="Hello, World!"\n')
        f.write('N 200 1 foo="Hey, World!"\n')
        f.close()

        f = open(os.path.join(tempdir, "2.nexus"), "w")
        f.write('N 150 1 foo="Goodbye, World!"\n')
        f.close()

        db = NexusDB(tempdir)
        db.readAll()
        assert db.get("1", "foo") == "Hey, World!"

def test_db_record_write():
    with TemporaryDirectory() as tempdir:
        db = NexusDB(tempdir)
        db.set("ID-1", {"name": "Bobby Tables"})
        print(db._write_file_path)
        print(open(db._write_file_path).read())
        print(db._read_file_paths)

        db = NexusDB(tempdir)
        db.readAll()
        assert db.get("ID-1", "name") == "Bobby Tables"