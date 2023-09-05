from hera_utils import hera_check_version, hera_assert_version

if hera_check_version("5.6.0") or hera_check_version("5.1.3"):
    from hera.shared._global_config import GlobalConfig
elif hera_check_version("4.4.1"):
    from hera.global_config import GlobalConfig
else:
    hera_assert_version("X.X.X")  # Will fail

from hera.workflows import ExistingVolume

import types
import json
from parse_arguments import parse_arguments
from retrieve_access_token import retrieve_access_token
from assert_pagoda_configmap import get_configmap_name
from assert_volume_claim import get_volume_claim_name


def define_cluster_part_of_environment():
    """
    Define the (Execution) Environment of the Experiment
    Refer to https://gitlab.liris.cnrs.fr/expedata/expe-data-project/-/blob/master/lexicon.md#execution-environment
    for a definition
    """

    class Struct:
        def toJSON(self):
            return json.dumps(
                self, default=lambda o: o.__dict__, sort_keys=True, indent=4
            )

    environment = Struct()

    ### Retrieve cluster information from arguments/environment
    args = parse_arguments()

    ### Parameters (including credentials) designating the cluster as passed to
    # Hera. Hera transmits the information through a global variable (acting as
    # persasive context for all Hera classes)
    GlobalConfig.host = args.server
    GlobalConfig.token = retrieve_access_token(
        args.service_account,
        namespace=args.namespace,
        config_file=args.k8s_config_file,
    )

    ### The service account seems to be required as soon as the workflow has
    # to transmit the output results of a Task to the input of another Task.
    GlobalConfig.service_account_name = args.service_account
    GlobalConfig.namespace = args.namespace

    ### Other parameters that are cluster specific and that must be transmitted
    # to the workflow definition
    environment.cluster = types.SimpleNamespace(
        docker_registry="harbor.pagoda.os.univ-lyon1.fr/"
    )

    ### Some tasks require to retrieve cluster specific environment
    # (e.g. HTTP_PROXY) values at runtime. They do by retrieving the ad-hoc
    # k8s configuration map. Assert this map exists.
    environment.cluster.configmap = get_configmap_name()

    ### A persistent volume (defined at the k8s level) can be used by
    # tasks of a workflow in order to flow output results from an upstream
    # task to a downstream one, and persist once the workflow is finished
    environment.persisted_volume = Struct()
    environment.persisted_volume.claim_name = get_volume_claim_name()

    return environment


environment = define_cluster_part_of_environment()
# The mount path is technicality standing in between Environment and
# Experiment related notions: more precisely it is a technicality that should
# be dealt by the (Experiment) Conductor (refer to
# https://gitlab.liris.cnrs.fr/expedata/expe-data-project/-/blob/master/lexicon.md#conductor )
environment.persisted_volume.mount_path = "/within-container-mount-point"


if __name__ == "__main__":
    from hera_utils import hera_print_version

    hera_print_version()

    print("CLI arguments/environment variables:")
    print(json.dumps(parse_arguments().__dict__, indent=4))

    # The following implictly assumes that environement was defined as
    #    environment=define_cluster_part_of_environment()
    print("Cluster related variables (either direct or derived):")
    print("  - Hera global variables: ")
    print("    host = ", GlobalConfig.host)
    print("    Namespace = ", GlobalConfig.namespace)
    print("    Service account = ", GlobalConfig.service_account_name)
    print("    Token = <found>")

    print(
        "Environment (of numerical experiment related definition",
        " (at Python level):",
    )
    print(environment.toJSON())
