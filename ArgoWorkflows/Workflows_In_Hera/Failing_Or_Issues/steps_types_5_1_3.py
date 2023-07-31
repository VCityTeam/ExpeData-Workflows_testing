# This will fail with message
#   hera.exceptions.InternalServerError: Server returned status code 500 with
#   message:
#  `templates.hello-hello-hello.steps[3].name 'list-of-step-1' is not unique`
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
# The following is a copy of
# https://github.com/argoproj-labs/hera/blob/5.1.3/examples/workflows/steps_types.py
from hera.workflows import (
    Container,
    Parameter,
    Step,
    Steps,
    Workflow,
    models as m,
)

my_step = Step(
    name="manually-adding-my-step",
    template="whalesay",
    arguments=[Parameter(name="message", value="hello1")],
)


my_steps = [
    Step(
        name="list-of-step-1",
        template="whalesay",
        arguments=[Parameter(name="message", value="hello1")],
    ),
    Step(
        name="list-of-step-2",
        template="whalesay",
        arguments=[Parameter(name="message", value="hello1")],
    ),
]

with Workflow(
    generate_name="steps-types-",
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
        # Manually add a step defined elsewhere
        s.sub_steps.append(my_step)

        # Manually add a list of steps defined elsewhere as sequential steps
        s.sub_steps.extend(my_steps)

        # Manually add a list of steps defined elsewhere as parallel steps
        s.sub_steps.append(my_steps)

        # Add a step to s implicitly through init
        Step(
            name="implicitly-adding-step-on-init",
            template="whalesay",
            arguments=[Parameter(name="message", value="hello1")],
        )

        # Manually add a model WorkflowStep to s
        s.sub_steps.append(
            m.WorkflowStep(
                name="model-workflow-step",
                template="whalesay",
                arguments=m.Arguments(
                    parameters=[
                        Parameter(name="message", value="hello-model1")
                    ]
                ),
            )
        )

        with s.parallel() as ps:
            # Add a step to ps implicitly through init
            Step(
                name="parallel-step-1",
                template="whalesay",
                arguments=[Parameter(name="message", value="hello2a")],
            )

            # Manually add a model WorkflowStep to ps
            ps.sub_steps.append(
                m.WorkflowStep(
                    name="parallel-step-2-model-workflow-step",
                    template="whalesay",
                    arguments=m.Arguments(
                        parameters=[
                            Parameter(name="message", value="hello-model2b")
                        ]
                    ),
                )
            )

    # Fully falling back to add a model Template containing a model WorkflowStep
    w.templates.append(
        m.Template(
            name="my-model-template",
            steps=[
                [
                    m.WorkflowStep(
                        name="model-template-workflow-step",
                        template="whalesay",
                        arguments=m.Arguments(
                            parameters=[
                                Parameter(
                                    name="message",
                                    value="hello-model-template",
                                )
                            ]
                        ),
                    )
                ]
            ],
        )
    )
w.create()
