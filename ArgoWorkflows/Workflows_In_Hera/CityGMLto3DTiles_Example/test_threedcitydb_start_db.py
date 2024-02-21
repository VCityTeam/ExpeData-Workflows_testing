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

    layout_database = layout(inputs.constants).database()

    ### First define the WorkFlowTemplates used below by the main Workflow.
    #
    # LIMIT: trying to define the following WorkFlowTemplate(s) in the context
    # of the Workflow (that is after the
    #     `with Workflow(generate_name="threedcitydb-start-",[...])`
    # declaration) will fail. Hera complains that the @scripts used by the
    # WorkFlowTemplates are undefined (e.g. `template print_script` undefined)
    db_check_template_name = "db-check-template"
    define_db_check_template(
        environment,
        layout_database,
        template_name=db_check_template_name,
    )

    with Workflow(generate_name="threedcitydb-start-", entrypoint="main") as w:
        ### Define containers used by this workflow
        threedcitydb_start_db_c = threedcitydb_start_db_container(
            environment,
            layout_database,
        )

        with DAG(name="main"):
            # LIMITS: because a deamon task cannot be integrated within a
            # WorkflowTemplate (refer to the comments within
            # define_db_check_template()), the following for loop cannot be
            # expressed natively in AW (that is by using "with_param" or
            # "with_item").
            for vintage in inputs.parameters.vintages:
                start_db_t = Task(
                    name="start-db-daemon-" + str(vintage),
                    template=threedcitydb_start_db_c,
                    arguments={
                        "database_name": layout_database.name,
                        "vintage": vintage,
                    },
                )
                threed_city_db_check_t = Task(
                    name="threed-city-db-check-" + str(vintage),
                    template_ref=models.TemplateRef(
                        # LIMITS: the construction of the name has to be aligned
                        # with the name chosen within the definition of the
                        # define_db_check_template() function. Find a better
                        # mechanism since this is error prone (e.g. changing
                        # the definition of define_db_check_template() might
                        # impact the following "calling" call or template
                        # reference).
                        name="workflow-" + db_check_template_name,
                        template=db_check_template_name,
                    ),
                    arguments={
                        "dbhostaddr": start_db_t.ip,
                        "vintage": vintage,
                    },
                )

                print_ip_t = check_is_valid_ip(
                    name="db-check-ip-validity" + str(vintage),
                    arguments=Parameter(
                        name="ip_addr",
                        value=start_db_t.ip,
                        # LIMIT: we wanted to write
                        # value="{{tasks.threed-city-db-check.outputs.parameters.dbip}}",
                        # but we need to decline the tasks names with the vintages
                        # i.e. to write an expression that evaluates to
                        #    value="{{tasks.threed-city-db-check-2012.outputs.parameters.dbip}}
                        # starting from
                        #    value="{{tasks.threed-city-db-check-+str(vintage).outputs.parameters.dbip}}
                        # There is thus a double evaluation of the value string
                        # - a first one at Hera definition stage where the
                        #   vintage for loop is expressed
                        # - a second evaluation at AW runtime stage to retrieve
                        #   the current value out of the expression.
                        # Writing such value string promisses to be painfull...
                    ),
                )
                start_db_t >> threed_city_db_check_t >> print_ip_t

    w.create()
