from hera.global_config import GlobalConfig
from parse_arguments import parse_arguments
from retrieve_access_token import retrieve_access_token

def define_cluster():
  args = parse_arguments()

  GlobalConfig.host = args.server
  GlobalConfig.token = retrieve_access_token(
      args.service_account,
      namespace=args.namespace,
      config_file=args.k8s_config_file,
  )
  GlobalConfig.namespace = args.namespace





