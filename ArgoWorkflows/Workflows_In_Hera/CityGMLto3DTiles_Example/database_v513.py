import os
from hera.workflows import (
    ConfigMapEnvFrom,
    Container,
    Env,
    ExistingVolume,
    models,
    Parameter,
    RetryStrategy,
)


def threedcitydb_start_db_container_constructor(cluster, parameters):
    results_dir = os.path.join(
        parameters.persistedVolume,
        parameters.experiment_output_dir,
        parameters.database.name,
    )
    new_container = Container(
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
            # Specific to 3dCityDB container
            Env(name="CITYDBNAME", value=parameters.database.name),
            Env(name="SRID", value="3946"),
            Env(name="SRSNAME", value="espg:3946"),
            # Adressed to postgres (that underpins 3DCityDB) at container level
            # as opposed to libpq environment variables refer to
            # https://www.postgresql.org/docs/current/libpq-envars.html
            Env(name="POSTGRES_PASSWORD", value=parameters.database.password),
            Env(name="POSTGRES_USER", value=parameters.database.user),
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
                    "exec pg_isready -U " + parameters.database.user
                    ### FIXME DO WE NEED THE PORT IN THE FOLLOWING COMMAND ?
                    # + " -h 127.0.0.1 -p "
                    # + parameters.database.port,
                ]
            )
        ),
    )
    return new_container


# FIXME: these are not Tasks anymore. Change the function names
def send_command_to_postgres_container_constructor(
    cluster, parameters, arguments
):
    container = Container(
        name="sendcommandtopostgresdb",
        image=cluster.docker_registry + "vcity/postgres:15.2",
        image_pull_policy=models.ImagePullPolicy.if_not_present,
        inputs=Parameter(name="hostaddr"),
        env=[
            # Assumes the corresponding config map is defined in the k8s cluster
            ConfigMapEnvFrom(
                config_map_name=cluster.configmap, optional=False
            ),
            # The following command variables are libpq environment variables
            # refer to https://www.postgresql.org/docs/current/libpq-envars.html
            # (as opposed to docker container variables)
            Env(name="PGDATABASE", value=parameters.database.name),
            # Note: the difference of syntax between the respective definitions
            # of the values of the PGHOSTADDR and PGPASSWORD environment
            # variables is due to the difference of their respective stages of
            # evalution:
            # - the value of PGHOSTADDR is evaluated at workflow run-time
            #   (on the argo server) and it thus follows the yaml syntax of an
            #   Argo Workflow,
            # - the value of PGHOSTADDR is evaluated at (hera based) workflow
            #   definition that is when hera constructs the yaml translation
            #   and sends it to the argo server (for later evaluation).
            Env(name="PGHOSTADDR", value="{{inputs.parameters.hostaddr}}"),
            Env(name="PGPASSWORD", value=parameters.database.password),
            Env(name="PGUSER", value=parameters.database.user),
        ],
        command=["/bin/bash", "-c"],
        args=arguments,
    )
    return container


def readiness_probe_container_constructor(cluster, parameters):
    ### FIXME DO WE NEED THE PORT IN THE FOLLOWING COMMAND ?
    # + " -p "
    # + parameters.database.port
    arguments = ["exec", "pg_isready"]
    return send_command_to_postgres_container_constructor(
        cluster, parameters, arguments
    )
