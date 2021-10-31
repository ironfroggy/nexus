import argparse
import base64
import sys
import uuid


RECORD_COMMANDS = [
    'create',
    'get',
    'set',
    'inc',
    'dec',
    'delete',
    'find',
]


def printRecord(nf, recordId, fields=None):
    if not fields:
        print(recordId)
    else:
        record = nf.get(recordId)
        values = "\t".join(str(record.get(field, "")) for field in fields)
        print(f"{recordId}\t{values}")


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
            # TODO: Parse filters and apply to record search
            from . import parser

            filters = []
            fields = []
            for string in recordArgs.pairs:
                p = parser.Parser(string)
                tokens = p.readUntilEnd(parser.EVAL_TOKEN_TYPES)
                if len(tokens) == 3:
                    _, key = tokens[0]
                    _, op = tokens[1]
                    _, value = tokens[2]
                    if op == '<':
                        filter = lambda rec, key=key, value=value: rec.get(key) < float(value)
                    elif op == '>':
                        filter = lambda rec, key=key, value=value: rec.get(key) > float(value)
                    elif op == '=':
                        filter = lambda rec, key=key, value=value: str(rec.get(key)) == str(value)
                    elif op == '!=':
                        filter = lambda rec, key=key, value=value: str(rec.get(key)) != str(value)
                    elif op == '~':
                        filter = lambda rec, key=key, value=value: str(value) in str(rec.get(key))
                    elif op == '~=':
                        filter = lambda rec, key=key, value=value: str(rec.get(key)).startswith(str(value))
                    elif op == '=~':
                        filter = lambda rec, key=key, value=value: str(rec.get(key)).endswith(str(value))
                    filters.append(filter)
                else:
                    fields.append(string)

            nf.readAll()
            from glob import fnmatch
            for recordId in nf.getRecordIds():
                if recordId.startswith(recordArgs.id):
                    ok = True
                    for filter in filters:
                        if not filter(nf.get(recordId)):
                            ok = False
                    if ok:
                        printRecord(nf, recordId, fields)
        elif args.command == 'create':
            if recordArgs.id.endswith('-'):
                rndPostfix = base64.encodebytes(uuid.uuid4().bytes)[:-3].decode('ascii')
                newId = recordArgs.id + rndPostfix
            else:
                newId = recordArgs.id 
            nf.set(newId, data)
        elif args.command == 'set':
            nf.set(recordArgs.id, data)
        elif args.command == 'inc':
            nf.inc(recordArgs.id, data)
        elif args.command == 'dec':
            nf.dec(recordArgs.id, data)
        elif args.command == 'delete':
            nf.delete(recordArgs.id, data)
        elif args.command == 'get':
            nf.readAll()
            if data:
                for key in data:
                    print(nf.get(recordArgs.id, key))
            else:
                record = nf.get(recordArgs.id)
                printRecord(nf, recordArgs.id, data.keys())
                # for key in record:
                #     print(key, '=', record[key])
    else:
        recordArgs = None

