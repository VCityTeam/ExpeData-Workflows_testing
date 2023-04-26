from hera.workflows import Container, Parameter


def whalesay_container_constructor():
    return Container(
        name="in",
        image="docker/whalesay:latest",
        command=["cowsay"],
        args=["{{inputs.parameters.a}}"],
        inputs=Parameter(name="a"),
    )
