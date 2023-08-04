from hera.workflows import models, script

import sys, os

sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition")
)
from pagoda_cluster_definition import environment


@script(
    image="python:3.9-alpine",
    command=["python"],
    image_pull_policy=models.ImagePullPolicy.if_not_present,
    # FIXME: The following introduces an undue dependency between a
    # treatment/process and an environment. This awkward resuling treatment
    # could be fixed if Hera allowed it, refer to
    # https://github.com/argoproj-labs/hera/discussions/738
    volume=environment.persisted_volume,
)
def generate_compute_tileset_configuration_file(
    vintage: int,
    database_name: str,
    hostname: str,
    password: str,
    user: str,
    port: int,
    target_directory: str,
):
    """
    Write the configuration file required by the py3dTilers stage in order
    to access the database.
    """
    import os

    os.makedirs(target_directory, exist_ok=True)
    config_filename = "CityTilerDBConfigStatic" + str(vintage) + ".yml"
    target_file = os.path.join(target_directory, config_filename)

    with open(target_file, "w") as output:
        # It seems that f-strings formating is not supported by Hera ?
        # Try uncommenting next line:
        #    output.write(f"PG_HOST: {hostname}\n")
        output.write("PG_HOST: " + hostname + "\n")
        output.write("PG_PORT: " + str(port) + "\n")
        output.write("PG_NAME: " + database_name + "\n")
        output.write("PG_USER: " + user + "\n")
        output.write("PG_PASSWORD: " + password + "\n")
        output.write("PG_VINTAGE: " + str(vintage) + "\n")
