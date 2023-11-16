import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition"))

from hera_utils import hera_assert_version, hera_clear_workflow_template

hera_assert_version("5.6.0")

###############
# Notes:
# 1/ non inclusion of db starter:
#    Some db related WorkflowTemplates might need to express the creation of a
#    db server. Alas we cannot integrate the starting of the database within
#    such a this workflow because, as stated in the ArgoWorkflows documentation
#    (refer to
#     https://argoproj.github.io/argo-workflows/walk-through/daemon-containers/)
#     the (started) daemons will be automatically destroyed when the
#     WorkflowTemplate exits the template scope in which the daemon was invoked.
#     This is why WorkflowTemplates never start services (daemon pods) that
#     should outlive their template scope.
# 2/ parameters of WorkflowTemplates should be flown at AW level
#    Refer to the lessons learned (modeling guidelines) corresponding chapter.
###
import os
from hera.workflows import (
    DAG,
    models,
    Parameter,
    Task,
    WorkflowTemplate,
)
from hera.expr import g as expr
from utils import convert_message_to_output_parameter, print_script
from database import (
    check_is_valid_ip,
    db_isready_container,
    db_probe_catalog_container,
    import_citygml_file_to_db_container,
)


def define_db_check_template(environment, database, vintage, template_name):
    # Note: refer above to note [1]
    workflow_template_name = "workflow-checkdb-" + str(vintage)
    with WorkflowTemplate(
        name=workflow_template_name,
        entrypoint=template_name,
    ) as w:
        db_isready_c = db_isready_container(
            environment, database, "shellprobing" + str(vintage)
        )
        db_probe_c = db_probe_catalog_container(
            environment, database, "catalogprobing" + str(vintage)
        )
        with DAG(name=template_name, inputs=[Parameter(name="dbhostaddr")]) as main_dag:
            # When the database fails to start properly, sometimes the ip number
            # returned by the AW engine is the original/uninterpreted expression
            # of the form "{{tasks.<TASKNAME>.ip}}" as opposed to a valid ip
            # number. We thus first check that the AW engine did its job.
            t1: Task = check_is_valid_ip(
                name="check-db-ip-is-valid",
                arguments={"ip_addr": "{{inputs.parameters.dbhostaddr}}"},
            )
            t2 = Task(
                name="db-shell-probing",
                template=db_isready_c,
                arguments=[
                    Parameter(
                        name="hostaddr",
                        value="{{inputs.parameters.dbhostaddr}}",
                    )
                ],
            )
            t3 = Task(
                name="db-catalog-probing",
                template=db_probe_c,
                arguments=[
                    Parameter(
                        name="hostaddr",
                        value="{{inputs.parameters.dbhostaddr}}",
                    )
                ],
            )
            # At this stage we can consider the db ip is valid (because behind
            # that IP the DB was proprely initialized/loaded and answering
            # requests). We thus repeat it to the output (although it was
            # handled over as input) in order for the caller to have the
            # notational convenience to hook his workflow downstream from this
            # check as opposed to directly downstream from the db starting
            # (which could be corrupted/ill-initialized/brain-damaged)
            t4: Task = convert_message_to_output_parameter(
                name="repeat-validated-ip",
                arguments=Parameter(
                    name="message", value="{{inputs.parameters.dbhostaddr}}"
                ),
            )
            t1 >> t2 >> t3 >> t4
            # Template output(s) forwarding:
            expression = expr.tasks["repeat-validated-ip"].outputs.parameters.message
            main_dag.outputs = [
                Parameter(name="dbip", value_from={"expression": str(expression)})
            ]
    hera_clear_workflow_template(environment, workflow_template_name)
    w.create()


def define_import_bouroughs_to_3dcitydb_template(
    environment, database, layout, vintage, boroughs
):
    # FIXME FIXME NOT FUNCTIONNAL YET
    """For the considered vintage, and the associated database, import all
    the (many) argument designated boroughs

    Args:
        environment (_type_): the experimental environment (cluster, partitions)
        database (_type_): elements for database access

    Dynamic Args (given at AW runtime)
        vintage (_type_): the considered and unique vintage
        boroughs (_type_): the set of boroughs that must be imported
    """
    # Note:
    # - refer above to note [1]
    # - we need to apply the note [2]. In the case of this workflow, we flow
    #   the ip address
    with WorkflowTemplate(
        name="workflow-import-boroughs",
        entrypoint="import-boroughs-template",
    ) as w:
        import_citygml_file_to_db_c = import_citygml_file_to_db_container(
            environment, database
        )
        with DAG(
            name="import-boroughs-template",
            inputs=[Parameter(name="dbhostaddr")],
        ) as main_dag:
            #### Preconditions:
            # Check the database is up and available.
            threed_city_db_check_t = Task(
                name="threed-city-db-check"
                + layout.container_name_postend(vintage, boroughs),
                template_ref=models.TemplateRef(
                    name="workflow-checkdb",
                    template="db-check-template",
                ),
                arguments={"dbhostaddr": "{{inputs.parameters.dbhostaddr}}"},
            )
            #### Proceed with importation per se
            dummy_fanin_t = print_script(
                name="print-results",
                arguments={"message": "End of importation stage."},
            )

            for borough in boroughs:
                input_dir = (
                    os.path.join(
                        environment.persisted_volume.mount_path,
                        layout.strip_gml_output_dir(vintage, borough),
                    ),
                )
                input_filename = (layout.strip_gml_output_filename(vintage, borough),)
                filenames_to_import = os.path.join(input_dir, input_filename)

                import_t = Task(
                    name="import-citygml-files-to-db" + str(vintage) + str(borough),
                    template=import_citygml_file_to_db_c,
                    arguments=[
                        Parameter(
                            name="database_ip_address",
                            value="{{inputs.parameters.dbhostaddr}}",
                        ),
                        Parameter(
                            name="filenames",
                            value=filenames_to_import,
                        ),
                    ],
                )

            threed_city_db_check_t >> import_t >> dummy_fanin_t

    hera_clear_workflow_template(environment, "workflow-import-boroughs")
    w.create()
