import sys, os

sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition")
)
from pagoda_environment_definition import environment


#################################################################
# The following trial of returning a string through a RawArtifact
# dates back to version 4.1.1. The following is an adaptation trial
# to Hera version 4.6.0. that will fail at submission stage (there is
# something wrong with writing "consume(t1.get_artifact("msg"))").
# Besides the configuration of artifact storage is far from trivial. And
# the documentation page
# https://argoproj.github.io/argo-workflows/configure-artifact-repository/
# doesn't illustrate how to use RawFactory  :-(
#################################################################

from hera.workflows import (
    ConfigMapEnvFrom,
    Container,
    DAG,
    ExistingVolume,
    RawArtifact,
    script,
    Task,
    Workflow,
)


@script()
def consume(msg: str):
    print(f"Message was: {msg}")


with Workflow(generate_name="rawartifact-") as w:
    cowsayprint = Container(
        name="cowsayprint",
        image="docker/whalesay",
        env=[
            ConfigMapEnvFrom(
                config_map_name=environment.cluster.configmap,
                optional=False,
            )
        ],
        command=[
            "cowsay",
            "Just trying to transmit a string to another task...",
        ],
        volumes=[
            ExistingVolume(
                name="dummy",
                claim_name=environment.persisted_volume.claim_name,
                mount_path=environment.persisted_volume.mount_path,
            )
        ],
        outputs=[
            RawArtifact(
                name="msg",
                path=environment.persisted_volume.mount_path,
                data="ball",
            )
        ],
    )
    with DAG(name="main"):
        t1 = Task(name="cowsayprint", template=cowsayprint)
        t2 = consume(t1.get_artifact("msg"))
        t1 >> t2

w.create()
