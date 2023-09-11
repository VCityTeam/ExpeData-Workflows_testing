import os, sys

sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition")
)
from hera_utils import hera_assert_version

hera_assert_version("5.6.0")

###
from hera.workflows import Container, ExistingVolume, models


def split_buildings_container(
    environment,
    input_filename: str,  # Absolute file path
    output_dir: str,  # Absolute directory path
    output_filename: str,  # Filename (relative to output_dir)
):
    return Container(
        name="split-buildings",
        image=environment.cluster.docker_registry + "vcity/3duse:0.1",
        image_pull_policy=models.ImagePullPolicy.if_not_present,
        working_dir="/root/3DUSE/Build/src/utils/cmdline/",
        command=[
            "splitCityGMLBuildings",
            "--input-file",
            input_filename,
            "--output-file",
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

    with Workflow(generate_name="split-buildings-", entrypoint="dag") as w:
        split_buildings_c = split_buildings_container(
            environment,
            input_filename=os.path.join(
                environment.persisted_volume.mount_path,
                layout.split_buildings_input_filename(parameters),
            ),
            output_dir=os.path.join(
                environment.persisted_volume.mount_path,
                layout.split_buildings_output_dir(parameters),
            ),
            output_filename=layout.split_buildings_output_filename(parameters),
        )
        with DAG(name="dag"):
            split_buildings_t = Task(
                name="split-buildings", template=split_buildings_c
            )
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
                environment.persisted_volume.mount_path,
                layout.split_buildings_output_dir(parameters),
            )
            write_output_t: Task = convert_message_to_output_parameter(
                arguments=Parameter(name="message", value=output_dir)
            )
            print_t = print_script(
                name="print-results",
                arguments=write_output_t.get_parameter("message"),
            )
            split_buildings_t >> write_output_t >> print_t
    w.create()
