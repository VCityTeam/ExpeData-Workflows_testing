import os, sys

sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition")
)
from hera_utils import hera_assert_version

hera_assert_version("5.6.0")

###
import os
from hera.workflows import Container, ExistingVolume, models, Parameter


def strip_gml_container(environment):
    return Container(
        inputs=[
            # Absolute file path
            Parameter(name="input_filename"),
            # Absolute directory path
            Parameter(name="output_dir"),
            # Filename (relative to output_dir)
            Parameter(name="output_filename"),
        ],
        name="strip-gml",
        image=environment.cluster.docker_registry
        + "vcity/citygml2stripper:0.1",
        image_pull_policy=models.ImagePullPolicy.if_not_present,
        # working_dir: is not necessary in this case
        command=[
            "python3",
            "/src/CityGML2Stripper.py",
            "--input",
            "{{inputs.parameters.input_filename}}",
            "--output",
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
