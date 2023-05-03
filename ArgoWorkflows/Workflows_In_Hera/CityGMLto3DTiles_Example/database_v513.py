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


def threedcitydb_start_db_container(cluster, parameters):
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
        # retry_strategy=RetryStrategy(limit=2),
        image=cluster.docker_registry + "vcity/3dcitydb-pg:13-3.1-4.1.0",
        image_pull_policy=models.ImagePullPolicy.always,
        env=[
            # Assumes the corresponding config map is defined in the k8s cluster
            ConfigMapEnvFrom(
                config_map_name=cluster.configmap, optional=False
            ),
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
            # On PaGoDa if you set PGDATA by uncommenting the following line,
            # then YOU NEED TO ADJUST the value of the `initialDelaySeconds`
            # filed within the readinessProbe:
            # Env(name="PGDATA", value=results_dir),
        ],
        volumes=[
            ExistingVolume(
                claim_name=cluster.volume_claim,
                # Providing a name is mandatory but how is it relevant/used ?
                name="dummy-name",
                mount_path=parameters.persistedVolume,
            )
        ],
        # With Hera v5.1.3 you must use `readiness_probe` as opposed to the
        # aliased (refer to v1.py) readinessProbe that does not seem to work.
        # Running the workflow will NOT display any error message, but the
        # `readinessProbe` entry is simply droppped (won't appear in the
        # manifest).
        readiness_probe=models.Probe(
            exec=models.ExecAction(command=["pg_isready"]),
            # On PaGoDa, the following table holds the respective values of
            # `initialDelaySeconds` required for 3dcitydb to become properly
            # active (and a workflow using that container to succeed):
            #
            #                        |---------------------------------------|
            #                        | PGDATA value is SET | PGDATA is UNSET |
            #  |---------------------|---------------------|-----------------|
            #  | Database not yet    |        360          |                 |
            #  | created             |                     |                 |
            #  |---------------------|---------------------|       60        |
            #  | Database previously |        120          |                 |
            #  | created             |                     |                 |
            #  |---------------------|---------------------|-----------------|
            #
            # The above table values were aquired through an empirical trial
            # and error process and are probably cluster dependent.
            # Oddly enough, when the chosen value of `initialDelaySeconds` is
            # below the (respective) working threshold, AW displays an end date
            # for the Container (with a duration roughly equivalent to the
            # value of initialDelaySeconds) and the 3dcitydb initialization
            # process seems to be halted. In this case the error messages are
            # of the form:
            #    Setting up 3DCityDB database schema in database <db-name> ...
            #    <some date> UTC [101] FATAL:  role "root" does not exist
            #    <some date> UTC [108] FATAL:  role "root" does not exist
            #     ....
            initialDelaySeconds=60,
        ),
    )
    return new_container


# FIXME: these are not Tasks anymore. Change the function names
def send_command_to_postgres_container(cluster, parameters, name, arguments):
    container = Container(
        name=name,
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
            # FIXME: at some point the database name will need to be derived
            # with the vintage name
            # {{inputs.parameters.database_name}}-{{inputs.parameters.vintage}}
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
            ### FIXME DO WE NEED THE PORT IN ALL THE FOLLOWING COMMAND ?
            # The variable is parameters.database.port
        ],
        command=["/bin/bash", "-c"],
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
    arguments = ["pg_isready"]
    return send_command_to_postgres_container(
        cluster, parameters, name, arguments
    )


def db_probe_catalog_container(cluster, parameters, name):
    arguments = ["psql", "-c", "SELECT * FROM pg_catalog.pg_tables"]
    return send_command_to_postgres_container(
        cluster, parameters, name, arguments
    )


# FIXME: clean the following debugging notes
# \rm -fr citydb-lyon-2012/
# k -n argo exec -it vcity-pvc-ubuntu-pod -- rm -fr /vcity-data/junk/citydb-lyon-2012/
# python CityGMLto3DTiles_Example/3dcitydb_start_db_v513.py
# kubectl -n argo cp vcity-pvc-nginx-pod:/var/lib/www/html/junk/citydb-lyon-2012 citydb-lyon-2012
# docker run --mount type=bind,source="$(pwd)"/citydb-lyon-2012,target=/var/lib/postgresql/data -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:13
# docker ps  yields 0.0.0.0:5432->5432/tcp
# lsof -i -P | grep -i "listen" | grep 5432
# psql -l -p 5432 -h 134.214.143.170 -U postgres -W -d citydb-lyon-2012
#    no pg_hba.conf entry for host "172.17.0.1", user "postgres", database "postgres"
# vim citydb-lyon-2012/
#      -----> edit line to become             host all all 127.17.0.1/32 trust
# Relaunch docker container
# psql -l -p 5432 -h 134.214.143.170 -U postgres -W -d citydb-lyon-2012
#      -----> psql: error: connection to server at "134.214.143.170", port 5432 failed: Connection refused


# En fait le initdb de la base semble interompu avec les messages
#         running bootstrap script ... ok
#         child process was terminated by signal 15: Terminated
#         initdb: removing contents of data directory "/within-container-mount-point/junk/citydb-lyon-2012"car les messages de logs
# qui ne sont pas les même qui si on fait à la main
# docker run --mount type=bind,source=`pwd`/citydb-lyon-2012,target=/var/lib/postgresql/data -e POSTGRES_PASSWORD=postgres -e POSTGRES_USER=postgres -e POSTGRES_DB=citydb-lyon-2012 -p 5432:5432 3dcitydb/3dcitydb-pg:13-3.1-4.1.0

# Moralité: la readinessProbe ne fonctionne pas (avec ces parametres ? quoique
#  le MANIFEST ne parle pas de probe !?)
# du coup la base commence a demarrer
# mais est interompue car le workflow est fini (et mal car il n'a pas pu
# consommer la page)
# du coup la base n'est pas initialisee
# du coup on ne peut pas interoger le dump (psql -l) car le create_user n'est
# pas effectif...
#
# TO DEBUG:
# 0. les time sleep suivants ne suffisent pas: 30, 60, 120, 180...
# 1. quand on enleve PGDATA alors le boot semble etre plus rapide et du
#    coup cela passe plus souvent.
# 2. jouer sur les delais de la readinessProbe (si elle est générée) pour
#    attendre plus longtemps
