import sys, os

sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition")
)
from pagoda_cluster_definition import define_cluster

cluster = define_cluster()

from hera_utils import hera_assert_version

hera_assert_version("5.6.0")

####################################
# Following code submitted to Hera: refer to
# https://github.com/argoproj-labs/hera/discussions/561
####################################

from hera.workflows import DAG, Parameter, script, Task, Workflow


@script()
def dummy():
    ...


@script()
def consume(msg: str):
    print(f"Message was: {msg}")


with Workflow(generate_name="io-") as w:
    with DAG(name="main"):
        t1: Task = dummy(
            name="t1",
            # Ditch attempt to piggyback some message in the outputs, when
            # the original template didn't have any output (don't ask about
            # the use case since I have to admit it's quite circumvolved).
            outputs=[Parameter(name="msg", value="some_valuable_message")],
        )
        t2: Task = consume(arguments={"msg": t1.get_parameter("msg")})

        t1 >> t2

w.create()
