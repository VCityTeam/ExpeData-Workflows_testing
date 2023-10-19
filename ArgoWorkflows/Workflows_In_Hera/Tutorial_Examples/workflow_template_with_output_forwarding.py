### Cluster specific
import sys, os

sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition")
)
from pagoda_environment_definition import environment

# Some Hera helpers and checks...
from hera_utils import hera_assert_version, hera_clear_workflow_template

hera_assert_version("5.6.0")


### The following is cluster independent (well almost)
# Note: this example was submitted to the community, refer to
# https://github.com/argoproj-labs/hera/discussions/732

from hera.workflows import (
    DAG,
    models as m,
    Parameter,
    script,
    Task,
    Workflow,
    WorkflowTemplate,
)
from hera.expr import g as expr


@script()
def increment(a: str):
    try:
        a_int = int(a)
        print(a_int + 1)
    except ValueError:
        print("Unable to convert ", a, " to an integer. Task failed.")
        raise Exception("failure")  # Fail task at AW level


@script()
def print_messsage(msg: str):
    print("Received: ", msg)


with WorkflowTemplate(
    name="increment-workflow-template",
    entrypoint="increment-template",
) as w:
    with DAG(
        name="increment-template",
        inputs=Parameter(name="value"),
    ) as main_dag:
        t1: Task = increment(
            name="increment-once",
            arguments=[
                Parameter(name="a", value="{{inputs.parameters.value}}")
            ],
        )
        t2 = increment(
            name="increment-twice",
            # Just to illustrate the syntax when _within_ a DAG template
            arguments=[Parameter(name="a", value=t1.result)],
        )
        t1 >> t2
        # And now the syntax to transmit a result coming from this DAG
        # to the calling context (aka "outputs forwarding").
        # First part: register the output as the template output.
        expression = expr.tasks["increment-twice"].outputs.result
        main_dag.outputs = [
            Parameter(
                name="computed", value_from={"expression": str(expression)}
            )
        ]
hera_clear_workflow_template(environment.cluster, "increment-workflow-template")
w.create()


with Workflow(
    generate_name="workflow-template-with-output-",
    entrypoint="main",
) as w:
    with DAG(name="main"):
        t1 = Task(
            name="call-workflowtemplate",
            template_ref=m.TemplateRef(
                name="increment-workflow-template",
                template="increment-template",
            ),
            arguments=Parameter(name="value", value=40),
        )

        t2 = print_messsage(
            name="print-result",
            arguments=Parameter(
                name="msg",
                # Second part: get your hands on the WorkflowTemplate output
                value="{{tasks.call-workflowtemplate.outputs.parameters.computed}}",
            ),
        )
        t1 >> t2
w.create()

### References
# * How Workflow Templates can have/forward outputs:
#   https://stackoverflow.com/questions/70897648/unable-to-pass-output-parameters-from-one-workflowtemplate-to-a-workflow-via-ano
# * For an example of value_from.expression
#   https://github.com/argoproj-labs/hera/blob/5.1.3/examples/workflows/dag_conditional_parameters.py
# * Passing arguments
#   https://github.com/argoproj-labs/hera/blob/5.1.3/examples/workflows/dag_with_script_param_passing.py
