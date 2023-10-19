### Cluster specific
import sys, os

sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition")
)
from pagoda_environment_definition import environment

### Some Hera helpers and checks...
from hera_utils import hera_assert_version, hera_clear_workflow_template

hera_assert_version("5.6.0")

### The following code is a copy of
### https://github.com/argoproj-labs/hera/blob/5.1.3/examples/workflows/steps_with_callable_container.py
from hera.workflows import Container, Parameter, Steps, Workflow

with Workflow(
    generate_name="steps-with-callable-container",
    entrypoint="hello-hello-hello",
) as w:
    whalesay = Container(
        name="whalesay",
        inputs=[Parameter(name="message")],
        image="docker/whalesay",
        command=["cowsay"],
        args=["{{inputs.parameters.message}}"],
    )

    with Steps(name="hello-hello-hello") as s:
        whalesay(
            name="hello1",
            arguments=[Parameter(name="message", value="hello1")],
        )

        with s.parallel():
            whalesay(
                name="hello2a",
                arguments=[Parameter(name="message", value="hello2a")],
            )
            whalesay(
                name="hello2b",
                arguments=[Parameter(name="message", value="hello2b")],
            )
w.create()
