# The following pipeline uses input_2012_tiny_import_dump.py as parameter file.
# When `parameters.database.keep_database` is set, an initialized 3DCityDB is
# serialized (to files as opposed to a database dump). Unless you wish to start
# the 3DCityDabase from a previous database serialisation, you might want to
# start from a clean slate and remove any possibly pre-existing database
# serialization (that would exist on the k8s volume) with the command :
# k -n argo exec -it vcity-pvc-ubuntu-pod -- rm -fr /vcity-data/junk/citydb-lyon-2012/
# (concerning the vcity-pvc-ubuntu-pod pod refer to the "Accessing results"
# chapter of the On_PaGoDA_cluster/Readme.md file).
# Running this pipeline is now done with
#     python  CityGMLto3DTiles_Example/threedcitydb_start_db.py
# Refer to "Accessing results" chapter of the On_PaGoDA_cluster/Readme.md file
# for further details about result exploration.

import sys, os

sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition")
)

from hera.workflows import (
    models,
    Parameter,
    script,
    Step,
    Steps,
    Task,
    WorkflowTemplate,
)
from hera_utils import hera_assert_version
from database import threedcitydb_start_db_container, define_checkdb_template
from utils import whalesay_container

hera_assert_version("5.6.0")


if __name__ == "__main__":
    from pagoda_cluster_definition import define_cluster
    from input_2012_tiny_import_dump import parameters
    from hera.workflows import DAG, Workflow

    cluster = define_cluster()
    define_checkdb_template(cluster, parameters)
    with Workflow(generate_name="threedcitydb-start-", entrypoint="main") as w:
        threedcitydb_start_db_c = threedcitydb_start_db_container(
            cluster, parameters
        )
        with DAG(name="main") as s:
            threedcitydb_start_t = Task(
                name="startthreedcitydb", template=threedcitydb_start_db_c
            )
            checkdb_t = Task(
                name="checkdb",
                template_ref=models.TemplateRef(
                    name="workflow-startdb",
                    template="checkdb-template",
                ),
                arguments={"dbhostaddr": threedcitydb_start_t.ip},
            )
            threedcitydb_start_t >> checkdb_t
    w.create()
