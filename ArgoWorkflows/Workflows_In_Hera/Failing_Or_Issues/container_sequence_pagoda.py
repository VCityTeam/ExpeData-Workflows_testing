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

#########################################################################
from hera.workflows import Container, Workflow

with Workflow(
    generate_name="containers-sequence-fail-1-", entrypoint="whalesay-1"
) as w:
    # This Containeer is enacted at runtime...
    Container(
        name="whalesay-1",
        image="docker/whalesay",
        command=["cowsay"],
        args=["Yeah"],
    )
    # ...but NOT this one !
    Container(
        name="whalesay-2",
        image="docker/whalesay",
        command=["cowsay"],
        args=["Yeah not done"],
    )

w.create()
