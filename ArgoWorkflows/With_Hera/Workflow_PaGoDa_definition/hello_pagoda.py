import sys, os
from hera.workflow import Workflow
from hera.task import Task
from pagoda_cluster_definition import define_cluster

define_cluster()
print(os.environ)


def print_environment():
    import os

    print("Environment variables:", os.environ)


with Workflow("hera-on-pagoda-", generate_name=True) as w:
    Task("printpythonenv", print_environment)
    Task(
        "cowsayprint",
        image="docker/whalesay",
        command=["cowsay", "The cow moos Hera from PaGoda."],
    )
w.create()
