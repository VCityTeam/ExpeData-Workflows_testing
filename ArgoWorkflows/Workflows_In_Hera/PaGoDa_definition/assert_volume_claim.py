import sys
import os
from kubernetes import client, config
from assert_argo_namespace_pods import assert_argo_namespace_pods


def assert_volume_claim(volume_name):
    assert_argo_namespace_pods()  # Guarantees that ARGO_NAMESPACE is defined
    namespace = os.environ.get("ARGO_NAMESPACE")
    # Configs can be set in Configuration class directly or using helper utility
    config.load_kube_config()
    v1 = client.CoreV1Api()

    try:
        v1.list_namespaced_persistent_volume_claim(namespace=namespace)
    except:
        print("Unable to list persistent volumes of the namespace.")
        print("Exiting.")
        sys.exit()

    try:
        v1.read_namespaced_persistent_volume_claim(
            namespace=namespace,
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
