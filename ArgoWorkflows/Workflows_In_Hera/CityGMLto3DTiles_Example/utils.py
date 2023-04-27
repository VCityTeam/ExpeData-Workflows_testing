from hera.workflows import Container, models, Parameter, script


def whalesay_container_constructor():
    return Container(
        name="in",
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
def write_output(message):
    with open("/test", "w") as f_out:
        f_out.write(message)
