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
    command=["cowsay"],
    args=["{{inputs.parameters.a}}"],
    inputs=Parameter(name="a"),
)


### Refer to
# https://github.com/argoproj-labs/hera/blob/5.1.3/examples/workflows/dag-with-script-output-param-passing.py
@script(
    outputs=[Parameter(name="a", value_from=models.ValueFrom(path="/test"))]
)
def convert_message_to_output_parameter(message):
    with open("/test", "w") as f_out:
        f_out.write(message)


def ip_http_check_container(cluster):
    return Container(
        name="iphttpcheck",
        image=cluster.docker_registry + "vcity/iphttpcheck:0.1",
        image_pull_policy=models.ImagePullPolicy.always,
        env_from=[
            # Assumes the corresponding config map is defined in the k8s cluster
            ConfigMapEnvFrom(name=cluster.configmap, optional=False),
        ],
        command=["python", "entrypoint.py"],
    )
