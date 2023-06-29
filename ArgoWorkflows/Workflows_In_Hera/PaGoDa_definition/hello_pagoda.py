from hera.workflows import (
    ConfigMapEnvFrom,
    Container,
    DAG,
    ExistingVolume,
    script,
    Task,
    Workflow,
)
from pagoda_cluster_definition import define_cluster

cluster = define_cluster()


@script(
    env=[
        # Assumes the corresponding config map is defined at k8s level
        ConfigMapEnvFrom(config_map_name=cluster.configmap, optional=False)
    ]
)
def print_environment():
    import os
    import json

    print("Hera on PaGoDa can run python scripts...")
    print(
        "...and retrieve environment variables: ",
        json.dumps(dict(os.environ), indent=4),
    )
    print("Done.")


@script(
    inputs={"mount_point": "/vol"},
    volumes=[
        ExistingVolume(
            name="dummy", claim_name=cluster.volume_claim, mount_path="/vol"
        )
    ],
)
def list_files(mount_point: str):
    import os

    print("List of files", os.listdir(mount_point))
    print("Done.")


if __name__ == "__main__":
    with Workflow(generate_name="hera-on-pagoda-", entrypoint="main") as w:
        cowsayprint = Container(
            name="cowsayprint",
            image="docker/whalesay",
            env=[
                ConfigMapEnvFrom(
                    config_map_name=cluster.configmap, optional=False
                )
            ],
            command=["cowsay", "PaGoda can pull whalesay docker container."],
        )
        with DAG(name="main"):
            t1: Task = print_environment()
            t2 = Task(name="cowsayprint", template=cowsayprint)
            t3 = Task = list_files()
            t1 >> t2 >> t3
    w.create()
