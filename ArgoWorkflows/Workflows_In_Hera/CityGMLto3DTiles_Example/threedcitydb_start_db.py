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
#     python  CityGMLto3DTiles_Example/3dcitydb_start_db.py
# Refer to "Accessing results" chapter of the On_PaGoDA_cluster/Readme.md file
# for further details about result exploration.

if __name__ == "__main__":
    import sys, os

    sys.path.append(
        os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition")
    )
    from pagoda_cluster_definition import define_cluster
    from input_2012_tiny_import_dump import parameters

    from hera.workflows import DAG, script, Task, Workflow
    from hera_utils import hera_assert_version
    from database import (
        threedcitydb_start_db_container,
        db_isready_container,
        db_probe_catalog_container,
    )
    from utils import whalesay_container

    hera_assert_version("5.1.3")

    cluster = define_cluster()
    with Workflow(generate_name="threedcitydb-start-", entrypoint="d") as w:
        threedcitydb_start_db_c = threedcitydb_start_db_container(
            cluster, parameters
        )
        whalesay_c = whalesay_container()
        db_isready_c = db_isready_container(
            cluster, parameters, "shellprobing"
        )
        db_probe_c = db_probe_catalog_container(
            cluster, parameters, "catalogprobing"
        )
        with DAG(name="d"):
            threedcitydb_start_t = Task(
                name="startthreedcitydb", template=threedcitydb_start_db_c
            )
            whalesay_t = Task(
                name="whalesay",
                template=whalesay_c,
                arguments={"a": threedcitydb_start_t.ip},
            )
            db_isready_t = Task(
                name="shellprobing",
                template=db_isready_c,
                arguments={"hostaddr": threedcitydb_start_t.ip},
            )
            db_probe_t = Task(
                name="catalogprobing",
                template=db_probe_c,
                arguments={"hostaddr": threedcitydb_start_t.ip},
            )
            threedcitydb_start_t >> whalesay_t >> db_isready_t >> db_probe_t
    w.create()
