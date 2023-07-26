import sys
import os
from kubernetes import client, config
from hera.workflows import WorkflowsService
from hera._version import version


def hera_print_version():
    print("Installed Hera version: ", version)


def hera_check_version(version_to_check):
    if version_to_check == version:
        return True
    return False


def hera_assert_version(version_to_check):
    if hera_check_version(version_to_check):
        return True
    print("Unsuported Hera version:", version_to_check)
    hera_print_version()
    sys.exit()


def hera_clear_workflow_template(cluster, workflow_template_name):
    # Cluster must be properly defined for WorkflowsService to be properly
    # created (under the hood WorkflowsService uses Hera's GlobalConfig global
    # variable (e.g. GlobalConfig.host, GlobalConfig.token or
    # GlobalConfig.namespace ...). We thus pass the cluster variable as an
    # explicit reminder of this implicit dependency.
    service = WorkflowsService()
    workflow_templates = service.list_workflow_templates().items
    for workflow_template in workflow_templates:
        if workflow_template.metadata.name == workflow_template_name:
            # A workflow_template (with the same name) is already registered and
            # it must thus be flushed
            print("Deleting Workflow Template ", workflow_template_name)
            service.delete_workflow_template(workflow_template_name)
