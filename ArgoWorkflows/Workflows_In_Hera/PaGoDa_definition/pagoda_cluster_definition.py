import types
from hera.global_config import GlobalConfig
from parse_arguments import parse_arguments
from retrieve_access_token import retrieve_access_token
from assert_pagoda_configmap import get_configmap_name
from assert_volume_claim import get_volume_claim_name


def define_cluster():
    ### Retrieve cluster information from arguments/environment
    args = parse_arguments()

    ### Parameters designating (with crendetials) the cluster as passed to Hera.
    # Hera transmits the information through a global variable (acting as
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
    cluster = types.SimpleNamespace(
        docker_registry="harbor.pagoda.os.univ-lyon1.fr/"
    )

    ### Some tasks require to retrieve cluster specific environment
    # (e.g. HTTP_PROXY) values at runtime. They do by retrieving the ad-hoc
    # k8s configuration map. Assert this map exists.
    cluster.configmap = get_configmap_name()

    ### A persistent volume (defined at the k8s level) can be used by
    # tasks of a workflow in order to flow output results from an upstream
    # task to a downstream one, and persist once the workflow is finished
    cluster.volume_claim = get_volume_claim_name()

    return cluster


if __name__ == "__main__":
    import json

    print("CLI arguments/environment variables:")
    print(json.dumps(parse_arguments().__dict__, indent=4))

    cluster = define_cluster()
    print("Derived cluster variables:")
    print("  - Hera global variables: ")
    print("    host = ", GlobalConfig.host)
    print("    Namespace = ", GlobalConfig.namespace)
    print("    Service account = ", GlobalConfig.service_account_name)
    print("    Token = <found>")

    print("  - Python level cluster definitions: ")
    print(json.dumps(cluster.__dict__, indent=4))
