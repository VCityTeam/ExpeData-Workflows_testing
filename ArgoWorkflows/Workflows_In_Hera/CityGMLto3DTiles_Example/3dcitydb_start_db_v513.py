import sys, os

sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition")
)
from hera_utils import hera_check_version

hera_check_version("5.1.3")

from hera.workflows import (
    ConfigMapEnvFrom,
    Container,
    Env,
    ExistingVolume,
    models,
    RetryStrategy,
)

from pagoda_cluster_definition import define_cluster
from input_2012_tiny_import_dump import parameters

cluster = define_cluster()


def threedcitydb_start_db_constructor(cluster, parameters):
    results_dir = os.path.join(
        parameters.persistedVolume,
        parameters.experiment_output_dir,
        parameters.database.name,
    )
    bozo = Container(
        name="threedcitydb-start-db",
        # start 3dcitydb as a daemon
        daemon=True,
        # Number of container retrial when failing
        retry_strategy=RetryStrategy(limit=2),
        image=cluster.docker_registry + "vcity/3dcitydb-postgis:v4.0.2",
        image_pull_policy=models.ImagePullPolicy.always,
        env=[
            # Assumes the corresponding config map is defined in the k8s cluster
            ConfigMapEnvFrom(
                config_map_name=cluster.configmap, optional=False
            ),
            # Specific to container
            Env(name="CITYDBNAME", value=parameters.database.name),
            Env(name="POSTGRES_PASSWORD", value=parameters.database.password),
            Env(name="POSTGRES_USER", value=parameters.database.user),
            Env(name="SRID", value="3946"),
            Env(name="SRSNAME", value="espg:3946"),
            Env(name="PGDATA", value=results_dir),
        ],
        command=["docker-entrypoint.sh"],
        args=["postgres", "-p", parameters.database.port],
        volumes=[
            ExistingVolume(
                claim_name=cluster.volume_claim,
                name="dummy-name",
                # V4.4.3 name=cluster.volume_claim,
                mount_path=parameters.persistedVolume,
            )
        ],
        readinessProbe=models.Probe(
            exec=models.ExecAction(
                command=[
                    "/bin/sh",
                    "-c",
                    "exec pg_isready -U "
                    + parameters.database.user
                    + " -h 127.0.0.1 -p "
                    + parameters.database.port,
                ]
            )
        ),
    )
    return bozo


if __name__ == "__main__":
    import sys, os

    sys.path.append(
        os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition")
    )
    from pagoda_cluster_definition import define_cluster
    from input_2012_tiny_import_dump import parameters

    # from database_v513 import readiness_probe_task
    from hera.workflows import DAG, Parameter, Task, Workflow

    cluster = define_cluster()
    with Workflow(generate_name="threedcitydb-start-", entrypoint="d") as w:
        whalesay_c = Container(
            name="in",
            image="docker/whalesay:latest",
            command=["cowsay"],
            args=["{{inputs.parameters.a}}"],
            inputs=Parameter(name="a"),
        )
        threedcitydb_start_db_c = threedcitydb_start_db_constructor(
            cluster, parameters
        )
        with DAG(name="d"):
            threedcitydb_start_t = Task(
                name="a", template=threedcitydb_start_db_c
            )
            t2 = Task(
                name="b",
                template=whalesay_c,
                arguments={"a": threedcitydb_start_t.ip},
            )
            threedcitydb_start_t >> t2
    w.create()
