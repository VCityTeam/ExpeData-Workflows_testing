import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition"))

########
from hera.workflows import Container, ExistingVolume, models, Parameter, script


@script(
    image="python:3.9-alpine",
    command=["python"],
    image_pull_policy=models.ImagePullPolicy.if_not_present,
    inputs=[
        Parameter(name="claim_name"),
        Parameter(name="mount_path"),
        Parameter(name="database_hostname"),
        Parameter(name="database_password"),
        Parameter(name="database_user"),
        Parameter(name="database_port"),
        Parameter(name="database_name"),
        Parameter(name="vintage"),
        Parameter(name="target_directory"),
    ],
    # LIMIT: as opposed to container definition, it seems HERA does not allow
    # for scripts to declare the volume that a task (using the script) will use
    # in the Task definition. Instead one has to define the volumes within the
    # script definition itself. This limitation introduces an undue dependency
    # between a process (the script) and its environment (the cluster volume
    # claims).
    # In addition the specification of the volume, that has to be in the
    # @script decorator section (it's a context of execution of the script),
    # must be partly done in Argo (altough Hera might someday offer a more
    # pythonic expression refer to
    # https://github.com/argoproj-labs/hera/discussions/738 )
    volumes=[
        ExistingVolume(
            # Providing a name is mandatory but how is it relevant/usefull ?
            name="dummy-name",
            claim_name="{{inputs.parameters.claim_name}}",
            mount_path="{{inputs.parameters.mount_path}}",
        )
    ],
)
def generate_compute_tileset_configuration_file(
    # Implicit argument refered by the @script(volume=<>) section:
    claim_name: str,
    mount_path: str,
    # In between Environment and Experiment arguments (Conductor's responsibility)
    database_hostname: str,
    database_password: str,
    database_user: str,
    database_port: int,
    # (Numerical) Experiment arguments
    database_name: str,
    vintage: int,
    target_directory: str,
):
    """
    Write the configuration file required by the py3dTilers stage in order
    to access the database.
    """
    import os

    print("Target directory", target_directory)
    os.makedirs(target_directory, exist_ok=True)

    config_filename = "CityTilerDBConfigStatic" + str(vintage) + ".yml"
    target_file = os.path.join(target_directory, config_filename)
    print("Target filename: ", target_file)

    with open(target_file, "w") as output:
        # LIMIT: Although the container specifies that it must use Python
        # version 3.9 (that accepts f-strings), it seems that f-strings
        # formating is not supported by Hera ? Try uncommenting the next line
        #    output.write(f"PG_HOST: {hostname}\n")
        # and watch the execution crash.
        output.write("PG_HOST: " + database_hostname + "\n")
        output.write("PG_PORT: " + str(database_port) + "\n")
        output.write("PG_NAME: " + database_name + "\n")
        output.write("PG_USER: " + database_user + "\n")
        output.write("PG_PASSWORD: " + database_password + "\n")
        output.write("PG_VINTAGE: " + str(vintage) + "\n")

    print(
        "List of target_directory files on exiting: ",
        os.listdir(target_directory),
    )


def compute_tileset_container(
    environment, output_directory, configuration_filename, container_name
):
    arguments = (
        "cd "
        + os.path.join(environment.persisted_volume.mount_path, output_directory)
        + " && citygml-tiler --type building -i "
        + configuration_filename
    )
    new_container = Container(
        name=container_name,
        image=environment.cluster.docker_registry + "vcity/py3dtilers:0.1",
        image_pull_policy=models.ImagePullPolicy.always,
        command=["/bin/bash", "-cv"],
        args=[arguments],  # A list with a single string
        volumes=[
            ExistingVolume(
                name="dummy-name",  # LIMIT: Mandatory but how is it usefull ?
                claim_name=environment.persisted_volume.claim_name,
                mount_path=environment.persisted_volume.mount_path,
            )
        ],
    )
    return new_container
