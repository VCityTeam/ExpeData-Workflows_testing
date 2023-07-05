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


def get_statistical_value_of_initial_delay(db_files_out_of_container: bool):
    """_summary_
    The sole purpose of this function is to gather methodological elements
    that led to the choice of some valueS (depends on the context) of the
    initial delay (initialDelaySeconds) before the database is ready for usage

    Parameters:
      db_files_out_of_container: whether we wish to store the database files
      (that is serialized internal representation as opposed to a dump) outisde
      of the container or not.
    """
    # On any given platform, there is a strong dependency between
    #  - the original state of database (e.g. never created, successfully
    #    already previously (externaly or at prior pipeline execution) or
    #    left inconsistent (after failure of a prior execution)
    #  - whether we can discard the database (it leaves within the
    #    container and gets discarded on exit) or we wish to preserve it
    #    after the workflow execution (the database is written on a
    #    mounted volume)
    # and the delay after which the database will be available (availability
    # is asserted with a properly configured startup probe).
    # On PaGoDA the following table holds the respective values of
    # `initialDelaySeconds` required for 3dcitydb to become properly
    # active (and a workflow using that container to succeed):
    #
    #                        |---------------------------------------|
    #                        | PGDATA value is SET | PGDATA is UNSET |
    #  |---------------------|---------------------|-----------------|
    #  | Database not yet    |        360          |                 |
    #  | created             |                     |                 |
    #  |---------------------|---------------------|                 |
    #  | Database previously |        120          |                 |
    #  | created with success|                     |       60        |
    #  |---------------------|---------------------|                 |
    #  | Database creation   |                     |                 |
    #  | aborted at previous |        ???          |                 |
    #  | run                 |                     |                 |
    #  |---------------------|---------------------|-----------------|
    #
    # The above table values were aquired through an empirical trial
    # and error process and are probably cluster dependent.
    #
    # Technical notes (if further debug is required):
    #    Oddly enough, when the chosen value of `initialDelaySeconds` is
    #    below the (respective) working threshold, AW displays an end date
    #    for the Container (with a duration roughly equivalent to the
    #    value of initialDelaySeconds) and the 3dcitydb initialization
    #    process seems to be halted. In this case the error messages are
    #    of the form:
    #       Setting up 3DCityDB database schema in database <db-name> ...
    #       <some date> UTC [101] FATAL:  role "root" does not exist
    #       <some date> UTC [108] FATAL:  role "root" does not exist
    #       ....
    if db_files_out_of_container:
        # Because we cannot tell whether the database was previously created or
        # not we are constrained to play it safe and take the maximum value of
        # both cases (that is consider the worse case) database already created
        # and database not yet created:
        initialDelaySeconds = 360
    else:
        initialDelaySeconds = 60
    return initialDelaySeconds


def threedcitydb_start_db_container(cluster, parameters):
    # IMPROVE: promote this derived variable to become a paramters attribute ?
    results_dir = os.path.join(
        parameters.persistedVolume,
        parameters.experiment_output_dir,
        parameters.database.name,
    )
    ### Deal with the variability of requirements concerning db serialization
    # storage and associated inital delay of availability
    env = [
        # Assumes the corresponding config map is defined in the k8s cluster
        ConfigMapEnvFrom(config_map_name=cluster.configmap, optional=False),
        # Specific to 3dCityDB container, refer to
        # https://3dcitydb-docs.readthedocs.io/en/latest/3dcitydb/docker.html#citydb-docker-config-psql
        Env(name="SRID", value=3946),
        Env(name="SRSNAME", value="espg:3946"),
        # Adressed to postgres (that underpins 3DCityDB) at container level
        # as opposed to libpq environment variables refer to
        # https://www.postgresql.org/docs/current/libpq-envars.html
        Env(name="POSTGRES_DB", value=parameters.database.name),
        Env(name="POSTGRES_PASSWORD", value=parameters.database.password),
        Env(name="POSTGRES_USER", value=parameters.database.user),
    ]
    if parameters.database.keep_database:
        # As offered by 3dCityDB container, just provide a PGDATA environment
        # value that points to the ad-hoc directory
        env.append(
            Env(name="PGDATA", value=results_dir),
        )

    initialDelaySeconds = get_statistical_value_of_initial_delay(
        parameters.database.keep_database
    )

    ### We can now define the container per se
    new_container = Container(
        name="threedcitydb-start-db",
        daemon=True,  # Run 3dcitydb container as a daemon (i.e. in background)
        # Number of container retrial when failing
        # retry_strategy=RetryStrategy(limit=2),
        image=cluster.docker_registry + "vcity/3dcitydb-pg:13-3.1-4.1.0",
        image_pull_policy=models.ImagePullPolicy.always,
        env=env,
        volumes=[
            ExistingVolume(
                claim_name=cluster.volume_claim,
                # Providing a name is mandatory but how is it relevant/used ?
                name="dummy-name",
                mount_path=parameters.persistedVolume,
            )
        ],
        # CAVEAT EMPTOR:
        # With Hera v5.1.3 you must use `startup_probe` as opposed to the
        # aliased (refer to v1.py) `startupProbe` that does not seem to work:
        # running the workflow will NOT display any error message, but the
        # `readinessProbe` entry is simply droppped (won't appear in the
        # manifest).
        # Ditto with `readiness_probe` vs `readinessProbe`.
        # Note: documentation reference
        # https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/#define-startup-probes
        startup_probe=models.Probe(
            exec=models.ExecAction(
                command=[
                    "/usr/lib/postgresql/13/bin/psql",
                    # "password=postgres",
                    # "export PGPASSWORD=postgres ;",
                    # "-d citydb-lyon-2012" FAILS with message
                    #    'FATAL:  database " citydb-lyon-2012" does not exist'
                    # (notice the leading whitespace in the string). It looks
                    # like HERA/AW throws an extra withespace at run time !?
                    "--dbname=" + parameters.database.name,
                    # "-U user" FAILS with
                    #     'FATAL:  role " postgres" does not exist'
                    # with a similar symptom as for the "-d " flag (refer above)
                    "--username=" + parameters.database.user,
                    "-c",
                    # '"SELECT * FROM citydb.building"' (that is with enquoted
                    # double-quotes) yields
                    #     ERROR:  syntax error at or near ""SELECT * FROM citydb.building"" at character 1
                    "SELECT * FROM citydb.building",
                ]
            ),
            initialDelaySeconds=initialDelaySeconds,
            # In case this doesn't suffice (e.g. on another platform than
            # PaGoDA), we add some further delay by picking some (quite
            # arbitraty at this stage of testing) values for failureThreshold
            # and periodSeconds:
            failureThreshold=10,
            periodSeconds=30,
            # Number of seconds after which the probe times out.
            timeoutSeconds=10,
        ),
    )
    return new_container


def send_command_to_postgres_container(
    cluster, parameters, name, command, arguments
):
    container = Container(
        name=name,
        image=cluster.docker_registry + "vcity/postgres:15.2",
        image_pull_policy=models.ImagePullPolicy.if_not_present,
        inputs=Parameter(name="hostaddr"),
        # Avoid conflicting demands with other pods.
        # synchronization=models.Mutex(name=mutex_lock_on_database_dump_import),
        env=[
            # Assumes the corresponding config map is defined in the k8s cluster
            ConfigMapEnvFrom(
                config_map_name=cluster.configmap, optional=False
            ),
            # The following command variables are libpq environment variables
            # refer to https://www.postgresql.org/docs/current/libpq-envars.html
            # (as opposed to docker container variables)
            Env(name="PGDATABASE", value=parameters.database.name),
            # FIXME: at some point the database name will need to be derived
            # with the vintage name
            # {{inputs.parameters.database_name}}-{{inputs.parameters.vintage}}
            # Note: the difference of syntax between the respective definitions
            # of the values of the PGHOSTADDR and PGPASSWORD environment
            # variables is due to the difference of their respective stages of
            # evaluation:
            # - the value of PGHOSTADDR is evaluated at workflow run-time
            #   (on the argo server) and it thus follows the yaml syntax of an
            #   Argo Workflow,
            # - the value of PGHOSTADDR is evaluated at (hera based) workflow
            #   definition that is when hera constructs the yaml translation
            #   and sends it to the argo server (for later evaluation).
            Env(name="PGHOSTADDR", value="{{inputs.parameters.hostaddr}}"),
            Env(name="PGPASSWORD", value=parameters.database.password),
            Env(name="PGUSER", value=parameters.database.user),
            ### FIXME DO WE NEED THE PORT IN ALL THE FOLLOWING COMMAND ?
            # The variable is parameters.database.port
        ],
        command=command,
        args=arguments,
    )
    return container


def db_isready_container(cluster, parameters, name):
    # On success this only validates the host address and the port since
    # as reminded by
    # https://stackoverflow.com/questions/26911508/postgres-testing-database-connection-in-bash
    #    It is not necessary to supply correct user name, password, or database
    #    name values to obtain the server status; however, if incorrect values
    #    are provided, the server will log a failed connection attempt.
    command = ["/bin/bash", "-c"]
    arguments = ["pg_isready"]
    return send_command_to_postgres_container(
        cluster, parameters, name, command, arguments
    )


def db_probe_catalog_container(cluster, parameters, name):
    command = ["psql"]
    # Note: oddly enough (?) the following arguments definition fails with
    #     "10.42.2.130:5432 - no response"
    #     ...
    #     Error: exit status 2
    # arguments = ["psql", "-c", "SELECT * FROM pg_catalog.pg_tables"]
    arguments = [
        "--dbname=" + parameters.database.name,
        "--username=" + parameters.database.user,
        "-c",
        "SELECT * FROM citydb.building",
    ]
    return send_command_to_postgres_container(
        cluster, parameters, name, command, arguments
    )


def import_citygml_file_to_db_container(cluster, parameters, input_filename):
    container = Container(
        name="threedcitydb-importer",
        image=cluster.docker_registry + "vcity/impexp:4.3.0",
        image_pull_policy=models.ImagePullPolicy.always,
        inputs=Parameter(name="hostaddr"),
        volumes=[
            ExistingVolume(
                claim_name=cluster.volume_claim,
                # Providing a name is mandatory but how is it relevant/used ?
                name="dummy-name",
                mount_path=parameters.persistedVolume,
            )
        ],
        command=["impexp-entrypoint.sh"],
        args=[
            "import",
            "-H",
            "{{inputs.parameters.hostaddr}}",
            "-d",
            parameters.database.name,
            "-u",
            parameters.database.user,
            "-p",
            parameters.database.password,
            os.path.join(parameters.persistedVolume, input_filename)
            # "-P", "{{inputs.parameters.port}}",
        ],
    )
    return container
