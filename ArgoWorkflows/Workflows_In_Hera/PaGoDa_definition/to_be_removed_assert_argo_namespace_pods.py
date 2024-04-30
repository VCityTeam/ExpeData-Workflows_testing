import sys
from kubernetes import client, config


def assert_argo_namespace_pods(args):

    if not hasattr(args, "k8s_config_file"):
        print("The Kubernetes configuration file (k8s_config_file) was not provided.")
        print("Exiting.")
        sys.exit()
    # Configs can be set in Configuration class directly or using helper utility
    config.load_kube_config(args.k8s_config_file)

    v1 = client.CoreV1Api()
    try:
        v1.list_node()
    except:
        print("First contact (list all nodes) with k8s cluster failed.")
        print("Exiting.")
        sys.exit()

    if not hasattr(args, "argo_namespace"):
        print("The argo namespace was not defined.")
        print("Exiting.")
        sys.exit()

    try:
        v1.list_namespaced_pod(namespace=args.argo_namespace)
    except:
        print("Listing nodes in Argo namespace (k8s cluster level) failed.")
        print("Exiting.")
        sys.exit()

    return True


if __name__ == "__main__":
    import logging
    from parse_arguments import parse_arguments

    logger = logging.getLogger(__name__)
    logging.basicConfig(filename="example.log", level=logging.DEBUG)

    args = parse_arguments(logger)
    assert_argo_namespace_pods(args)
    print("Argo namespace pods are accessible.")
