import sys, os

sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition")
)
from hera_utils import hera_assert_version

hera_assert_version("5.6.0")
from pagoda_environment_definition import environment

####
from hera.workflows import Container, Workflow

with Workflow(generate_name="hello-", entrypoint="cowsay") as w:
    Container(
        name="cowsay", image="docker/whalesay", command=["cowsay", "Moo Hera"]
    )
w.create()
