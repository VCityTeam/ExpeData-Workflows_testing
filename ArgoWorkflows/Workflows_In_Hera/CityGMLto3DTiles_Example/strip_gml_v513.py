import os
from hera.workflows import Container, ExistingVolume, models


def strip_gml_container(
    cluster,
    workflow_parameters,
    input_filename: str,  # Absolute file path
    output_dir: str,  # Absolute directory path
    output_filename: str,  # Filename (relative to output_dir)
):
    output_dir = os.path.join(workflow_parameters.persistedVolume, output_dir)
    return Container(
        name="strip-gml",
        image=cluster.docker_registry + "vcity/citygml2stripper:0.1",
        image_pull_policy=models.ImagePullPolicy.if_not_present,
        # working_dir: is not necessary in this case
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
                name="dummy-name-but-required",
                claim_name=cluster.volume_claim,
                mount_path=parameters.persistedVolume,
            )
        ],
    )


if __name__ == "__main__":
    import sys, os

    sys.path.append(
        os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition")
    )
    from pagoda_cluster_definition import define_cluster
    from utils import whalesay_container_constructor, write_output
    from hera_utils import hera_assert_version

    hera_assert_version("5.1.3")

    from input_2012_tiny_import_dump import parameters
    from experiment_layout import layout
    from hera.workflows import DAG, Task, Parameter, Workflow

    cluster = define_cluster()
    with Workflow(generate_name="strip-gml-", entrypoint="dag") as w:
        strip_gml_c = strip_gml_container(
            cluster,
            parameters,
            input_filename=os.path.join(
                layout.split_buildings_output_dir(parameters),
                layout.split_buildings_output_filename(parameters),
            ),
            output_dir=layout.strip_gml_output_dir(parameters),
            output_filename=layout.strip_gml_output_filename(parameters),
        )
        whalesay_c = whalesay_container_constructor()
        with DAG(name="dag"):
            strip_gml_t = Task(name="split-buildings", template=strip_gml_c)
            # The original `split-buildings` container does not define an output
            # file that holds the name of the resulting file. This makes it hard
            # to transmit that information (the name of the resulting file) to the next
            # taks in the workflow that requires that filename as one of its inputs.
            # In order to circumvent that shortcoming of the `split-buildings` container
            # we add a posttreament that whose single purpose is to write that result
            # file (holding filename(s).
            # This inital limited task is thus complemented with an adhoc post-treament
            # task.
            output_dir = os.path.join(
                parameters.persistedVolume,
                layout.split_buildings_output_dir(parameters),
            )
            write_output_t: Task = write_output(
                arguments=Parameter(name="message", value=output_dir)
            )
            whalesay_t = Task(
                name="whalesay",
                template=whalesay_c,
                arguments=write_output_t.get_parameter("a").with_name("a"),
            )
            strip_gml_t >> write_output_t >> whalesay_t
    w.create()
