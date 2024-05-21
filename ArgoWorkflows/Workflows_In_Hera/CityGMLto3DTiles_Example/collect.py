from hera.workflows import (
    ConfigMapEnvFrom,
    Container,
    ExistingVolume,
    models,
    Parameter,
)


def collect_container_constructor(environment, constants):
    return Container(
        inputs=[
            Parameter(name="vintage"),
            Parameter(name="borough"),
            Parameter(name="results_dir"),
        ],
        name="collect",
        image=environment.cluster.docker_registry + "vcity/collect_lyon_data:0.1",
        image_pull_policy=models.ImagePullPolicy.always,
        env_from=[
            # Assumes the corresponding config map is defined in the k8s cluster
            ConfigMapEnvFrom(name=environment.cluster.configmap, optional=False),
        ],
        command=[
            "python3",
            "entrypoint.py",
            "--borough",
            "{{inputs.parameters.borough}}",
            "--pattern",
            constants.pattern,
            "--results_dir",
            "{{inputs.parameters.results_dir}}",
            "--vintage",
            "{{inputs.parameters.vintage}}",
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
                name="msg",
                value_from=models.ValueFrom(
                    path="{{inputs.parameters.results_dir}}/Resulting_Filenames.txt"
                ),
            )
        ],
    )
