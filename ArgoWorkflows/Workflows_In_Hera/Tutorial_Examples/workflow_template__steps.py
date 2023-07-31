### Cluster specific
import sys, os

sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition")
)
from pagoda_cluster_definition import define_cluster

cluster = define_cluster()

### Some Hera helpers and checks...
from hera_utils import hera_assert_version, hera_clear_workflow_template

hera_assert_version("5.6.0")

### The following is cluster independent (well almost)

from hera.workflows import (
    Container,
    models as m,
    Parameter,
    Step,
    Steps,
    Workflow,
    WorkflowTemplate,
)

### The following WorkflowTemplate is an adapted copy of
### https://github.com/argoproj-labs/hera/blob/5.1.3/examples/workflows/upstream/workflow_event_binding__event_consumer_workflowtemplate.py
with WorkflowTemplate(
    name="workflow-template-whalesay-template",
    entrypoint="whalesay-template",
    # CHANGED: the following line didn't seem to be used (didn't appear in the
    # generated yaml).
    #     arguments=Parameter(name="message", value="hello"),
    # BTW check that AW's workflow templates does indeed accept such an
    # "arguments" entry (and what the associated semantics could/would be)
) as w:
    say = Container(
        name="argosay",
        # CHANGED: because the cluster in behind a seclusive/autistic firewall
        # there is no access to Docker Hub (hub.docker.com)
        #    image="argoproj/argosay:v2",
        image=cluster.docker_registry + "vcity/argosay:v2",
        image_pull_policy=m.ImagePullPolicy.always,
        inputs=[
            Parameter(name="message"),
        ],
        args=["echo", "{{inputs.parameters.message}}"],
    )
    with Steps(
        name="whalesay-template",
        # CHANGED: had to add an inputs entry for whalesay-template to accept
        # arguments
        inputs=Parameter(name="message"),
    ):
        say(
            name="a",
            arguments=[
                Parameter(
                    name="message", value="{{inputs.parameters.message}}"
                )
            ],
        )
# CHANGED: if we want the workflow script (that is this file) to be run once
# edited we need to remove a previously submitted version of this workflow
# template (or AW server will reject this new version with a name conflict):
hera_clear_workflow_template(cluster, "workflow-template-whalesay-template")

# CHANGED: following line added for the workflow templae to be registered
w.create()

### The following Workflow is a copy of
### https://github.com/argoproj-labs/hera/blob/5.1.3/examples/workflows/upstream/workflow_template__steps.py
with Workflow(
    generate_name="workflow-template-steps-",
    entrypoint="hello-hello-hello",
) as w:
    with Steps(name="hello-hello-hello") as s:
        Step(
            name="hello1",
            template_ref=m.TemplateRef(
                name="workflow-template-whalesay-template",
                template="whalesay-template",
            ),
            arguments=Parameter(name="message", value="hello1"),
        )
        with s.parallel():
            Step(
                name="hello2a",
                template_ref=m.TemplateRef(
                    # CHANGED: the original script made reference to
                    #     name="workflow-template-inner-steps",
                    #     template="inner-steps"
                    # that just didn't seem to be resolved. It would trigger an
                    # error message of the form:
                    #     'templates.hello-hello-hello.steps[1].hello2a template
                    #     reference workflow-template-inner-steps.inner-steps
                    #     not found'
                    name="workflow-template-whalesay-template",
                    template="whalesay-template",
                ),
                arguments=Parameter(name="message", value="hello2a"),
            )
            Step(
                name="hello2b",
                template_ref=m.TemplateRef(
                    name="workflow-template-whalesay-template",
                    template="whalesay-template",
                ),
                arguments=Parameter(name="message", value="hello2b"),
            )
# CHANGED: following line added for the workflow to run
w.create()
