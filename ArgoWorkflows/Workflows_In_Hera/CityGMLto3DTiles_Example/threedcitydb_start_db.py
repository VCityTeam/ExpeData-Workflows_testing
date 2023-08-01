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

from hera_utils import hera_assert_version

hera_assert_version("5.6.0")

#################### Cluster independent code
if __name__ == "__main__":
    from pagoda_cluster_definition import cluster
    from input_2012_tiny_import_dump import parameters
    from database import define_db_start_template, check_is_valid_ip
    from hera.workflows import DAG, models, Parameter, Task, Workflow

    define_db_start_template(cluster, parameters)
    with Workflow(generate_name="threedcitydb-start-", entrypoint="main") as w:
        with DAG(name="main") as s:
            threedcitydb_start_t = Task(
                name="threed-city-db-start",
                template_ref=models.TemplateRef(
                    name="workflow-startdb",
                    template="db-start-template",
                ),
            )
            print_ip_t = check_is_valid_ip(
                name="db-check-ip-validity",
                arguments=Parameter(
                    name="ip_addr",
                    value="{{tasks.threed-city-db-start.outputs.parameters.dbip}}",
                ),
            )
            threedcitydb_start_t >> print_ip_t

    w.create()
