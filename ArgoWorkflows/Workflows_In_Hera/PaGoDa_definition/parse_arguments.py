import os
import sys
import argparse
import logging


def parse_arguments(logger=logging.getLogger(__name__)):
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
        "--server",
        help="The URL of the argo server. Default is the value of the ARGO_SERVER environment variable.",
        type=str,
        default=os.environ.get("ARGO_SERVER"),
    )
    parser.add_argument(
        "--service_account",
        help="The name of the service account (holding the token). Default is the value of the ARGO_SERVICE_ACCOUNT environment variable.",
        type=str,
        default=os.environ.get("ARGO_SERVICE_ACCOUNT"),
    )
    args = parser.parse_args()

    if args.server is None:
        logger.error("Name of the service account not defined: either try")
        logger.error("  - setting the ARGO_SERVER environment variable")
        logger.error(
            "  - providing the server optional argument; refer to usage below"
        )
        logger.error("")
        parser.print_help()
        sys.exit()
    else:
        ### For some undocumented reason the ARGO_SERVER value given by the argo UI
        # can be of the form `server.domain.org:443` when Hera expects an URL of
        # form `https://server.domain.org`. Try to fix that on the fly.
        # This is kludgy and completely ad-hoc and I will deny having written that
        # excuse for a code (and yes my github account was hacked).
        if args.server.endswith(":443"):
            args.server = args.server.replace(":443", "")
        if args.server.endswith("http://"):
            args.server = args.server.replace("http://", "https://")
        if not args.server.startswith("https://"):
            args.server = "https://" + args.server

    if args.service_account is None:
        logger.error("Name of the service account not defined: either try")
        logger.error(
            "  - setting the ARGO_SERVICE_ACCOUNT environment variable"
        )
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


if __name__ == "__main__":
    args = parse_arguments()
    print("Parsed arguments:")
    print(args)
