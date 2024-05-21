import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from hera_utils import parse_arguments
from environment import construct_environment

args = parse_arguments()
environment = construct_environment(args)

######################################
### The following is a copy of
### https://github.com/argoproj-labs/hera/blob/5.1.3/examples/workflows/dag_with_param_passing.py
from hera.workflows import DAG, Container, Parameter, Task, Workflow

with Workflow(generate_name="hera-dag-with-param-passing-", entrypoint="d") as w:
    out = Container(
        name="out",
        image="docker/whalesay",
        command=["cowsay", "Moo 42"],
        outputs=Parameter(name="x", value=42),
    )
    in_ = Container(
        name="in",
        image="docker/whalesay",
        command=["cowsay"],
        args=["{{inputs.parameters.a}}"],
        inputs=Parameter(name="a"),
    )
    with DAG(name="d"):
        t1 = Task(name="a", template=out)
        t2 = Task(
            name="b",
            template=in_,
            arguments=t1.get_parameter("x").with_name("a"),
        )
        t1 >> t2
w.create()
