import sys, os

sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition")
)
from hera_utils import hera_assert_version

hera_assert_version("5.6.0")

####

import os
from hera.workflows import (
    ConfigMapEnvFrom,
    Container,
    ExistingVolume,
    models,
    Parameter,
)


def collect_container_constructor(environment, inputs, results_dir: str):
    output_value_path = os.path.join(
        environment.persisted_volume.mount_path,
        results_dir,
        "Resulting_Filenames.txt",
    )
    return Container(
        name="collect",
        image=environment.cluster.docker_registry
        + "vcity/collect_lyon_data:0.1",
        image_pull_policy=models.ImagePullPolicy.always,
        env_from=[
            # Assumes the corresponding config map is defined in the k8s cluster
            ConfigMapEnvFrom(
                name=environment.cluster.configmap, optional=False
            ),
        ],
        command=[
            "python3",
            # inputs=[
            "entrypoint.py",
            "--borough",
            # FAIL: NE MARCHERA PAS sur une boucle
            inputs.parameters.boroughs,
            "--pattern",
            inputs.constants.pattern,
            "--results_dir",
            results_dir,
            "--vintage",
            # FAIL: NE MARCHERA PAS sur une boucle
            inputs.parameters.vintages,
            "--volume",
            environment.persisted_volume.mount_path,
        ],
        volumes=[
            ExistingVolume(
                claim_name=environment.persisted_volume.claim_name,
                name="dummy",
                mount_path=environment.persisted_volume.mount_path,
            )
        ],
        outputs=[
            Parameter(
                name="msg", value_from=models.ValueFrom(path=output_value_path)
            )
        ],
    )
