import types
from hera.global_config import GlobalConfig
from parse_arguments import parse_arguments
from retrieve_access_token import retrieve_access_token


def define_cluster():
  ### Retrieve cluster information from arguments/environment
  args = parse_arguments()

  ### Parameters designating (with crendetials) the cluster as passed to Hera.
  # Hera transmits the information through a global variable (acting as
  # persasive context for all Hera classes) 
  GlobalConfig.host = args.server
  GlobalConfig.token = retrieve_access_token(
      args.service_account,
      namespace=args.namespace,
      config_file=args.k8s_config_file,
  )
  # The service account seems to be required as soon as the workflow has
  # to transmit the output results of a Task to the input of another Task.
  GlobalConfig.service_account_name = args.service_account
  GlobalConfig.namespace = args.namespace

  ### Other parameters that are cluster specific and that must be transmitted
  # to the workflow definition
  cluster = types.SimpleNamespace(
    docker_registry='harbor.pagoda.os.univ-lyon1.fr/' 
  )

  return cluster





