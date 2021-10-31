import io
import os
import re
import typing
import uuid

from .utils import timestamp
from . import parser


R_KEY = re.compile(r'(\w+)')
R_ID = re.compile(r'^[-0-9a-f]+')


class EndOfRecords(ValueError):
    pass


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
    
    def writeLine(self, recordId, op, data):
        buffer = [
            op,
            ' ',
            str(timestamp()),
            ' ',
            recordId,
        ]
        if op == 'X':
            buffer.append(' ')
            if data:
                for key in data:
                    buffer.extend([key, ' '])
        else:
            buffer.append(' ')
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
    
    def _stringToValue(self, string):
        try:
            return int(string)
        except ValueError:
            try:
                return float(string)
            except ValueError:
                return string
    
    def _convertDictValues(self, data):
        for key, value in data.items():
            data[key] = self._stringToValue(value)
    
    def set(self, recordId, data):
        self._convertDictValues(data)
        rec = self.records.setdefault(recordId, {})
        rec.update(data)
        self.writeLine(recordId, 'N', data)
    
    def inc(self, recordId, data):
        self._convertDictValues(data)
        rec = self.records.setdefault(recordId, {})
        rec.update(data)
        self.writeLine(recordId, 'I', data)

    def dec(self, recordId, data):
        self._convertDictValues(data)
        rec = self.records.setdefault(recordId, {})
        rec.update(data)
        self.writeLine(recordId, 'D', data)
    
    def delete(self, recordId, keys=None):
        self.writeLine(recordId, 'X', keys)
    
    def get(self, recordId, key=None):
        if not self.records:
            self.readAll()
        record = self.records[recordId]
        if key:
            return record[key]
        else:
            return record
    
    def _parseOpLine(self, line):
        if line[0] == '*':
            ts, linedata = line.split(' ', 1)
            return '*', 0, linedata.strip(), None
        try:
            op, ts, linedata = line.split(' ', 2)
        except ValueError:
            raise ValueError("Invalid line: %r" % (line,))
        ts = int(ts)
        data = None
        p = parser.Parser(linedata)
        t, recordId = p.readToken([parser.TOKEN_TYPE.ID])
        if op == 'X':
            data = []
            while p.remaining:
                t, key = p.readToken([parser.TOKEN_TYPE.KEY, parser.TOKEN_TYPE.LINEEND])
                if t == parser.TOKEN_TYPE.LINEEND:
                    break
                else:
                    data.append(key)
            
        elif op in 'NUID':
            data = self._parseRecordData(p.remaining)
        else:
            data = None
        # ts = int(ts)
        return op, ts, recordId, data
    
    def applyOperation(self, op, records, recordId, data):
        if op == 'X':
            rec = records.get(recordId)
            if rec:
                if data:
                    for key in data:
                        rec.pop(key)
                else:
                    records.pop(recordId)
            
        elif op in 'NU':
            rec = records.setdefault(recordId, Record())
            rec.id = recordId
            rec.update(data)
        elif op == 'I':
            records.setdefault(recordId, Record())
            rec = records[recordId]
            for key, value in data.items():
                rec.setdefault(key, 0)
                rec[key] += data[key]
        elif op == 'D':
            records.setdefault(recordId, Record())
            rec = records[recordId]
            for key, value in data.items():
                rec.setdefault(key, 0)
                rec[key] -= data[key]
    
    def _parseRecordData(self, line):
        p = parser.Parser(line)
        record = {}

        # t, record.id = p.readToken([parser.TOKEN_TYPE.ID])

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
    
    def parseNextRecord(self):
        line = self._file.readline()
        if line:
            return self._parseOpLine(line)
        else:
            raise EndOfRecords()
    
    def readRecord(self):
        op, ts, recordId, data = self.parseNextRecord()
        if op == '*':
            return ts, None
        else:
            self.applyOperation(op, self.records, recordId, data)
        return ts, self.records.get(recordId, None)
    
    def readAll(self):
        try:
            while True:
                ts, record = self.readRecord()
        except EndOfRecords:
            pass
