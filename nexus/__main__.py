import argparse
import sys


RECORD_COMMANDS = [
    'get',
    'set',
    'inc',
    'dec',
]

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

    if args.command == 'get':
        mode = 'r'
    else:
        mode = 'a'

    nf = NexusFile(args.path, mode)
    if args.command == 'set':
        nf.writeRecord(recordArgs.id, data)
    elif args.command == 'get':
        nf.readAll()
        if data:
            for key in data:
                if key in nf.records[recordArgs.id]:
                    print(nf.records[recordArgs.id][key])
        else:
            for key in nf.records[recordArgs.id]:
                print(key, '=', nf.records[recordArgs.id][key])
else:
    recordArgs = None

