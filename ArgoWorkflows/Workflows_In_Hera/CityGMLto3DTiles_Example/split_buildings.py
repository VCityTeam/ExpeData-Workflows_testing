import os, sys

sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition")
)
from hera_utils import hera_assert_version

hera_assert_version("5.6.0")

###
from hera.workflows import Container, ExistingVolume, models, Parameter


def split_buildings_container(environment):
    return Container(
        inputs=[
            # Absolute file path
            Parameter(name="input_filename"),
            # Absolute directory path
            Parameter(name="output_dir"),
            # Filename (relative to output_dir)
            Parameter(name="output_filename"),
        ],
        name="split-buildings",
        image=environment.cluster.docker_registry + "vcity/3duse:0.1",
        image_pull_policy=models.ImagePullPolicy.if_not_present,
        working_dir="/root/3DUSE/Build/src/utils/cmdline/",
        command=[
            "splitCityGMLBuildings",
            "--input-file",
            "{{inputs.parameters.input_filename}}",
            "--output-file",
            "{{inputs.parameters.output_filename}}",
            "--output-dir",
            "{{inputs.parameters.output_dir}}",
        ],
        volumes=[
            ExistingVolume(
                name="dummy-name-but-required",
                claim_name=environment.persisted_volume.claim_name,
                mount_path=environment.persisted_volume.mount_path,
            )
        ],
    )
