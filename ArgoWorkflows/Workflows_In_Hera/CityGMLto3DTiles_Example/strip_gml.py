import os
from write_output import write_output_task

from hera import (
    ConfigMapEnvFrom,
    ExistingVolume,
    ImagePullPolicy,
    Task,
    Workflow,
)


def strip_gml_task(
    cluster,
    workflow_parameters,
    input_filename: str,  # Absolute file path
    output_dir: str,  # Absolute directory path
    output_filename: str,  # Filename (relative to output_dir)
):
    output_dir = os.path.join(workflow_parameters.persistedVolume, output_dir)
    treatment_task = Task(
        "strip-gml",
        image=cluster.docker_registry + "vcity/citygml2stripper:0.1",
        image_pull_policy=ImagePullPolicy.IfNotPresent,
        # working_dir: is not necessary in this case
        env=[
            # Assumes the corresponding config map is defined in the k8s cluster
            ConfigMapEnvFrom(config_map_name=cluster.configmap, optional=False)
        ],
        command=[
            "python3",
            "/src/CityGML2Stripper.py",
            "--input",
            os.path.join(workflow_parameters.persistedVolume, input_filename),
            "--output",
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
    from experiment_layout import layout

    def consume(msg: str):
        print(f"Resulting filenames: {msg}")

    cluster = define_cluster()
    with Workflow("stripgml-", generate_name=True) as w:
        strip_gml_t = strip_gml_task(
            cluster,
            parameters,
            input_filename=os.path.join(
                layout.split_buildings_output_dir(parameters),
                layout.split_buildings_output_filename(parameters)
            ),
            output_dir=layout.strip_gml_output_dir(parameters),
            output_filename=layout.strip_gml_output_filename(parameters),
        )
        consume_t = Task(
            "c", consume, inputs=[strip_gml_t.get_parameter("msg")]
        )
        strip_gml_t >> consume_t
    w.create()
