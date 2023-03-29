import sys, os

sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "Workflow_PaGoDa_definition")
)
import types
from pagoda_cluster_definition import define_cluster

cluster = define_cluster()


########
parameters = types.SimpleNamespace(
    borough="LYON_8EME",
    pattern="BATI",
    experiment_output_dir="junk",
    vintage="2012",
    persistedVolume="/tmp",
)

results_dir = os.path.join(
    parameters.experiment_output_dir,
    "stage_1",
    parameters.vintage,
    parameters.borough + "_" + parameters.vintage,
)

##########
from hera import ConfigMapEnvFrom, ImagePullPolicy, Task, Workflow


def disk_usage():
    import os

    print(f'Available storage:\n{os.popen("df -h").read()}')


def define_workflow():
    with Workflow("collect-", generate_name=True) as w:
        Task("firsttask", disk_usage)
        Task(
            "second",
            image=cluster.docker_registry + "vcity/collect_lyon_data:0.1",
            image_pull_policy=ImagePullPolicy.Always,
            env=[
                # Assumes the corresponding config map is defined in the k8s cluster
                ConfigMapEnvFrom(
                    config_map_name=cluster.configmap, optional=False
                )
            ],
            command=[
                "python3",
                # inputs=[
                "entrypoint.py",
                "--borough",
                parameters.borough,
                "--pattern",
                parameters.pattern,
                "--results_dir",
                results_dir,
                "--vintage",
                parameters.vintage,
                "--volume",
                parameters.persistedVolume,
            ],
        )
    w.create()


define_workflow()
