import sys
import base64
from kubernetes import client
from hera.shared._global_config import GlobalConfig


class argo_server:
    """
    The Argo server is a part of the (Execution) Environment of the Experiment
    Refer to https://gitlab.liris.cnrs.fr/expedata/expe-data-project/-/blob/master/lexicon.md#execution-environment
    for a definition
    """

    def __init__(self, k8s_cluster, args):
        self.k8s_cluster = k8s_cluster

        if not hasattr(args, "argo_server"):
            print("Mandatory URL of Argo server not provided.")
            print("Exiting.")
            sys.exit()
        self.server = args.argo_server

        if not hasattr(args, "argo_service_account"):
            print("Mandatory argo server service account not provided.")
            print("Exiting.")
            sys.exit()
        # The service account to authenticate from.
        self.service_account = args.argo_service_account

    def __retrieve_access_token(self):
        """Retrieve the ServiceAccount token stored within the kubernetes config.
        Watch out: the returned token has nothing to do with the ARGO_TOKEN given
        by the argo UI. Both tokens are not only different by their format (the one
        returned by this function is _not_ prefixed with the `Bearer v2:` string)
        but they do _not_ correspond to the same service. This token provides access
        to the argo-server at the k8s level whereas ARGO_TOKEN provides access to
        the argo API.
        """
        try:
            service_account_content = (
                self.k8s_cluster.v1.read_namespaced_service_account(
                    self.service_account, self.k8s_cluster.namespace
                )
            )
        except client.exceptions.ApiException as e:
            raise RuntimeError(
                "Unable to retrieve service account {0} within namespace {1}.\n\nOrginal Kubernets error message:\n{2}".format(
                    self.service_account, self.k8s_cluster.namespace, e
                )
            ) from None
        secret_name = service_account_content.secrets[0].name
        secret = self.k8s_cluster.v1.read_namespaced_secret(
            secret_name, self.k8s_cluster.namespace
        ).data
        return base64.b64decode(secret["token"]).decode()

    def define_argo_server_part_of_environment(self):
        """

        Note: Hera handles its own context/environment (which ArgoWorflows to use)
          by defining the "GlobalConfig" global variable that
          - aggregates its lower level configuration variables
          - acts as a persasive context for all Hera classes
          There is thus nothing to be returned or accessed since the information
          flow is done through global variable accesses.
        """

        ### Parameters (including credentials) designating the cluster as passed to
        # Hera.
        GlobalConfig.host = self.server
        GlobalConfig.token = self.__retrieve_access_token()

        ### The service account seems to be required as soon as the workflow has
        # to transmit the output results of a Task to the input of another Task.
        GlobalConfig.service_account_name = self.service_account
        GlobalConfig.namespace = self.k8s_cluster.namespace

    def print_config(self):
        self.define_argo_server_part_of_environment()
        print("Argo server related variables used by Hera to submit workflows:")
        print("    host = ", GlobalConfig.host)
        print("    Namespace = ", GlobalConfig.namespace)
        print("    Service account = ", GlobalConfig.service_account_name)
        print("    Token = <found>")


if __name__ == "__main__":
    import logging
    from parse_arguments import parse_arguments
    from k8s_cluster_utils import k8s_cluster

    logger = logging.getLogger(__name__)
    logging.basicConfig(filename="example.log", level=logging.DEBUG)

    args = parse_arguments(logger)
    cluster = k8s_cluster(args)
    argo_server = argo_server(cluster, args)
    argo_server.print_config()

    print("Argo server looks ok.")
