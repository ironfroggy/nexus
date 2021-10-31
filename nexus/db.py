from __future__ import annotations
from nexus.file import NexusFile, Record, EndOfRecords


from typing import Iterable
from enum import Enum
import os
import uuid


class NexusDB:
    dirname: str

    def __init__(self, dirname: str) -> None:
        if not os.path.exists(dirname):
            os.mkdir(dirname)
        self.dirname = dirname
        self._device = str(uuid.uuid1(uuid.getnode(), 0))[24:]    

        self._write_file_path = os.path.join(dirname, f"{self._device}.nexus")
        self._read_file_paths = [
            os.path.join(dirname, f"{filename}")
            for filename in os.listdir(dirname)
        ]
        if self._write_file_path not in self._read_file_paths:
            self._read_file_paths.insert(0, self._write_file_path)

        self.records = {}
    
    def _openReadFiles(self):
        return [NexusFile(path, "r") for path in self._read_file_paths]

    def readAll(self):
        ts = 0
        files = self._openReadFiles()
        nextOps = [nf.parseNextRecord() for nf in files]
        while not all(op is None for op in nextOps):
            # Find the next timestamp, read that line, advance that file
            lowestIdx = 0
            lowestTS = float('inf')
            for i, op in enumerate(nextOps):
                if op:
                    if op[1] < lowestTS:
                        lowestIdx = i
                        lowestTS = ts
            # Process operation
            nf = files[lowestIdx]
            op, ts, recordId, data = nextOps[lowestIdx]
            nf.applyOperation(op, self.records, recordId, data)
            # Advance the entry in nextOps
            try:
                nextOps[lowestIdx] = files[lowestIdx].parseNextRecord()
            except EndOfRecords:
                nextOps[lowestIdx] = None

    def getRecordIds(self):
        id_set = set()
        for nf in self._openReadFiles():
            nf.readAll()
            id_set.update(nf.records.keys())
        return id_set
    
    def findAllOfRecordsEntries(self, recordId):
        entries = []
        for nf in self._openReadFiles():
            nf.readAll()
            record = nf.records.get(recordId)
            if record is not None:
                entries.append(record)
        return entries

    def get(self, recordId, key=None):
        record = self.records.get(recordId)
        if record and key:
            return record[key]
        else:
            return record
    
    def set(self, recordId, data):
        nf = NexusFile(self._write_file_path)
        nf.set(recordId, data)
        nf.close()
    
    def inc(self, recordId, data):
        nf = NexusFile(self._write_file_path)
        nf.inc(recordId, data)
        nf.close()
    
    def dec(self, recordId, data):
        nf = NexusFile(self._write_file_path)
        nf.dec(recordId, data)
        nf.close()
    
    def delete(self, recordId, data):
        nf = NexusFile(self._write_file_path)
        nf.delete(recordId, data)
        nf.close()
