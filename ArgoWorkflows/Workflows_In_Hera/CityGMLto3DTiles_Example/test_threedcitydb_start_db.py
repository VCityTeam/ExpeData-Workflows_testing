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
#     python  CityGMLto3DTiles_Example/test_threedcitydb_start_db.py
# Refer to "Accessing results" chapter of the On_PaGoDA_cluster/Readme.md file
# for further details about result exploration.
import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition"))

from hera_utils import hera_assert_version

hera_assert_version("5.6.0")


################ Environment (including cluster) independent code (well almost)
if __name__ == "__main__":
    from hera.workflows import DAG, models, Parameter, Task, Workflow

    from database import check_is_valid_ip, threedcitydb_start_db_container
    from database_aggregated import define_db_check_template

    from pagoda_environment_definition import environment
    from input_2012_tiny_import_dump import inputs
    from experiment_layout import layout

    ### First define the WorkFlowTemplates used below by the main Workflow.
    #
    # LIMIT: trying to define the following WorkFlowTemplate(s) in the context
    # of the Workflow (that is after the
    #     `with Workflow(generate_name="threedcitydb-start-",[...])`
    # declaration) will fail. Hera complains that the @scripts used by the
    # WorkFlowTemplates are undefined (e.g. `template print_script` undefined)
    db_check_template_names = {}
    for vintage in inputs.parameters.vintages:
        db_check_template_name = "db-check-template-" + str(vintage)
        define_db_check_template(
            environment,
            layout.database(vintage),
            vintage,
            template_name=db_check_template_name,
        )
        db_check_template_names[vintage] = db_check_template_name

    with Workflow(generate_name="threedcitydb-start-", entrypoint="main") as w:
        ### Define containers used by this workflow
        # LIMIT: because of a runtime configuration limit of the container
        # (refer to the LIMIT comment within threedcitydb_start_db_container())
        # we have no choice but to define as many containers as they are
        # vintages (parameter) values.
        threedcitydb_containers = {}
        for vintage in inputs.parameters.vintages:
            threedcitydb_start_db_c = threedcitydb_start_db_container(
                environment, inputs.constants, layout.database(vintage)
            )
            threedcitydb_containers[vintage] = threedcitydb_start_db_c

        with DAG(name="main") as s:
            for vintage in inputs.parameters.vintages:
                start_db_t = Task(
                    name="start-db-daemon-" + str(vintage),
                    template=threedcitydb_containers[vintage],
                )
                threed_city_db_check_t = Task(
                    name="threed-city-db-check-" + str(vintage),
                    template_ref=models.TemplateRef(
                        name="workflow-checkdb-" + str(vintage),
                        template=db_check_template_names[vintage],
                    ),
                    arguments={"dbhostaddr": start_db_t.ip},
                )
                ## start_db_t >> threed_city_db_check_t

                print_ip_t = check_is_valid_ip(
                    name="db-check-ip-validity" + str(vintage),
                    arguments=Parameter(
                        name="ip_addr",
                        value=start_db_t.ip
                        # We wanted to write
                        # value="{{tasks.threed-city-db-check.outputs.parameters.dbip}}",
                    ),
                )
                start_db_t >> threed_city_db_check_t >> print_ip_t

    w.create()
