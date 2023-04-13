import sys
import os
from kubernetes import client, config


def assert_volume_claim(volume_name):

    # Configs can be set in Configuration class directly or using helper utility
    config.load_kube_config()

    v1 = client.CoreV1Api()
    try:
        v1.list_node()
    except:
        print("First contact (list nodes) with k8s cluster failed.")
        print("Exiting.")
        sys.exit()

    if not os.environ["ARGO_NAMESPACE"]:
        os.environ.get("ARGO_NAMESPACE")
        print("Argo namespace not defined in environment.")
        print("Exiting.")
        sys.exit()

    try:
        v1.list_namespaced_persistent_volume_claim(
            namespace=os.environ.get("ARGO_NAMESPACE")
        )
    except:
        print("Unable to list persistent volumes of the namespace.")
        print("Exiting.")
        sys.exit()

    try:
        v1.read_namespaced_persistent_volume_claim(
            namespace=os.environ.get("ARGO_NAMESPACE"),
            name=volume_name,
        )
    except:
        print("Volume claim not found.")
        print("Exiting.")
        sys.exit()


def get_volume_claim_name():
    pagoda_volume_claim_name = "vcity-pvc"
    assert_volume_claim(pagoda_volume_claim_name)
    return pagoda_volume_claim_name


if __name__ == "__main__":
    print("Cluster volume claim name:", get_volume_claim_name())
