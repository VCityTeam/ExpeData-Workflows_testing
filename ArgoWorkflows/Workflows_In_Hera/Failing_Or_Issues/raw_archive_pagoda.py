import sys, os

sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition")
)
from pagoda_cluster_definition import define_cluster

cluster = define_cluster()

#################################################################
# The following trial of returning a string through a RawArtifact
# will error with "You need to configure artifact storage".
# But the configuration of artifact storage is far from trivial. And the
# documentation page
# https://argoproj.github.io/argo-workflows/configure-artifact-repository/
# doesn't illustrate how to use RawFactory  :-(
#################################################################

from hera import ConfigMapEnvFrom, ExistingVolume, RawArtifact, Task, Workflow


def consume(msg: str):
    print(f"Message was: {msg}")


with Workflow("rawartifact-", generate_name=True) as w:
    t1 = Task(
        "cowsayprint",
        image="docker/whalesay",
        env=[
            ConfigMapEnvFrom(config_map_name=cluster.configmap, optional=False)
        ],
        command=[
            "cowsay",
            "Just trying to transmit a string to another task...",
        ],
        volumes=[
            ExistingVolume(
                name=cluster.volume_claim,
                mount_path="/persistedVolume",
            )
        ],
        outputs=[RawArtifact("msg", path="/persistedVolume", data="ball")],
    )
    t2 = Task("c", consume, inputs=[t1.get_artifact("msg")])
    t1 >> t2

w.create()
