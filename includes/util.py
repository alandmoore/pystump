"""
Miscellaneous utility functions for Pystump
"""

import sys
from flask import g


def debug(*messages):
    if g.debug:
        sys.stderr.write("\n".join([str(m) for m in messages]))
    else:
        pass
