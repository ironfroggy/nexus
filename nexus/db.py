from __future__ import annotations
from nexus import NexusBlock

from typing import Iterable
from enum import Enum


class BlockType(Enum):
    META = 0
    DATA = 1
    INDEX = 2


class NexusFile:
    path: str

    def __init__(self, path):
        self.path = path
        self.blockSize = 512
    
    def readBlock(self, index) -> bytes:
        f = open(self.path, "rb")
        f.seek(self.blockSize * index)
        return f.read(self.blockSize)
    
    def addBlock(self, blockData):
        assert self.blockSize == len(blockData)
        f = open(self.path, "ab")
        f.write(blockData)
    
    def iterPages(self): # -> Iterable[NexusPage]:
        raise NotImplementedError()
    
    def createPage(self, title): # -> NexusPage:
        raise NotImplementedError()


class NexusFileBlock:
    nexusFile: NexusFile
    index: int
    blockType: BlockType


class MetaBlock(NexusBlock):
    blockType = BlockType.META

    nexusVersion: int = 1
    nexusSchema: int = 1

    def toBytes(self):
        return [
            (self.nexusVersion, "")
        ]
