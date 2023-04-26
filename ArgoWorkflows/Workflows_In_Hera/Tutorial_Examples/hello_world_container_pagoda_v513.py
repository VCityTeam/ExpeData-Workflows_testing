import sys, os

sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition")
)
from pagoda_cluster_definition import define_cluster

define_cluster()

####
from hera_utils import hera_assert_version

hera_assert_version("5.1.3")
from hera.shared._global_config import GlobalConfig

####
from hera.workflows import Container, Workflow

with Workflow(generate_name="hello-", entrypoint="cowsay") as w:
    Container(
        name="cowsay", image="docker/whalesay", command=["cowsay", "Moo Hera"]
    )
w.create()
