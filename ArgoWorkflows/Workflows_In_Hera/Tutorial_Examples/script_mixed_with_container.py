import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from hera_utils import parse_arguments
from environment import construct_environment

args = parse_arguments()
environment = construct_environment(args)


####
from hera.workflows import Container, Parameter, Steps, script, Workflow


@script(image="python:alpine3.6")
def hello(message):
    print(message)


with Workflow(generate_name="script-mixed-with-container-", entrypoint="entry") as w:
    # Callable container
    whalesay = Container(
        name="whalesay",
        inputs=[Parameter(name="message")],
        image="docker/whalesay",
        command=["cowsay"],
        args=["{{inputs.parameters.message}}"],
    )
    with Steps(name="entry") as s:
        hello(name="hello-1", arguments={"message": "Hello 1."})
        whalesay(
            name="hello-2",
            arguments=[Parameter(name="message", value="Hello 2.")],
        )
        hello(name="hello-3", arguments={"message": "Hello 3."})

w.create()
