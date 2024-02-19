####
import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition"))
from pagoda_environment_definition import environment

####
from hera_utils import hera_assert_version

hera_assert_version("5.6.0")

######################################
### The following is a copy of
### https://github.com/argoproj-labs/hera/blob/5.1.3/examples/workflows/dag_with_param_passing.py
from hera.workflows import DAG, Container, Parameter, Task, Workflow

with Workflow(generate_name="dag-container-with-item-", entrypoint="dag") as w:
    # Callable container
    whalesay = Container(
        name="whalesay",
        inputs=[
            Parameter(name="greeting"),
            Parameter(name="name"),
        ],
        image="docker/whalesay",
        command=["cowsay"],
        args=["{{inputs.parameters.greeting}} {{inputs.parameters.name}}"],
    )

    with DAG(name="dag"):
        t1 = Task(
            name="wellcome-assembly",
            template=whalesay,
            arguments={"greeting": "Wellcome", "name": "new members"},
        )
        t2 = Task(
            name="hello-members",
            template=whalesay,
            arguments={"greeting": "Hello", "name": "{{item}}"},
            with_items=["John", "Suzy"],
        )
        t1 >> t2
w.create()
