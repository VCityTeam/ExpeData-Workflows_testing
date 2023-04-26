import sys, os

sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition")
)
from pagoda_cluster_definition import define_cluster

cluster = define_cluster()

####
from hera_utils import hera_assert_version

hera_assert_version("5.1.3")

#########################################################################
# This is a simplification of
# https://github.com/argoproj-labs/hera/blob/5.1.3/examples/workflows/steps_with_callable_container.py
from hera.workflows import Container, Steps, Parameter, Workflow

with Workflow(
    generate_name="containers-sequence-with-steps-",
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
