import sys, os

sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition")
)
from pagoda_cluster_definition import define_cluster

cluster = define_cluster()

####
from hera_utils import hera_check_version
hera_check_version("4.4.2")

#########################################################################

# Hera version 4.4.2
from hera import (Task, Workflow)

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