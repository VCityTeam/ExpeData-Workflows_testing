from hera_utils import hera_assert_version, hera_clear_workflow_template

hera_assert_version("5.6.0")

###########
import os
from utils import get_new_container_identifier
from hera.workflows import (
    Container,
    Env,
    ExistingVolume,
    models,
    Parameter,
    script,
)

# CLEAN ME from hera.expr import g as expr


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
    # and error process and are probably environment dependent.
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


def threedcitydb_start_db_container(environment, database):
    # LIMITS: the 3dcitydb-pg container doesn't seem to use a CMD entry in
    # its Dockefile definition (refer to
    # https://github.com/3dcitydb/3dcitydb/blob/master/postgresql/Dockerfile)
    # but instead uses the Un*x deamon/init.d starting script mechanism.
    # This prevents passing arguments to the container at runtime (e.g. by
    # providing arguments, with `docker run 3dcitydb-pg arg1 arg2`, or
    # environment parameters, with `docker run -e ENV_VAR=my_value 3dcitydb-pg`).
    # In turn this constrains to build as many containers as they are
    # parameters (or combination of parameters) at the Hera level. For example
    # the database name derives from the vintage parameter for which we need
    # to loop for. We thus have no choice but to define as many containers
    # (and associated container names) as they are vintage values.
    # In conclusion: some container run time limitations deport to constrains,
    # at the Hera level, like container multiplication...

    # The simplest possible usage of the 3dcitydb container per se
    new_container = Container(
        name="threedcitydb-start-db-" + get_new_container_identifier(),
        # Run 3dcitydb container as a daemon (i.e. in background)
        daemon=True,
        # Number of container retrial when failing
        # retry_strategy=RetryStrategy(limit=2),
        image=environment.cluster.docker_registry + "vcity/3dcitydb-pg:13-3.1-4.1.0",
        image_pull_policy=models.ImagePullPolicy.always,
        inputs=[Parameter(name="vintage")],
        env=[
            # Specific to 3dCityDB container, refer to
            # https://3dcitydb-docs.readthedocs.io/en/latest/3dcitydb/docker.html#citydb-docker-config-psql
            Env(name="SRID", value=3946),
            Env(name="SRSNAME", value="espg:3946"),
            # Adressed to postgres (that underpins 3DCityDB) at container level
            # as opposed to libpq environment variables refer to
            # https://www.postgresql.org/docs/current/libpq-envars.html
            Env(
                name="POSTGRES_DB",
                value=database.name + "{{inputs.parameters.vintage}}",
            ),
            Env(name="POSTGRES_PASSWORD", value=database.password),
            Env(name="POSTGRES_USER", value=database.user),
        ],
    )

    if database.keep_database:
        # As offered by 3dCityDB container, just provide a PGDATA environment
        # value that points to the ad-hoc directory
        new_container.env.append(
            Env(
                name="PGDATA",
                value=os.path.join(
                    environment.persisted_volume.mount_path,
                    database.serialization_output_dir + "{{inputs.parameters.vintage}}",
                ),
            ),
        )
        new_container.volumes = [
            ExistingVolume(
                claim_name=environment.persisted_volume.claim_name,
                # Providing a name is mandatory but how is it relevant/used ?
                name="dummy-name",
                mount_path=environment.persisted_volume.mount_path,
            )
        ]

    if use_readiness_probe := True:
        readiness_probe = models.Probe(
            exec=models.ExecAction(
                command=[
                    "/bin/sh",
                    "-c",
                    "exec pg_isready -U postgres -h 127.0.0.1 -p 5432",
                ]
            )
        )
        new_container.readiness_probe = readiness_probe

    if use_startup_probe := True:
        # The inital delay of availability depends on the mode db serialization
        # storage and associated

        initialDelaySeconds = get_statistical_value_of_initial_delay(
            database.keep_database
        )

        # CAVEAT EMPTOR:
        # With Hera v5.1.3 you must use `startup_probe` as opposed to the
        # aliased (refer to v1.py) `startupProbe` that does not seem to work:
        # running the workflow will NOT display any error message, but the
        # `startupProbe` entry is simply droppped (won't appear in the manifest).
        # Ditto with `readiness_probe` vs `readinessProbe`.
        # Note: documentation reference
        # https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/#define-startup-probes
        startup_probe = models.Probe(
            exec=models.ExecAction(
                command=[
                    "/usr/lib/postgresql/13/bin/psql",
                    # Note: oddly engough psql does not seem to require a valid
                    # password. Hence we just skip it.
                    #
                    # Note: "-d citydb-lyon-2012" FAILS with message
                    #    'FATAL:  database " citydb-lyon-2012" does not exist'
                    # (notice the leading whitespace in the string). It looks
                    # like HERA/AW throws an extra withespace at run time !?
                    "--dbname=" + database.name + "{{inputs.parameters.vintage}}",
                    # Note: "-U user" FAILS with
                    #     'FATAL:  role " postgres" does not exist'
                    # with a similar symptom as for the "-d " flag (refer above)
                    "--username=" + database.user,
                    "-c",
                    # Note: '"SELECT * FROM citydb.building"' (that is with
                    # enquoted double-quotes) yields
                    #    ERROR:  syntax error at or near ""SELECT * FROM citydb.building"" at character 1
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
        )
        new_container.startup_probe = startup_probe

    return new_container


def send_command_to_postgres_container(
    environment, database, container_name, command, arguments
):
    container = Container(
        name=container_name + "-" + get_new_container_identifier(),
        image=environment.cluster.docker_registry + "vcity/postgres:15.2",
        image_pull_policy=models.ImagePullPolicy.if_not_present,
        inputs=[
            Parameter(name="hostaddr"),
            Parameter(name="vintage"),
        ],
        # Avoid conflicting demands with other pods.
        # synchronization=models.Mutex(name=mutex_lock_on_database_dump_import),
        env=[
            # The following command variables are libpq environment variables
            # refer to https://www.postgresql.org/docs/current/libpq-envars.html
            # (as opposed to docker container variables)
            Env(
                name="PGDATABASE",
                value=database.name + "{{inputs.parameters.vintage}}",
            ),
            # Note: the difference of syntax between the respective definitions
            # of the values of the PGHOSTADDR and PGPASSWORD environment
            # variables is due to the difference of their respective stages of
            # evaluation:
            # - the value of PGHOSTADDR is evaluated at workflow run-time
            #   (on the argo server) and it thus follows the yaml syntax of an
            #   Argo Workflow,
            # - the value of PGPASSWORD is evaluated at (hera based) workflow
            #   submission that is when hera constructs the yaml translation
            #   and sends it to the argo server (for later evaluation).
            Env(name="PGHOSTADDR", value="{{inputs.parameters.hostaddr}}"),
            Env(name="PGPASSWORD", value=database.password),
            Env(name="PGUSER", value=database.user),
            # Note: we default PGPORT because each database runs on a separate
            # host. Port distinction was originaly required because all
            # databases were running on the same desktop.
        ],
        command=command,
        args=arguments,
    )
    return container


def db_isready_container(environment, database):
    # On success this only validates the host address and the port since
    # as reminded by
    # https://stackoverflow.com/questions/26911508/postgres-testing-database-connection-in-bash
    #    It is not necessary to supply correct user name, password, or database
    #    name values to obtain the server status; however, if incorrect values
    #    are provided, the server will log a failed connection attempt.
    command = ["/bin/bash", "-c"]
    arguments = ["pg_isready"]
    return send_command_to_postgres_container(
        environment, database, "db-isready-container", command, arguments
    )


def db_probe_catalog_container(environment, database):
    command = ["psql"]
    # Note: oddly enough (?) when taking the following arguments value
    #     arguments = ["psql", "-c", "SELECT * FROM pg_catalog.pg_tables"]
    # the the commands fail with the following error message
    #     "10.42.2.130:5432 - no response"
    #     ...
    #     Error: exit status 2
    arguments = [
        "-c",
        "SELECT * FROM citydb.building",
    ]
    return send_command_to_postgres_container(
        environment, database, "probe-catalog-container", command, arguments
    )


def import_citygml_file_to_db_container(environment, database):
    container = Container(
        name="threedcitydb-importer" + database.name,
        image=environment.cluster.docker_registry + "vcity/impexp:4.3.0",
        image_pull_policy=models.ImagePullPolicy.always,
        inputs=[
            Parameter(name="database_ip_address"),
            Parameter(name="filenames"),
        ],
        volumes=[
            ExistingVolume(
                # Providing a name is mandatory but how is it relevant/used ?
                name="dummy-name",
                claim_name=environment.persisted_volume.claim_name,
                mount_path=environment.persisted_volume.mount_path,
            )
        ],
        command=["impexp-entrypoint.sh"],
        args=[
            "import",
            "-H",
            "{{inputs.parameters.database_ip_address}}",
            "-d",
            database.name,
            "-u",
            database.user,
            "-p",
            database.password,
            # "-P", database.port,
            "{{inputs.parameters.filenames}}",
        ],
    )
    return container


@script()
def check_is_valid_ip(ip_addr: str):
    """
    Check whether the input string is a valid ip number i.e. that the
    string is of the form X.Y.Z.T where X, Y, Z, T are intergers ranging in
    [1:256]
    """
    import socket

    try:
        print("Checking ", ip_addr, " as presumed IP number.")
        socket.inet_aton(ip_addr)
        print(ip_addr, " is a well formed string to stand as IP number.")
    except socket.error:
        print(ip_addr, " was NOT well formed string to stand as IP number.")
        raise Exception("failure")
