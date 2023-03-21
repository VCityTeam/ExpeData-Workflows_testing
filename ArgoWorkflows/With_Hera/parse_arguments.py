import os
import sys
import argparse


def parse_arguments(logger):
    """Define a command line parser and parse the command arguments.

    :param default_service_account: the name of the service account that will be used as default value
    :return: the arguments that were retrieved by the parser
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--k8s_config_file",
        help="Path to kubernetes configuration file. Default is the value of the KUBECONFIG environment variable.",
        type=str,
        default=os.environ.get("KUBECONFIG"),
    )
    parser.add_argument(
        "--namespace",
        help="The name of the namespace. Default is the value of the ARGO_NAMESPACE environment variable.",
        type=str,
        default=os.environ.get("ARGO_NAMESPACE"),
    )
    parser.add_argument(
        "service_account",
        help="The name of the service account (holding the token). Default is the value of the ARGO_SERVICE_ACCOUNT environment variable.",
        type=str,
        default=os.environ.get("ARGO_SERVICE_ACCOUNT"),
        nargs="?",  # Optional positional argument
    )
    args = parser.parse_args()
    if args.service_account is None:
      logger.error("Name of the service account not defined: either try")
      logger.error("  - setting the ARGO_SERVICE_ACCOUNT environment variable")
      logger.error(
          "  - providing the service_account optional argument; refer to usage below"
      )
      logger.error("")
      parser.print_help()
      sys.exit()
    if args.k8s_config_file is None:
      logger.error("K8s configuration file pathname not defined: either try")
      logger.error("  - setting the KUBECONFIG environment variable")
      logger.error(
          "  - setting the --k8s_config_file argument; refer to usage below"
      )
      logger.error("")
      parser.print_help()
      sys.exit()
    if args.namespace is None:
      logger.error(
          "The namespace used by argo within k8s is not defined: either try"
      )
      logger.error("  - setting the ARGO_NAMESPACE environment variable")
      logger.error(
          "  - setting the --namespace argument; refer to usage below"
      )
      logger.error("")
      parser.print_help()
      sys.exit()
    return args
