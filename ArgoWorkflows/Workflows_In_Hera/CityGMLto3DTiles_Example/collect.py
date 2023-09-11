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


def collect_container_constructor(environment, parameters, results_dir: str):
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
            parameters.borough,
            "--pattern",
            parameters.pattern,
            "--results_dir",
            results_dir,
            "--vintage",
            parameters.vintage,
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


if __name__ == "__main__":
    from pagoda_environment_definition import environment
    from input_2012_tiny_import_dump import parameters
    from experiment_layout import layout

    from utils import print_script, ip_http_check_container
    from hera.workflows import DAG, Task, Workflow

    with Workflow(generate_name="fullcollect-", entrypoint="dag") as w:
        ip_http_check_c = ip_http_check_container(environment)
        collect_c = collect_container_constructor(
            environment,
            parameters,
            results_dir=layout.collect_output_dir(
                parameters, output_dir="stage_1"
            ),
        )
        with DAG(name="dag"):
            check_ip_connectivity_t = Task(
                name="iphttpcheck", template=ip_http_check_c
            )
            collect_t = Task(name="collect", template=collect_c)
            print_t = print_script(
                name="print-results",
                arguments=collect_t.get_parameter("msg").with_name("message"),
            )
            check_ip_connectivity_t >> collect_t >> print_t
    w.create()
