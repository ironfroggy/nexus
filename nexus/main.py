import argparse
import sys


RECORD_COMMANDS = [
    'get',
    'set',
    'inc',
    'dec',
    'find',
]


def printRecord(nf, recordId, fields=None):
    if fields is None:
        print(recordId)
    else:
        record = nf.get(recordId)
        print("\t".join(record.get(field, "") for field in fields))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('path', type=str, action='store')
    parser.add_argument('command', type=str, action='store')
    args, remaining = parser.parse_known_args()

    if args.command in RECORD_COMMANDS:
        recordParser = argparse.ArgumentParser()
        parser.add_argument('id', type=str, action='store')
        parser.add_argument('pairs', type=str, nargs='*')
        recordArgs, remaining = parser.parse_known_args()

        data = {}
        for pair in recordArgs.pairs:
            try:
                key, value = pair.split('=', 1)
            except ValueError:
                key = pair
                value = True
            data[key] = value

        from nexus.file import NexusFile
        from nexus.db import NexusDB

        if args.command == 'get':
            mode = 'r'
        else:
            mode = 'a'

        nf = NexusDB(args.path)
        if args.command == 'find':
            from glob import fnmatch
            for recordId in nf.getRecordIds():
                if recordId.startswith(recordArgs.id):
                    printRecord(nf, recordId, recordArgs.pairs)
        elif args.command == 'set':
            nf.set(recordArgs.id, data)
        elif args.command == 'get':
            if data:
                for key in data:
                    print(nf.get(recordArgs.id, key))
            else:
                record = nf.get(recordArgs.id)
                for key in record:
                    print(key, '=', record[key])
    else:
        recordArgs = None
