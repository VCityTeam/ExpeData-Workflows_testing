import sys, os

sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition")
)
from pagoda_cluster_definition import define_cluster

define_cluster()

####
from hera_utils import hera_check_version
hera_check_version("5.1.3")
from hera.shared._global_config import GlobalConfig

####
from hera.workflows import Container, Parameter, Steps, script, Task, Workflow

@script(image="python:alpine3.6")
def hello(message):
    print(message)

with Workflow(generate_name="hello-", entrypoint="hello-hello-hello") as w:
    # Callable container
    whalesay = Container(
      name="whalesay",
      inputs=[Parameter(name="message")],
      image="docker/whalesay",
      command=["cowsay"],
      args=["{{inputs.parameters.message}}"],
    )
    with Steps(name="hello-hello-hello") as s:
        Task = hello(name="hello-1", arguments={"message": "Hello 1."})
        whalesay(
            name="hello-2",
            arguments=[Parameter(name="message", value="Hello 2.")],
        )
        Task = hello(name="hello-3", arguments={"message": "Hello 3."})

w.create()

