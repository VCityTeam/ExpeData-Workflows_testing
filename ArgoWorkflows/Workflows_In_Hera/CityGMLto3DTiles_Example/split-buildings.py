import os
from write_output import write_output_task

from hera import (
    ConfigMapEnvFrom,
    ExistingVolume,
    ImagePullPolicy,
    Parameter,
    Task,
    Workflow,
)


def split_buildings_task(
    cluster,
    workflow_parameters,
    input_filename: str,  # Absolute file path
    output_dir: str,  # Absolute directory path
    output_filename: str,  # Filename (relative to output_dir)
):
    output_dir = os.path.join(workflow_parameters.persistedVolume, output_dir)
    treatment_task = Task(
        "split-buildings",
        image=cluster.docker_registry + "vcity/3duse:0.1",
        image_pull_policy=ImagePullPolicy.IfNotPresent,
        working_dir="/root/3DUSE/Build/src/utils/cmdline/",
        env=[
            # Assumes the corresponding config map is defined in the k8s cluster
            ConfigMapEnvFrom(config_map_name=cluster.configmap, optional=False)
        ],
        command=[
            "splitCityGMLBuildings",
            "--input-file",
            os.path.join(workflow_parameters.persistedVolume, input_filename),
            "--output-file",
            output_filename,
            "--output-dir",
            output_dir,
        ],
        volumes=[
            ExistingVolume(
                name=cluster.volume_claim,
                mount_path=parameters.persistedVolume,
            )
        ],
    )
    ### Add a post-treatment defining a file, to pass the output filename
    # to the next task, because the original `split-buildings` forgot to do
    # so. Additionnaly the form taken to fix that `split-buildings` shortcoming
    # takes the form of a kludgy trick because Hera doesn't yet offer the
    # `Value()` class.
    output_value_path = os.path.join(output_dir, output_filename)
    post_treatement_task = write_output_task(cluster, output_value_path)
    treatment_task >> post_treatement_task
    return post_treatement_task


if __name__ == "__main__":
    import sys, os

    sys.path.append(
        os.path.join(
            os.path.dirname(__file__), "..", "PaGoDa_definition"
        )
    )
    from pagoda_cluster_definition import define_cluster
    from input_2012_tiny_import_dump import parameters

    def consume(msg: str):
        print(f"Resulting filenames: {msg}")

    cluster = define_cluster()
    with Workflow("splitbuildings-", generate_name=True) as w:
        split_buildings_t = split_buildings_task(
            cluster,
            parameters,
            input_filename=os.path.join(
                parameters.experiment_output_dir,
                "stage_1",
                parameters.vintage,
                parameters.borough + "_" + parameters.vintage,
                parameters.borough
                + "_"
                + parameters.pattern
                + "_"
                + parameters.vintage
                + ".gml",
            ),
            output_dir=os.path.join(
                parameters.experiment_output_dir,
                "stage_2",
                parameters.vintage,
                parameters.borough + "_" + parameters.vintage,
            ),
            output_filename=parameters.borough
            + "_"
            + parameters.pattern
            + "_"
            + parameters.vintage
            + "_split.gml",
        )
        consume_t = Task(
            "c", consume, inputs=[split_buildings_t.get_parameter("msg")]
        )
        split_buildings_t >> consume_t
    w.create()
