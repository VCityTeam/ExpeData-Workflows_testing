import sys
import os
from kubernetes import client, config


def assert_pagoda_configmap(configmap_name):

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
        v1.list_namespaced_config_map(
            namespace=os.environ.get("ARGO_NAMESPACE")
        )
    except:
        print("Unable to list configuration maps of the namespace.")
        print("Exiting.")
        sys.exit()

    try:
        v1.read_namespaced_config_map(
            namespace=os.environ.get("ARGO_NAMESPACE"),
            name=configmap_name,
        )
    except:
        print("PaGoDa cluster configuration map not defined.")
        print("Exiting.")
        sys.exit()


def get_configmap_name():
    pagoda_configmap_name = "vcity-pagoda-proxy-environment"
    assert_pagoda_configmap(pagoda_configmap_name)
    return pagoda_configmap_name


if __name__ == "__main__":
    print("Cluster configuration name:", get_configmap_name())
