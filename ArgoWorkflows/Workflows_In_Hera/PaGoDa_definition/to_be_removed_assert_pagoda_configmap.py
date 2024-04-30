import sys
from kubernetes import client, config
from assert_argo_namespace_pods import assert_argo_namespace_pods


def assert_pagoda_configmap(args):
    if not hasattr(args, "k8s_configmap_name"):
        print(
            "The name of the Kubernetes configmap file (k8s_configmap_name) was not provided."
        )
        print("Exiting.")
        sys.exit()
    # First assert that argo_namespace was properly defined and that the k8s
    # cluster is accessible:
    assert_argo_namespace_pods(args)

    # Designate (again) the k8s cluster to be inquired
    config.load_kube_config(args.k8s_config_file)
    v1 = client.CoreV1Api()

    # First, try listing the existing config maps:
    try:
        v1.list_namespaced_config_map(namespace=args.argo_namespace)
    except:
        print("Unable to list configuration maps of the namespace.")
        print("Exiting.")
        sys.exit()

    try:
        v1.read_namespaced_config_map(
            namespace=args.argo_namespace,
            name=args.k8s_configmap_name,
        )
    except:
        print(
            "The ",
            args.k8s_configmap_name,
            "config map could not be retrieve from cluster.",
        )
        print("Exiting.")
        sys.exit()


if __name__ == "__main__":
    import logging
    from parse_arguments import parse_arguments

    logger = logging.getLogger(__name__)
    logging.basicConfig(filename="example.log", level=logging.DEBUG)

    args = parse_arguments(logger)
    assert_pagoda_configmap(args)
    print("Cluster config map ", args.k8s_configmap_name, " properly retrieved.")
