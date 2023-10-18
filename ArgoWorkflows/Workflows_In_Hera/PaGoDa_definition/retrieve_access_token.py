import base64
import errno
import os
from typing import Optional
import logging
from kubernetes import client, config

logger = logging.getLogger(__name__)


def retrieve_access_token(
    service_account: str,
    namespace: str = "default",
    config_file: Optional[str] = None,
):
    """Get ServiceAccount token using kubernetes config.
    Watch out: the returned token has nothing to do with the ARGO_TOKEN given
    by argo UI. Both tokens are not only different by their format (the one
    returned by this function is _not_ prefixed with the `Bearer v2:` string)
    but they do _not_ correspond to the same service. This token provides access
    to the argo-server at the k8s level whereas ARGO_TOKEN provides access to
    the argo API.
     Parameters
    ----------
    service_account: str
        The service account to authenticate from.
    namespace: str = 'default'
        The K8S namespace the workflow service submits workflows to. This defaults to the `default` namespace.
    config_file:
        The path to k8s configuration file.
     Raises
    ------
    FileNotFoundError
        When the config_file can not be found.
    """
    if config_file is None:
        logger.error("K8s configuration file pathname not set.")
        raise FileNotFoundError(
            errno.ENOENT, os.strerror(errno.ENOENT), config_file
        )
    if not os.path.isfile(config_file):
        logger.error("K8s configuration file pathname is not valid.")
        raise FileNotFoundError(
            errno.ENOENT, os.strerror(errno.ENOENT), config_file
        )

    config.load_kube_config(config_file=config_file)
    v1 = client.CoreV1Api()
    try:
        service_account_content = v1.read_namespaced_service_account(
            service_account, namespace
        )
    except client.exceptions.ApiException as e:
        raise RuntimeError(
            "Unable to retrieve service account {0} within namespace {1}.\n\nOrginal Kubernets error message:\n{2}".format(
                service_account, namespace, e
            )
        ) from None
    secret_name = service_account_content.secrets[0].name
    secret = v1.read_namespaced_secret(secret_name, namespace).data
    return base64.b64decode(secret["token"]).decode()


if __name__ == "__main__":
    from parse_arguments import parse_arguments

    args = parse_arguments()
    print(args)

    token = retrieve_access_token(
        args.service_account,
        namespace=args.namespace,
        config_file=args.k8s_config_file,
    )
    print("The retrieved token is {}".format(token))
