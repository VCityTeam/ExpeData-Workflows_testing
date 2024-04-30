import os
import sys
import configargparse
import logging


def parse_arguments(logger=logging.getLogger(__name__)):
    """Define a command line parser and parse the command arguments.

    :param default_service_account: the name of the service account that will be used as default value
    :return: the arguments that were retrieved by the parser
    """
    ### Retrieve the configuration files (when they are present)
    default_config_files = list()
    argo_homedir_configfile_path = "~/hera.config"
    if os.path.exists(argo_homedir_configfile_path):
        default_config_files.append(argo_homedir_configfile_path)
    argo_cwd_configfile_path = os.path.join(os.getcwd(), "hera.config")
    if os.path.exists(argo_cwd_configfile_path):
        default_config_files.append(argo_cwd_configfile_path)
    if os.environ.get("ARGOCONFIG"):
        argo_configfile_path = os.environ.get("ARGOCONFIG")
        if os.path.exists(argo_configfile_path):
            default_config_files.append(argo_configfile_path)
        else:
            logger.error(
                "Erroneous ARGOCONFIG environment variable value: ",
                argo_configfile_path,
            )
            print("Argo configuration file ", argo_configfile_path, " ignored")
    if default_config_files:
        print("Found config files: ", default_config_files)

    parser = configargparse.ArgParser(default_config_files=default_config_files)
    parser.add(
        "--k8s_config_file",
        help="Path to kubernetes configuration file. Default is the value of the KUBECONFIG environment variable.",
        type=str,
        default=os.environ.get("KUBECONFIG"),
    )
    parser.add(
        "--k8s_configmap_name",
        help="Name of the k8s configuration map used by cluster admin to transmit cluster specific configurations.",
        type=str,
        default=os.environ.get("KUBECONFIGMAP"),
    )
    parser.add(
        "--k8s_volume_claim_name",
        help="Name of the k8s volume claim to be used by numerical experiment.",
        type=str,
        default=os.environ.get("KUBEVOLUMECLAIMNAME"),
    )
    parser.add(
        "--argo_namespace",
        help="The name of the namespace. Default is the value of the ARGO_NAMESPACE environment variable.",
        type=str,
        default=os.environ.get("ARGO_NAMESPACE"),
    )
    parser.add(
        "--argo_server",
        help="The URL of the argo server. Default is the value of the ARGO_SERVER environment variable.",
        type=str,
        default=os.environ.get("ARGO_SERVER"),
    )
    parser.add(
        "--argo_service_account",
        help="The name of the service account (holding the token). Default is the value of the ARGO_SERVICE_ACCOUNT environment variable.",
        type=str,
        default=os.environ.get("ARGO_SERVICE_ACCOUNT"),
    )
    args = parser.parse_args()

    ######### K8s cluster level
    if args.k8s_config_file is None:
        logger.error("K8s configuration file pathname not defined: either try")
        logger.error("  - setting the KUBECONFIG environment variable")
        logger.error("  - setting the --k8s_config_file argument; refer to usage below")
        logger.error("")
        parser.print_help()
        sys.exit()

    if args.k8s_configmap_name is None:
        logger.debug("The optionnal name of the k8s configuration map (used by")
        logger.debug("cluster admin to transmit cluster specific configurations).")
        logger.debug("was not provided. When needed either try")
        logger.error("  - setting the KUBECONFIGMAP environment variable")
        logger.error(
            "  - setting the --k8s_configmap_name argument; refer to usage below"
        )
        parser.print_help()

    ######### Argo Worflow server layer
    if args.argo_server is None:
        logger.error("The name of the argo server was not provided: either try")
        logger.error("  - setting the ARGO_SERVER environment variable")
        logger.error("  - setting the ARGO_SERVER environment variable")
        logger.error(
            "  - providing the argo_server optional CLI argument; refer to usage below"
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
        if args.argo_server.endswith(":443"):
            args.argo_server = args.argo_server.replace(":443", "")
        if args.argo_server.endswith("http://"):
            args.argo_server = args.argo_server.replace("http://", "https://")
        if not args.argo_server.startswith("https://"):
            args.argo_server = "https://" + args.argo_server

    if args.argo_service_account is None:
        logger.error("Name of the service account not defined: either try")
        logger.error("  - setting the ARGO_SERVICE_ACCOUNT environment variable")
        logger.error(
            "  - providing the service_account optional argument; refer to usage below"
        )
        logger.error("")
        parser.print_help()
        sys.exit()

    if args.argo_namespace is None:
        logger.error("The namespace used by argo within k8s is not defined: either try")
        logger.error("  - setting the ARGO_NAMESPACE environment variable")
        logger.error("  - setting the --namespace argument; refer to usage below")
        logger.error("")
        parser.print_help()
        sys.exit()
    return args


if __name__ == "__main__":
    import logging

    logger = logging.getLogger(__name__)
    logging.basicConfig(filename="example.log", level=logging.DEBUG)

    args = parse_arguments(logger)
    print("Parsed arguments:")
    print(args)
