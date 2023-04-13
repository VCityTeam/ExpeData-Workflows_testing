import sys, os

sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition")
)
from pagoda_cluster_definition import define_cluster

cluster = define_cluster()

####################################
# Following code submitted to Hera: refer to
# https://github.com/argoproj-labs/hera/issues/559
####################################

from hera import Parameter, Task, ValueFrom, Workflow


def dummy():
    ...


def consume(msg: str):
    print(f"Message was: {msg}")


with Workflow("io") as w:
    t1 = Task(
        "d", dummy, outputs=[Parameter("msg", value="some_valuable_message")]
    )
    t2 = Task("c", consume, inputs=[t1.get_parameter("msg")])
    t1 >> t2

w.create()
