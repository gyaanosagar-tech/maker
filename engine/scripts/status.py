#!/usr/bin/env python3
"""What can this machine actually do? Prints the truth, not a wish list."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "core"))
import tools
print(tools.report())
