import os
from hera import (
    ConfigMapEnvFrom,
    Env,
    ExistingVolume,
    ImagePullPolicy,
    RetryStrategy,
    Task,
    Workflow,
)


def threedcitydb_start_db(cluster, parameters):
    results_dir = os.path.join(
        parameters.persistedVolume,
        parameters.experiment_output_dir,
        parameters.database.name,
    )
    task = Task(
        "threedcitydb-start-db",
        # start 3dcitydb as a daemon
        daemon=True,
        # Number of container retrial when failing
        retry_strategy=RetryStrategy(limit=2),
        image=cluster.docker_registry + "vcity/3dcitydb-postgis:v4.0.2",
        image_pull_policy=ImagePullPolicy.Always,
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
                name=cluster.volume_claim,
                mount_path=parameters.persistedVolume,
            )
        ],
        ### Not transposed to Hera
        # readinessProbe:                   # wait for readinessProbe to succeed
        # References:
        # - https://argoproj.github.io/argo-workflows/fields/#probe
        # - https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#container-probes
        # - https://github.com/bitnami/charts/issues/2682 (for inspiration)
        # exec:
        #   command:
        #   - /bin/sh
        #   - -c
        #   - exec pg_isready -U "postgres" -h 127.0.0.1 -p "{{inputs.parameters.port}}"
    )
    return task


if __name__ == "__main__":
    import sys, os

    sys.path.append(
        os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition")
    )
    from pagoda_cluster_definition import define_cluster
    from input_2012_tiny_import_dump import parameters
    from database import readinessProbe_task

    cluster = define_cluster()
    with Workflow("threedcitydb-start-", generate_name=True) as w:
        threedcitydb_start_t = threedcitydb_start_db(cluster, parameters)
        ## Will fail on submission with
        #     argo_workflows.exceptions.ServiceException: (500)
        #     Reason: Internal Server Error
        #     failed to resolve {{tasks.threedcitydb-start-db.ip}}
        # Note: using <<task>>.ip notation is inspired by
        #  hera(4.4.2)/examples/daemon.py 
        readinessProbe_t = readinessProbe_task(
          cluster, 
          parameters, 
          threedcitydb_start_t.ip, 
          5
        )
        # threedcitydb_start_t >> readinessProbe_t
    w.create()
