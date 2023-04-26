import os
from hera.workflows import (
    ConfigMapEnvFrom,
    Container,
    DAG,
    ExistingVolume,
    models,
    Parameter,
    Task,
    Workflow,
)


def collect_container_constructor(cluster, parameters, results_dir: str):
    output_value_path = os.path.join(
        parameters.persistedVolume,
        results_dir,
        "Resulting_Filenames.txt",
    )
    return Container(
        name="collect",
        image=cluster.docker_registry + "vcity/collect_lyon_data:0.1",
        image_pull_policy=models.ImagePullPolicy.always,
        env_from=[
            # Assumes the corresponding config map is defined in the k8s cluster
            ConfigMapEnvFrom(name=cluster.configmap, optional=False),
        ],
        command=[
            "python3",
            # inputs=[
            "entrypoint.py",
            "--borough",
            parameters.borough,
            "--pattern",
            parameters.pattern,
            "--results_dir",
            results_dir,
            "--vintage",
            parameters.vintage,
            "--volume",
            parameters.persistedVolume,
        ],
        volumes=[
            ExistingVolume(
                claim_name=cluster.volume_claim,
                name=cluster.volume_claim,
                mount_path=parameters.persistedVolume,
            )
        ],
        outputs=[
            Parameter(
                name="msg", value_from=models.ValueFrom(path=output_value_path)
            )
        ],
    )


if __name__ == "__main__":
    import sys, os

    sys.path.append(
        os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition")
    )
    from pagoda_cluster_definition import define_cluster
    from input_2012_tiny_import_dump import parameters
    from experiment_layout import layout
    from utils import whalesay_container_constructor

    cluster = define_cluster()
    with Workflow(generate_name="fullcollect-", entrypoint="dag") as w:
        whalesay_c = whalesay_container_constructor()
        collect_c = collect_container_constructor(
            cluster,
            parameters,
            results_dir=layout.collect_output_dir(
                parameters, output_dir="stage_1"
            ),
        )
        with DAG(name="dag"):
            collect_t = Task(name="collect", template=collect_c)
            whalesay_t = Task(
                name="whalesay",
                template=whalesay_c,
                # The following commented version fail: the whale says
                # something but not what is expected
                # arguments={"a": collect_t.get_parameter("msg")},
                # arguments=[Parameter(name="a", value=collect_t.get_parameter("msg"))],
                arguments=collect_t.get_parameter("msg").with_name("a"),
            )
            collect_t >> whalesay_t
    w.create()
