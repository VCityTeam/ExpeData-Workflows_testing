from hera import Workflow, ConfigMapEnvFrom, Task
from pagoda_cluster_definition import define_cluster

cluster = define_cluster()


def print_environment():
    import os
    import json

    print("Hera on PaGoDa can run python scripts...")
    print(
        "...and retrieve environment variables: ",
        json.dumps(dict(os.environ), indent=4),
    )
    print("Done.")


def define_workflow():
    with Workflow("hera-on-pagoda-", generate_name=True) as w:
        Task(
            "printpythonenv",
            print_environment,
            env=[
                # Assumes the corresponding config map is defined at k8s level
                ConfigMapEnvFrom(
                    config_map_name=cluster.configmap, optional=False
                )
            ],
        )
        Task(
            "cowsayprint",
            image="docker/whalesay",
            env=[
                ConfigMapEnvFrom(
                    config_map_name=cluster.configmap, optional=False
                )
            ],
            command=["cowsay", "PaGoda can pull whalesay docker container."],
        )
    w.create()


if __name__ == "__main__":
    define_workflow()
