import uuid
from hera.workflows import (
    ConfigMapEnvFrom,
    Container,
    models,
    Parameter,
    script,
)


whalesay_container = Container(
    name="whalesay",
    image="docker/whalesay:latest",
    inputs=Parameter(name="message"),
    command=["cowsay"],
    args=["{{inputs.parameters.message}}"],
)


### Refer to
# https://github.com/argoproj-labs/hera/blob/5.1.3/examples/workflows/dag-with-script-output-param-passing.py
@script(outputs=[Parameter(name="message", value_from=models.ValueFrom(path="/test"))])
def convert_message_to_output_parameter(message):
    with open("/test", "w") as f_out:
        f_out.write(message)


@script()
def print_list_script(messages: list):
    print(messages)


@script()
def print_script(message):
    print(message)


def ip_http_check_container(environment):
    return Container(
        name="iphttpcheck",
        image=environment.cluster.docker_registry + "vcity/iphttpcheck:0.1",
        image_pull_policy=models.ImagePullPolicy.always,
        env_from=[
            # Assumes the corresponding config map is defined in the k8s cluster
            ConfigMapEnvFrom(name=environment.cluster.configmap, optional=False),
        ],
        command=["python", "entrypoint.py"],
    )


def get_new_container_identifier():
    # FIXME: Is this guaranteed to be without collisions ? In other terms
    # is it possible to generate two identical identifiers ?
    # NOTE (AW constrain): container names must be a lowercase RFC 1123
    # subdomain that must consist of lower case alphanumeric characters,
    # '-' or '.', and must start and end with an alphanumeric character
    # (e.g. 'example.com', regex used for validation is
    # '[a-z0-9]([-a-z0-9]*[a-z0-9])?(\.[a-z0-9]([-a-z0-9]*[a-z0-9])?)*')
    return uuid.uuid4().hex[:6].lower()
