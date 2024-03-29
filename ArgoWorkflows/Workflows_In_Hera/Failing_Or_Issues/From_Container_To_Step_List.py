# Submitted as discussion
# https://github.com/argoproj-labs/hera/discussions/727
import sys, os

sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition")
)

# Following import points Hera to the PAgoDA cluster (although the
# numertical environment variables is not used, this has some side effects)
from pagoda_environment_definition import environment

####
from hera_utils import hera_assert_version

hera_assert_version("5.6.0")
####

from hera.workflows import Container, Parameter, Step, Steps, Workflow

whalesay_container = Container(
    name="whalesay",
    inputs=[Parameter(name="message")],
    image="docker/whalesay",
    command=["cowsay"],
    args=["{{inputs.parameters.message}}"],
)

my_step = Step(
    name="inlined-step",
    inline=whalesay_container,
    arguments=[Parameter(name="message", value="Inline.")],
)

with Workflow(generate_name="workflow-name-", entrypoint="main") as w:
    with Steps(name="main") as s:
        # Following implicit Step constructor is OK
        whalesay_container(
            name="not-inlined-step",
            arguments=[Parameter(name="message", value="OK.")],
        )
        s.sub_steps.append(my_step)
        # FAIL: following line will faill with a message of the form
        # 'templates.main.steps failed to resolve {{inputs.parameters.message}}'}

w.create()
