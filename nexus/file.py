import io
import re
import typing
import uuid

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
        self._file = open(filename, mode)
        self._device = str(uuid.uuid1(uuid.getnode(), 0))[24:]

        self.records = {}

        if mode[0] == 'w':
            # new file, write header
            self._id = uuid.uuid4()
            self._file.writelines([
                '* 0 format=nexus\n',
                '* 0 encoding=utf8\n',
                '* 0 version=0\n',
                '* 0 revision=0\n',
                f'* 0 device={self._device}\n',
                f'* 0 fileid={str(self._id)}\n',
            ])
    
    def close(self):
        self._file.close()
    
    def writeRecord(self, recordId, data):
        # TODO: Handle update
        self.records[recordId] = dict(data)

        buffer = [
            'N 0 ',
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
    
    def _matchNext(self, line, idx):
        m = re.match('(\w+)="((?:[^"]|.)*)"', line[idx:])
        if m is None:
            m = re.match('(\w+)=([^ ]+)', line[idx:])
        return m
    
    def _parseOpLine(self, line):
        try:
            op, ts, linedata = line.split(' ', 2)
        except ValueError:
            raise ValueError("Invalid line: %r" % (line,))
        ts = int(ts)
        recordId = None
        if op == '*':
            return op, ts, linedata.strip()
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
        record = Record()
        idx = line.index(' ')
        record.id = line[:idx]
        idx += 1
        m = self._matchNext(line, idx)
        while m is not None:
            key, value = m.groups()
            if re.match('\d+', value):
                value = int(value)
            record[key] = value
            idx += m.end() - m.start()
            m = self._matchNext(line, idx)
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
