import sys, os

sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition")
)

from hera_utils import hera_assert_version

hera_assert_version("5.6.0")

########
from hera.workflows import (
    ExistingVolume,
    Parameter,
    script,
)


@script(
    inputs=[
        Parameter(name="claim_name"),
        Parameter(name="mount_path"),
        Parameter(name="experiment_output_dir"),
    ],
    volumes=[
        ExistingVolume(
            name="dummy",
            claim_name="{{inputs.parameters.claim_name}}",
            mount_path="{{inputs.parameters.mount_path}}",
        )
    ],
)
def list_experiment_pesisted_files(
    claim_name, mount_path, experiment_output_dir
):
    import os

    print()
    print("Persisted volume files: ", os.listdir(mount_path))
    experiment_dir = os.path.join(mount_path, experiment_output_dir)
    print("Experiment directory list: ", os.listdir(experiment_dir))
    print("Done.")


if __name__ == "__main__":
    from pagoda_environment_utils import print_pagoda_environment
    from pagoda_environment_utils import list_pesistent_volume_files
    from pagoda_environment_definition import environment
    from input_2012_tiny_import_dump import parameters
    from hera.workflows import (
        ConfigMapEnvFrom,
        Container,
        DAG,
        Parameter,
        Task,
        Workflow,
    )

    with Workflow(
        generate_name="testing-numerical-experiment-setup-", entrypoint="main"
    ) as w:
        cowsayprint = Container(
            name="cowsayprint",
            image="docker/whalesay",
            env=[
                ConfigMapEnvFrom(
                    config_map_name=environment.cluster.configmap,
                    optional=False,
                )
            ],
            command=["cowsay", "PaGoda can pull whalesay docker container."],
        )
        with DAG(name="main"):
            t1 = print_pagoda_environment(
                arguments=Parameter(
                    name="config_map_name",
                    value=environment.cluster.configmap,
                ),
            )
            t2 = Task(name="cowsayprint", template=cowsayprint)
            t3 = list_pesistent_volume_files(
                arguments=[
                    Parameter(
                        name="claim_name",
                        value=environment.persisted_volume.claim_name,
                    ),
                    Parameter(
                        name="mount_path",
                        value=environment.persisted_volume.mount_path,
                    ),
                ],
            )
            t4 = list_experiment_pesisted_files(
                arguments=[
                    Parameter(
                        name="claim_name",
                        value=environment.persisted_volume.claim_name,
                    ),
                    Parameter(
                        name="mount_path",
                        value=environment.persisted_volume.mount_path,
                    ),
                    Parameter(
                        name="experiment_output_dir",
                        value=parameters.experiment_output_dir,
                    ),
                ],
            )
            t1 >> t2 >> t3 >> t4
    w.create()
