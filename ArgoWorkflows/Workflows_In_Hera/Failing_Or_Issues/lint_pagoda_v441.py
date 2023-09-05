# Caveat emptor
# This is an oudated file (version 4.4.1) that is just kept here on
# historival purposes. Trying to fix this file would be pointless...

import sys, os

sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition")
)
from pagoda_cluster_definition import define_cluster

define_cluster()

####################################################################
# The following script (Hera version 4.1.1) will fail although it was
# part of the examples refer to
# https://github.com/argoproj-labs/hera/blob/4.4.1/examples/lint.py
#   
# Submitted for discussion to hera
# https://github.com/argoproj-labs/hera/discussions/571
####################################################################
from hera import Task, Workflow


def say(msg: str) -> None:
    print(msg)


with Workflow("lint-", generate_name=True) as w:
    Task("say", say, with_param=["Hello, world!"])

w.lint()
