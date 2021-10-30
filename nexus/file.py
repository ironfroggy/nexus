import io
import os
import re
import typing
import uuid

from .utils import timestamp
from . import parser


R_KEY = re.compile(r'(\w+)')
R_ID = re.compile(r'^[-0-9a-f]+')

class Record(dict):
    id: str

class NexusFile:
    """Nexus Data File
    
    Operation Types:
    *: Meta data line
    N: Define a new record
    U: Update an existing record
    X: Delete a record
    I: Increment a numerical record value
    D: Decrement a numerical record value
    M: Move a record to a new ID

    Operation Line Format:
    <OP> <TS> <Record Id> <Operation Data>
    OP: Operation code (see table above)
    TS: Timestamp, an integer in milliseconds, UTC

    Meta Data Lines:
    * version=0
    * revision=0
    * author=<email>
    * device=<device identifier>
    * created=<created time>
    * updated=<updated time>
    * fileid=<random UUID>
    * fromfileid=<random UUID>
    """

    _file: io.StringIO
    _id: uuid.UUID

    records: typing.Mapping[str, typing.Mapping[str, typing.Any]]

    def __init__(self, filename: str, mode: str = "a") -> None:
        self._filename = filename
        self._device = str(uuid.uuid1(uuid.getnode(), 0))[24:]

        is_new = not os.path.exists(filename)
        if is_new:
            # new file, write header
            self._id = uuid.uuid4()
            ts = timestamp()
            open(filename, "w").writelines([
                f'* format=nexus\n',
                f'* encoding=utf8\n',
                f'* version=0\n',
                f'* revision=0\n',
                f'* device={self._device}\n',
                f'* fileid={str(self._id)}\n',
            ])

        self._file = open(filename, mode)
        self.records = {}
            
    
    def close(self):
        self._file.close()
    
    def writeRecord(self, recordId, data):
        # TODO: Handle update
        self.records[recordId] = dict(data)

        buffer = [
            'N ',
            str(timestamp()),
            ' ',
            recordId,
            ' ',
        ]
        for key, value in data.items():
            assert re.match(R_KEY, key)
            if isinstance(value, int):
                enc = str(value)
            elif isinstance(value, str):
                enc = repr(value)
                if enc[0] == "'":
                    enc = '"' + enc[1:-1] + '"'
            else:
                raise ValueError(f"Cannot write '{value.__class__.__name__}' type values.")
            buffer.extend((key, '=', enc, ' '))
        buffer.pop() # Remove the last space, not needed
        buffer.append('\n')
        line = ''.join(buffer)
        self._file.write(line)
    
    def _parseOpLine(self, line):
        if line[0] == '*':
            ts, linedata = line.split(' ', 1)
            return '*', ts, linedata.strip()
        try:
            op, ts, linedata = line.split(' ', 2)
        except ValueError:
            raise ValueError("Invalid line: %r" % (line,))
        ts = int(ts)
        recordId = None
        if op in 'NUID':
            record = self._parseRecordData(linedata)
            recordId = record.id
            if op in 'NU':
                self.records.setdefault(record.id, record).update(record)
            elif op == 'I':
                if record.id in self.records:
                    for key, value in record.items():
                        self.records[record.id][key] += value
            elif op == 'D':
                if record.id in self.records:
                    for key, value in record.items():
                        self.records[record.id][key] -= value
        return op, ts, recordId
    
    def _parseRecordData(self, line):
        p = parser.Parser(line)
        record = Record()

        t, record.id = p.readToken([parser.TOKEN_TYPE.ID])

        while p.remaining:
            # End of line?
            try:
                t, n = p.readToken([parser.TOKEN_TYPE.LINEEND], advance=False)
            except parser.ParserError:
                pass
            else:
                break

            _, key = p.readToken([parser.TOKEN_TYPE.KEY])
            p.readToken([parser.TOKEN_TYPE.OP_EQ])
            t, value = p.readToken([
                parser.TOKEN_TYPE.STRING,
                parser.TOKEN_TYPE.NUMBER,
            ])

            if t == parser.TOKEN_TYPE.STRING:
                value = p.parseStringLiteral(value)
            elif t == parser.TOKEN_TYPE.NUMBER:
                value = float(value)
                as_int = int(value)
                if as_int == value:
                    value = as_int 
            
            record[key] = value

        return record
    
    def readRecord(self):
        line = self._file.readline()
        if line:
            op, ts, recordId = self._parseOpLine(line)
            if op == '*':
                return True
            return self.records[recordId]
    
    def readAll(self):
        while True:
            record = self.readRecord()
            if record is None:
                break
