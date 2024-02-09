import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition"))
from hera_utils import hera_assert_version

hera_assert_version("5.6.0")
from pagoda_environment_definition import environment

####
# THE NEED: we need to build containers (based on the same image) that
# differ by arguments given at Hera submission stage (and that we wish
# to "burn" into each respective container). In this use case the
# container "build-in" name (that is the name argument provided to the
# Container class constructor) is not used by the workflow to
# distinguish the different containers (instead we keep track of the
# the python Container objects).
#
# The PROBLEM: alas name is a required argument of the Container
# constructor. In addition container names have to be unique accross
# the set of build containers. Hence we need to provide a set of
# container names when these names are meaningless for the workflow
# definition and usage.
# 
# REPRODUCING THE PROBLEM: it suffice to change the definition of
# the get_new_identifier() function to return any arbitrary (fixed)
# string (e.g. return "dummy"). Then at Hera submission stage one
# gets the following error message:
#       hera.exceptions.BadRequest: Server returned status code 400
#       with message: `spec.templates[1].name 'dummy' is not unique`
#
# PROPOSED SOLUTION: ramdomly generate unique container names.
####
import uuid
from hera.workflows import Container, DAG, Task, Workflow


def get_new_identifier():
    # FIXME: Is this guaranteed to be without collisions ? In other terms
    # is it possible to generate two identical identifiers ?
    # NOTE (AW constrain): container names must be a lowercase RFC 1123
    # subdomain that must consist of lower case alphanumeric characters,
    # '-' or '.', and must start and end with an alphanumeric character
    # (e.g. 'example.com', regex used for validation is
    # '[a-z0-9]([-a-z0-9]*[a-z0-9])?(\.[a-z0-9]([-a-z0-9]*[a-z0-9])?)*')
    return uuid.uuid4().hex[:6].lower()


def define_container(message: str):
    return Container(
        name=get_new_identifier(),
        image="docker/whalesay",
        command=["cowsay", message],
    )


with Workflow(generate_name="nameless-container-name-", entrypoint="main") as w:
    container_a = define_container("Moo Hera")
    container_b = define_container("Hera Moo")
    with DAG(name="main"):
        task_a = Task(name="a", template=container_a)
        task_b = Task(name="b", template=container_b)
        task_a >> task_b

w.create()
