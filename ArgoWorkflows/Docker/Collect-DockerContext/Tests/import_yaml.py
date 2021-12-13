import yaml

with open('../../../workflow_input.yaml') as stream:
  try:
    parsed_yaml=yaml.safe_load(stream)
    print(parsed_yaml)
  except yaml.YAMLError as e:
    print(e)
