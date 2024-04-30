if __name__ == "__main__":
    from parse_arguments import parse_arguments
    from pagoda_environment_definition import construct_environment
    from pagoda_environment_utils import print_pagoda_environment
    from pagoda_environment_utils import list_pesistent_volume_files
    from hera.workflows import (
        ConfigMapEnvFrom,
        Container,
        DAG,
        Parameter,
        Task,
        Workflow,
    )

    args = parse_arguments()
    environment = construct_environment(args)

    with Workflow(generate_name="test-pagoda-setup-", entrypoint="main") as w:
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
            t1 >> t2 >> t3
    w.create()
