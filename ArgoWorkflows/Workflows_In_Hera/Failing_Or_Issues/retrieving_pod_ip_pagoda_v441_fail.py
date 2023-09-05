# Caveat emptor
# This is an oudated file (version 4.4.1) that now has a working
# equivalent (refer to Tutorial_Examples/retrieving_pod_ip_pagoda.py)
# and that is just kept here on historival purposes.
# Trying to fix this file would be pointless...
import sys, os

sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition")
)
from pagoda_cluster_definition import define_cluster

cluster = define_cluster()

####
from hera_utils import hera_assert_version

hera_assert_version("4.4.1")

#########################################################################
from hera import Task, Workflow

with Workflow("retrieve-deamon-pod-ip-", generate_name=True) as w:
    daemon_t = Task(
        "startpostgresdb",
        daemon=True,
        image="postgres:15.2",
    )
    consumer_t = Task(
        "isdbready",
        image="postgres:15.2",
        command=["/bin/bash", "-c"],
        args=["exec pg_isready -U user -h " + daemon_t.ip + " -p 5432"],
    )
    daemon_t >> consumer_t

w.create()
