import sys

__args = sys.argv[1:]


def getArg(arg, default=None):
    for val in __args:
        pair = val.split("=")
        if pair[0] == arg:
            return pair[1]
    return default
