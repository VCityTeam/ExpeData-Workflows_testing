import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', "PaGoDa_definition"))
from pagoda_cluster_definition import define_cluster

define_cluster()

# The following is a copy of 
# https://github.com/argoproj-labs/hera-workflows/blob/4.4.1/examples/coin_flip.py

from hera import Task, Workflow


def random_code():
    import random
    res = "heads" if random.randint(0, 1) == 0 else "tails"
    print(res)


def heads():
    print("it was heads")


def tails():
    print("it was tails")


# assumes you used `hera.set_global_token` and `hera.set_global_host` so that the workflow can be submitted
with Workflow("coin-flip-", generate_name=True) as w:
    r = Task("r", random_code)
    h = Task("h", heads)
    t = Task("t", tails)

    h.on_other_result(r, "heads")
    t.on_other_result(r, "tails")

w.create()
