import sys
from kubernetes import client, config
from assert_argo_namespace_pods import assert_argo_namespace_pods


def assert_volume_claim(args):
    if not hasattr(args, "k8s_volume_claim_name"):
        print("The volume claim name of the Kubernetes cluster was not provided.")
        print("Exiting.")
        sys.exit()
    # First assert that argo_namespace was properly defined and that the k8s
    # cluster is accessible:
    assert_argo_namespace_pods(args)

    # Designate (again) the k8s cluster to be inquired
    config.load_kube_config(args.k8s_config_file)
    v1 = client.CoreV1Api()

    # First, trying listing the existing volume claims:
    try:
        v1.list_namespaced_persistent_volume_claim(namespace=args.argo_namespace)
    except:
        print("Unable to list persistent volumes of the namespace.")
        print("Exiting.")
        sys.exit()

    try:
        v1.read_namespaced_persistent_volume_claim(
            namespace=args.argo_namespace,
            name=args.k8s_volume_claim_name,
        )
    except:
        print("The ", args.k8s_volume_claim_name, " volume claim not found.")
        print("Exiting.")
        sys.exit()


if __name__ == "__main__":
    import logging
    from parse_arguments import parse_arguments

    logger = logging.getLogger(__name__)
    logging.basicConfig(filename="example.log", level=logging.DEBUG)

    args = parse_arguments(logger)
    assert_volume_claim(args)
    print(
        "The cluster volume claim ",
        args.k8s_volume_claim_name,
        " was properly retrieved.",
    )
