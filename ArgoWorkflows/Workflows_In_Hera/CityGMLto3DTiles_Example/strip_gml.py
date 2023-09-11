import os, sys

sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition")
)
from hera_utils import hera_assert_version

hera_assert_version("5.6.0")

###
import os
from hera.workflows import Container, ExistingVolume, models


def strip_gml_container(
    environment,
    input_filename: str,  # Absolute file path
    output_dir: str,  # Absolute directory path
    output_filename: str,  # Filename (relative to output_dir)
):
    return Container(
        name="strip-gml",
        image=environment.cluster.docker_registry
        + "vcity/citygml2stripper:0.1",
        image_pull_policy=models.ImagePullPolicy.if_not_present,
        # working_dir: is not necessary in this case
        command=[
            "python3",
            "/src/CityGML2Stripper.py",
            "--input",
            input_filename,
            "--output",
            output_filename,
            "--output-dir",
            output_dir,
        ],
        volumes=[
            ExistingVolume(
                name="dummy-name-but-required",
                claim_name=environment.persisted_volume.claim_name,
                mount_path=environment.persisted_volume.mount_path,
            )
        ],
    )


if __name__ == "__main__":
    from pagoda_environment_definition import environment
    from input_2012_tiny_import_dump import parameters
    from experiment_layout import layout

    from utils import print_script, convert_message_to_output_parameter
    from hera.workflows import DAG, Task, Parameter, Workflow

    with Workflow(generate_name="strip-gml-", entrypoint="dag") as w:
        strip_gml_c = strip_gml_container(
            environment,
            input_filename=os.path.join(
                environment.persisted_volume.mount_path,
                layout.split_buildings_output_dir(parameters),
                layout.split_buildings_output_filename(parameters),
            ),
            output_dir=os.path.join(
                environment.persisted_volume.mount_path,
                layout.strip_gml_output_dir(parameters),
            ),
            output_filename=layout.strip_gml_output_filename(parameters),
        )
        with DAG(name="dag"):
            strip_gml_t = Task(name="strip-gml", template=strip_gml_c)
            # The original `strip-gml` container does not define an output
            # file that holds the name of the resulting file. This makes it hard
            # to transmit that information (the name of the resulting file) to
            # the next task in the workflow that requires that filename as one
            # of its inputs.
            # In order to circumvent that shortcoming of the `strip-gml`
            # container, we add a post-treament (to `strip-g,;`) whose
            # single purpose is to write that result file (holding filename(s)).
            # This inital limited task is thus complemented with an adhoc
            # post-treament task.
            output_dir = os.path.join(
                environment.persisted_volume.mount_path,
                layout.strip_gml_output_dir(parameters),
            )
            write_output_t: Task = convert_message_to_output_parameter(
                arguments=Parameter(name="message", value=output_dir)
            )
            print_t = print_script(
                name="print-results",
                arguments=write_output_t.get_parameter("message"),
            )
            strip_gml_t >> write_output_t >> print_t
    w.create()
