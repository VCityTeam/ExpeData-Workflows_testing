import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from hera_utils import parse_arguments
from environment import construct_environment

args = parse_arguments()
environment = construct_environment(args)

##################################################################
#  The following is a copy of
# https://github.com/argoproj-labs/hera/blob/5.1.3/examples/workflows/dag-with-script-output-param-passing.py
from hera.workflows import (
    DAG,
    Parameter,
    Task,
    Workflow,
    models as m,
    script,
)


@script(outputs=[Parameter(name="a", value_from=m.ValueFrom(path="/test"))])
def out():
    with open("/test", "w") as f_out:
        f_out.write("test")


@script()
def in_(a):
    print(a)


with Workflow(
    generate_name="hera-dag-with-script-output-param-passing-", entrypoint="d"
) as w:
    with DAG(name="d"):
        t1: Task = out()
        t2 = in_(arguments=t1.get_parameter("a"))
        t1 >> t2
w.create()
