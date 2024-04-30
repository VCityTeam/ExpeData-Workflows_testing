# A set of utility functions for interacting with a Kubernetes cluster

import sys
from kubernetes import client, config


class k8s_cluster:
    def __init__(self, args):
        if not hasattr(args, "k8s_config_file"):
            print("The configuration file of the Kubernetes cluster was not provided.")
            print("Exiting.")
            sys.exit()
        self.__k8s_config_file = args.k8s_config_file
        # Configs can be set in Configuration class directly or using helper utility
        config.load_kube_config(self.__k8s_config_file)
        self.v1 = client.CoreV1Api()

        if not hasattr(args, "argo_namespace"):
            print("Defaulting Kubernetes cluster namespace.")
            self.namespace = "default"
        else:
            self.namespace = args.argo_namespace

    def print_config(self):
        print("K8s cluster server related variables:")
        print("    Configuration file = ", self.__k8s_config_file)
        print("    Namespace = ", self.namespace)

    def assert_cluster(self):
        """Assert the cluster can be contacted by listing its nodes."""
        try:
            self.v1.list_node()
        except:
            print("First handshake (list all nodes) with k8s cluster failed.")
            print("Exiting.")
            sys.exit()
        return True

    def assert_namespace(self):
        """Assert that the namespace exists and is accessible by listing its pods"""

        # First assert the precondition
        self.assert_cluster()

        # Then assert the namespace validity by listing its pods.
        try:
            self.v1.list_namespaced_pod(namespace=self.namespace)
        except:
            print("Listing k8s cluster nodes of namespace ", self.namespace, " failed.")
            print("Exiting.")
            sys.exit()

        return True

    def assert_volume_claim(self, k8s_volume_claim_name):
        # First assert the preconditions
        self.assert_namespace()

        # Then, trying listing all the existing volume claims:
        try:
            self.v1.list_namespaced_persistent_volume_claim(namespace=self.namespace)
        except:
            print(
                "Unable to list k8s cluster persistent volumes of namespace ",
                self.namespace,
            )
            print("Exiting.")
            sys.exit()

        # Eventually, check the designated volume claim
        try:
            self.v1.read_namespaced_persistent_volume_claim(
                namespace=self.namespace,
                name=k8s_volume_claim_name,
            )
        except:
            print(
                "The k8s cluster ",
                k8s_volume_claim_name,
                " volume claim was not found.",
            )
            print("Exiting.")
            sys.exit()
        return True

    def assert_configmap(self, k8s_configmap_name):

        # First assert the preconditions
        self.assert_namespace()

        # Then, try listing all the existing config maps:
        try:
            self.v1.list_namespaced_config_map(namespace=self.namespace)
        except:
            print(
                "Unable to list configuration maps of the ",
                self.namespace,
                " namespace.",
            )
            print("Exiting.")
            sys.exit()

        # Eventually, check the designated configmap
        try:
            self.v1.read_namespaced_config_map(
                namespace=self.namespace,
                name=k8s_configmap_name,
            )
        except:
            print(
                "The ",
                k8s_configmap_name,
                "config map could not be retrieve from cluster.",
            )
            print("Exiting.")
            sys.exit()
        return True


if __name__ == "__main__":
    import logging
    from parse_arguments import parse_arguments

    logger = logging.getLogger(__name__)
    logging.basicConfig(filename="example.log", level=logging.DEBUG)

    args = parse_arguments(logger)
    cluster = k8s_cluster(args)
    cluster.assert_volume_claim(args.k8s_volume_claim_name)
    cluster.assert_configmap(args.k8s_configmap_name)
    print("Kubernetes cluster seems ok.")
