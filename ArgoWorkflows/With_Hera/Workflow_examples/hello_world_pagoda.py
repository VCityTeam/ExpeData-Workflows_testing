import hello_world
import sys, os

sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "Workflow_PaGoDa_definition")
)
from pagoda_cluster_definition import define_cluster

define_cluster()
hello_world.define_workflow()
