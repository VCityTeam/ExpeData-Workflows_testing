import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition"))
# Following import points Hera to the PAgoDA cluster (although the
# numertical environment variables is not used, this has some side effects)
from pagoda_environment_definition import environment


####
from hera_utils import hera_assert_version

hera_assert_version("5.6.0")

####
from hera.workflows import Container, Parameter, Steps, script, Workflow


@script(image="python:alpine3.6")
def hello(message):
    print(message)


with Workflow(generate_name="mixed-scripts-and-container-", entrypoint="entry") as w:
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
