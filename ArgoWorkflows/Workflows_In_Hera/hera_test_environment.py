# Test, at HERA level, whether the enverinoment is properly defined.
# See also CityGMLto3DTiles_Example/test_experiment_setup.py that in addition
# to checking the environment, also checks the experiment inputs.
from hera.workflows import (
    ConfigMapEnvFrom,
    ExistingVolume,
    Parameter,
    script,
)


@script(
    env=[
        # Assumes the corresponding config map is defined at k8s level
        ConfigMapEnvFrom(
            config_map_name="{{inputs.parameters.config_map_name}}",
            optional=False,
        )
    ]
)
def print_environment(
    # Implicit arguments refered above by the @script() decorator (and oddly
    # enough required by Hera altough not used by the function)
    config_map_name,
):
    import os
    import json

    print("Hera on PaGoDa can run python scripts...")
    print(
        "...and retrieve environment variables: ",
        json.dumps(dict(os.environ), indent=4),
    )
    print("Done.")


@script(
    inputs=[
        Parameter(name="claim_name"),
        Parameter(name="mount_path"),
    ],
    volumes=[
        ExistingVolume(
            name="dummy",
            claim_name="{{inputs.parameters.claim_name}}",
            mount_path="{{inputs.parameters.mount_path}}",
        )
    ],
)
def list_pesistent_volume_files(
    # claim_name argument is only used by the @script decorator and is present
    # here only because Hera seems to require it
    claim_name,
    mount_path,
):
    import os

    print(
        "Numerical experiment environment: persistent volume claim_name is ",
        claim_name,
    )
    print(
        "Numerical experiment environment: persistent volume mount path ",
        mount_path,
    )
    print(
        "Numerical experiment persistent volume directory list: ",
        os.listdir(mount_path),
    )
    print("Done.")


if __name__ == "__main__":
    # A workflow that tests whether the defined environment is correct as
    # seen and used from within the Argo server engine (at Workflow runtime)
    from hera_utils import parse_arguments
    from environment import construct_environment
    from hera.workflows import (
        Container,
        DAG,
        Task,
        Workflow,
    )

    args = parse_arguments()
    environment = construct_environment(args)

    with Workflow(generate_name="hera-test-environment-", entrypoint="main") as w:
        cowsayprint = Container(
            name="cowsayprint",
            image="docker/whalesay",
            env=[
                ConfigMapEnvFrom(
                    config_map_name=environment.cluster.configmap,
                    optional=False,
                )
            ],
            command=["cowsay", "Argo can pull whalesay docker container."],
        )
        with DAG(name="main"):
            t1 = print_environment(
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
            t1 >> t2 >> t3
    w.create()
