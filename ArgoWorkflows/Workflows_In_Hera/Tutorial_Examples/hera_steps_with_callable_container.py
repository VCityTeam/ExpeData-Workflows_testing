import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from hera_utils import parse_arguments
from environment import construct_environment

args = parse_arguments()
environment = construct_environment(args)

#########################################################################
# This is a simplification of
# https://github.com/argoproj-labs/hera/blob/5.1.3/examples/workflows/steps_with_callable_container.py
from hera.workflows import Container, Steps, Parameter, Workflow

with Workflow(
    generate_name="hera-steps-with-collable-container-",
    entrypoint="sequence-entry",
) as w:
    whalesay = Container(  # Container must be callable
        name="whalesay",
        inputs=[Parameter(name="message")],
        image="docker/whalesay",
        command=["cowsay"],
        args=["{{inputs.parameters.message}}"],
    )
    with Steps(name="sequence-entry") as s:
        whalesay(
            name="hello-1",
            arguments=[Parameter(name="message", value="Hello 1.")],
        )
        whalesay(
            name="hello-2",
            arguments=[Parameter(name="message", value="Hello 2.")],
        )

w.create()
