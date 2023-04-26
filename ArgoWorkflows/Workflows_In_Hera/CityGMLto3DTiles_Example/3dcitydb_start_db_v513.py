if __name__ == "__main__":
    import sys, os

    sys.path.append(
        os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition")
    )
    from pagoda_cluster_definition import define_cluster
    from input_2012_tiny_import_dump import parameters

    from hera.workflows import DAG, Task, Workflow
    from hera_utils import hera_assert_version
    from database_v513 import (
        threedcitydb_start_db_container_constructor,
        readiness_probe_container_constructor,
    )
    from utils import whalesay_container_constructor

    hera_assert_version("5.1.3")

    cluster = define_cluster()
    with Workflow(generate_name="threedcitydb-start-", entrypoint="d") as w:
        whalesay_c = whalesay_container_constructor()
        threedcitydb_start_db_c = threedcitydb_start_db_container_constructor(
            cluster, parameters
        )
        c = readiness_probe_container_constructor(cluster, parameters)

        with DAG(name="d"):
            threedcitydb_start_t = Task(
                name="startthreedcitydb", template=threedcitydb_start_db_c
            )
            t2 = Task(
                name="whalesay",
                template=whalesay_c,
                arguments={"a": threedcitydb_start_t.ip},
            )
            t3 = Task(
                name="shellprobing",
                template=c,
                arguments={"hostaddr": threedcitydb_start_t.ip},
            )
            threedcitydb_start_t >> t2 >> t3
    w.create()
