import sys
import os
from kubernetes import client, config


def assert_argo_namespace_pods():
    if not os.environ["ARGO_NAMESPACE"]:
        print("ARGO_NAMESPACE environment variable not defined.")
        print("Exiting.")
        sys.exit()

    # Configs can be set in Configuration class directly or using helper utility
    config.load_kube_config()

    v1 = client.CoreV1Api()
    try:
        v1.list_node()
    except:
        print("First contact (list all nodes) with k8s cluster failed.")
        print("Exiting.")
        sys.exit()

    try:
        v1.list_namespaced_pod(namespace=os.environ.get("ARGO_NAMESPACE"))
    except:
        print("Listing nodes in Argo namespace (k8s cluster level) failed.")
        print("Exiting.")
        sys.exit()

    return True


if __name__ == "__main__":
    assert_argo_namespace_pods()
    print("Argo namespace pods are accessible.")
