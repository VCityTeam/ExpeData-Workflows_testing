import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition"))

from hera_utils import hera_assert_version, hera_clear_workflow_template

hera_assert_version("5.6.0")

###############
# LIMIT notes:
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
from utils import convert_message_to_output_parameter
from database import (
    check_is_valid_ip,
    db_isready_container,
    db_probe_catalog_container,
    import_citygml_file_to_db_container,
)


def define_db_check_template(environment, database, vintage, template_name):
    # LIMIT: refer above to note [1]
    workflow_template_name = "workflow-checkdb-" + str(vintage)
    with WorkflowTemplate(
        name=workflow_template_name,
        entrypoint=template_name,
    ) as w:
        # FIXME FIXME A présent que le conteneurs suivants sont indépendants
        # de vintage (lors de leur définition mais plus lors de leur usage)
        # peut-on les définir à l'extérieur de cette fonction (par exemple
        # au niveau du fichier ou même dans database.py) et donc une bonne
        # fois pour toutes ? Car si tel était le cas alors cela éviterait de
        # devoir utiliser get_new_container_identifier() dans database.py...
        db_isready_c = db_isready_container(environment, database)
        db_probe_c = db_probe_catalog_container(environment, database)
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
                arguments={
                    "hostaddr": "{{inputs.parameters.dbhostaddr}}",
                    "database_name": database.name + str(vintage),
                },
            )
            t3 = Task(
                name="db-catalog-probing",
                template=db_probe_c,
                arguments={
                    "hostaddr": "{{inputs.parameters.dbhostaddr}}",
                    "database_name": database.name + str(vintage),
                },
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


def define_import_boroughs_to_3dcitydb_template(
    environment, layout_instance, vintage, boroughS, template_name
):
    """For the considered vintage, and the associated database, import all
    the (many) argument designated boroughS (thus the capital S that underlines
    the multiplicty of buroughs)

    Args:
        environment (_type_): the experimental environment (cluster, partitions)
        database (_type_): elements for database access

    Dynamic Args (given at AW runtime)
        vintage (_type_): the considered and unique vintage
        boroughs (_type_): the set of boroughs that must be imported
    """
    # Notes:
    # - LIMIT: refer above to note [1]
    # - LIMIT: we need to apply the note [2]. In the case of this workflow, we
    #   flow the ip address
    # - EXPERIMENT DESIGN: refer to "EXPERIMENT_DESIGN.md" for the priming
    #   vintage over boroughs in the databases and its "functional" integration
    #   approach/consquence ending in the creation of this WorkflowTemplate.

    ### First define the WorkFlowTemplates used below by the main Workflow.
    #
    # LIMIT: trying to define the following WorkFlowTemplate(s) in the context
    # of the Workflow (that is after the
    #     `with Workflow(generate_name="threedcitydb-start-",[...])`
    # declaration) will fail. Hera complains that the @scripts used by the
    # WorkFlowTemplates are undefined (e.g. `template print_script undefined`).

    database = layout_instance.database(vintage)
    db_check_template_name = "db-check-template-" + str(vintage)
    define_db_check_template(
        environment,
        database,
        vintage,
        template_name=db_check_template_name,
    )

    workflow_template_name = "workflow-import-" + str(vintage)
    with WorkflowTemplate(
        name=workflow_template_name,
        entrypoint=template_name,
    ) as w:
        import_citygml_file_to_db_c = import_citygml_file_to_db_container(
            environment, database
        )
        with DAG(
            name=template_name,
            inputs=[Parameter(name="dbhostaddr")],
        ):
            #### Preconditions:
            # Check the database is up and available.
            threed_city_db_check_t = Task(
                name="threed-city-db-check-" + str(vintage),
                template_ref=models.TemplateRef(
                    name="workflow-checkdb-" + str(vintage),
                    template=db_check_template_name,
                ),
                arguments={"dbhostaddr": "{{inputs.parameters.dbhostaddr}}"},
            )

            for borough in boroughS:
                input_dir = os.path.join(
                    environment.persisted_volume.mount_path,
                    layout_instance.strip_gml_output_dir(vintage, borough),
                )

                input_filename = layout_instance.strip_gml_output_filename(
                    vintage, borough
                )

                # FIXME: call the importation method with a real list of
                # filenameS as opposed to this single filename
                filenames_to_import = os.path.join(input_dir, input_filename)

                import_t = Task(
                    name="import-citygml-files-to-db"
                    + layout_instance.container_name_postend(vintage, borough),
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

                threed_city_db_check_t >> import_t

    hera_clear_workflow_template(environment, workflow_template_name)
    w.create()
