from __future__ import annotations
from nexus.file import NexusFile, Record


from typing import Iterable
from enum import Enum
import os
import uuid


class NexusDB:
    dirname: str

    def __init__(self, dirname: str) -> None:
        self.dirname = dirname
        self._device = str(uuid.uuid1(uuid.getnode(), 0))[24:]    

        self._write_file_path = os.path.join(dirname, f"{self._device}.nexus")
        self._read_file_paths = [
            os.path.join(dirname, f"{filename}")
            for filename in os.listdir(dirname)
        ]
    
    def _openReadFiles(self):
        return [NexusFile(path, "r") for path in self._read_file_paths]
    
    def findAllOfRecordsEntries(self, recordId):
        entries = []
        for nf in self._openReadFiles():
            nf.readAll()
            record = nf.records.get(recordId)
            if record is not None:
                entries.append(record)
        return entries
    
    def combineRecord(self, recordId):
        entries = self.findAllOfRecordsEntries(recordId)
        record = Record()
        record.id = recordId
        for entry in entries:
            record.update(entry)
        return record
    
    def get(self, recordId, key=None):
        record = self.combineRecord(recordId)
        if key:
            return record[key]
        else:
            return record
