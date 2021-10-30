from time import time_ns
from datetime import datetime


def timestamp():
    return time_ns()

def from_timestamp():
    return datetime.fromtimestamp(int(1_000_000_000))
