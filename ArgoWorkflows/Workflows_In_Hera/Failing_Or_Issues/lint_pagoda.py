import sys, os

sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition")
)
from pagoda_cluster_definition import define_cluster

define_cluster()

####################################################################
# The following script will fail although it is part of the examples
# Submitted for discussion to hera
# https://github.com/argoproj-labs/hera/discussions/571
####################################################################
from hera import Task, Workflow


def say(msg: str) -> None:
    print(msg)


with Workflow("lint-", generate_name=True) as w:
    Task("say", say, with_param=["Hello, world!"])

w.lint()
