import sys, os

sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition")
)
from pagoda_environment_definition import environment

####
from hera_utils import hera_assert_version

hera_assert_version("5.6.0")

#########################################################################
from hera.workflows import (
    ConfigMapEnvFrom,
    Container,
    DAG,
    Env,
    models,
    Parameter,
    RetryStrategy,
    Task,
    Workflow,
)

with Workflow(generate_name="retrieve-pod-ip-", entrypoint="d") as w:
    daemon_template = Container(
        name="mydaemon",
        # start 3dcitydb as a daemon
        daemon=True,
        # Number of container retrial when failing
        retry_strategy=RetryStrategy(limit=2),
        image=environment.cluster.docker_registry + "vcity/3dcitydb-postgis:v4.0.2",
        image_pull_policy=models.ImagePullPolicy.always,
        env=[
            # Assumes the corresponding config map is defined in the k8s cluster
            ConfigMapEnvFrom(
                config_map_name=environment.cluster.configmap, optional=False
            ),
            Env(name="POSTGRES_PASSWORD", value="dummy"),
        ],
        command=["docker-entrypoint.sh"],
        args=["postgres", "-p", "5432"],
        readinessProbe=models.Probe(
            exec=models.ExecAction(
                command=[
                    "/bin/sh",
                    "-c",
                    "exec pg_isready -U postgres -h 127.0.0.1 -p 5432",
                ]
            )
        ),
    )
    in_ = Container(
        name="in",
        image="docker/whalesay:latest",
        command=["cowsay"],
        args=["{{inputs.parameters.a}}"],
        inputs=Parameter(name="a"),
    )
    with DAG(name="d"):
        t1 = Task(name="a", template=daemon_template)
        t2 = Task(name="b", template=in_, arguments={"a": t1.ip})
        t1 >> t2


w.create()
