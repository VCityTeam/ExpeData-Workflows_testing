import os
from hera import (
    ConfigMapEnvFrom,
    ExistingVolume,
    ImagePullPolicy,
    Parameter,
    Task,
    ValueFrom,
    Workflow,
)


def collect_task(cluster, parameters, output_dir: str):
    results_dir = os.path.join(
        parameters.experiment_output_dir,
        output_dir,
        parameters.vintage,
        parameters.borough + "_" + parameters.vintage,
    )
    output_value_path = os.path.join(
        parameters.persistedVolume,
        results_dir,
        "Resulting_Filenames.txt",
    )
    task = Task(
        "collect",
        image=cluster.docker_registry + "vcity/collect_lyon_data:0.1",
        image_pull_policy=ImagePullPolicy.Always,
        env=[
            # Assumes the corresponding config map is defined in the k8s cluster
            ConfigMapEnvFrom(config_map_name=cluster.configmap, optional=False)
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
        volumes=[
            ExistingVolume(
                name=cluster.volume_claim,
                mount_path=parameters.persistedVolume,
            )
        ],
        outputs=[
            Parameter("msg", value_from=ValueFrom(path=output_value_path))
        ],
    )
    return task


if __name__ == "__main__":
    import sys, os

    sys.path.append(
        os.path.join(
            os.path.dirname(__file__), "..", "Workflow_PaGoDa_definition"
        )
    )
    from pagoda_cluster_definition import define_cluster
    from input_2012_tiny_import_dump import parameters

    def consume(msg: str):
        print(f"Message was: {msg}")

    cluster = define_cluster()
    with Workflow("fullcollect-", generate_name=True) as w:
        collect_t = collect_task(cluster, parameters, output_dir="stage_1")
        t2 = Task("c", consume, inputs=[collect_t.get_parameter("msg")])
        collect_t >> t2
    w.create()