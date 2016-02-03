"""
Miscellaneous utility functions for Pystump
"""

import sys
from flask import g
from datetime import datetime


def debug(*messages):
    if g.debug:
        sys.stderr.write("\n".join([str(m) for m in messages]))
    else:
        pass


def string_to_datetime(datestring):

    if not datestring:
        return None

    formats = (
        "%Y-%m-%d %H:%M",
        "%Y-%m-%dT%H:%M",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%m/%d/%Y %H:%M",
        "%m/%d/%Y %I:%M",
        "%-m/%-d/%Y %-I:%M"
    )

    for f in formats:
        try:
            dt = datetime.strptime(datestring, f)
        except ValueError:
            print("{} doesn't match {}".format(datestring, f))
            continue
        else:
            return dt

    return None
