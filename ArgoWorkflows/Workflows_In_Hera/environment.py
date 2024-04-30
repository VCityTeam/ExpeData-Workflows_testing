import types
import json
import logging
from hera_utils import parse_arguments, k8s_cluster, argo_server


class Struct:
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


class numerical_experiment_environment(Struct):

    def __init__(self, k8s_cluster, args):
        """The CLI arguments (parameters) are collected at three levels:
        - the ones designating the underlyin k8s cluster, and
        - the ones designating the Argo server,
        - the remaining ones that are still required to run the workflows and
          that are gathered within this numerical_experiment environment class.

        :param k8s_cluster: k8s cluster used to assert that the environment
                            elements are properly accessible.
        :param args: the CLI arguments holding the environment tidbits.
        """

        # The information that are "close/related" to k8s server that will be
        # required to run the workflows. This is to be distinguished from the
        # k8s cluster it self on top of which the argo server is deployed.
        # The numerical experiment can be defined
        self.cluster = types.SimpleNamespace(
            docker_registry="harbor.pagoda.os.univ-lyon1.fr/"
        )

        ### Some tasks require to retrieve cluster specific environment
        # (e.g. HTTP_PROXY) values at runtime. This retrieval is done through an
        # ad-hoc k8s configuration map. Assert this map exists.
        k8s_cluster.assert_configmap(args.k8s_configmap_name)
        self.cluster.configmap = args.k8s_configmap_name

        ### A persistent volume (defined at the k8s level) can be used by
        # tasks of a workflow in order to flow output results from an upstream
        # task to a downstream one, and persist once the workflow is finished
        self.persisted_volume = Struct()
        k8s_cluster.assert_volume_claim(args.k8s_volume_claim_name)
        self.persisted_volume.claim_name = args.k8s_volume_claim_name

        # The mount path is technicality standing in between Environment and
        # Experiment related notions: more precisely it is a technicality that should
        # be dealt by the (Experiment) Conductor (refer to
        # https://gitlab.liris.cnrs.fr/expedata/expe-data-project/-/blob/master/lexicon.md#conductor )
        self.persisted_volume.mount_path = "/within-container-mount-point"

    def print_config(self):
        print("Environment of numerical experiment (at Python level):")
        print(self.toJSON())


def construct_environment(args, verbose=False):
    k8s = k8s_cluster(args)
    k8s.assert_cluster()
    if verbose:
        k8s.print_config()
        print("Kubernetes cluster seems ok.")
        print("")

    argo = argo_server(k8s, args)
    argo.define_argo_server_part_of_environment()
    if verbose:
        argo.print_config()
        print("Argo server looks ok.")
        print("")

    # The above components of the environment are not stored. They are
    # used by HERA to submit the workflow to the Argo server (thus at
    # submission stage).
    # The remanining elements of the environment are integrated in the
    # workflow definitions (and retrieved by the Argo engine at workflow
    # execution stage)
    environment = numerical_experiment_environment(k8s, args)
    if verbose:
        environment.print_config()

    return environment


if __name__ == "__main__":
    from hera_utils import check_version, print_version

    if not check_version("5.6.0"):
        print("Hera version ")
        print_version()
        print(" is untested.")

    logger = logging.getLogger(__name__)
    logging.basicConfig(filename="example.log", level=logging.DEBUG)

    args = parse_arguments(logger)
    print("CLI arguments/environment variables:")
    print(json.dumps(args.__dict__, indent=4))
    print("")

    environment = construct_environment(args, verbose=True)
