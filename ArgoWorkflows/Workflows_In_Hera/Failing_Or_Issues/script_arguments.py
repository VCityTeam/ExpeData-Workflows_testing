import sys, os

sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition")
)

###
# Refer to discussion
# https://github.com/argoproj-labs/hera/discussions/738
from hera.workflows import DAG, Parameter, script, Workflow


@script(
    image="{{inputs.parameters.image}}",
)
def test():  # FAILS at submission stage with
    #   failed to resolve {{inputs.parameters.image}}`
    # but the following definitions smoothly accepts submission
    # def test(image):
    ...


with Workflow(generate_name="fail-", entrypoint="main") as w:
    with DAG(name="main"):
        t1 = test(
            arguments=Parameter(
                name="image",
                value="pyton:3.9-alpine",
            ),
        )
w.create()
