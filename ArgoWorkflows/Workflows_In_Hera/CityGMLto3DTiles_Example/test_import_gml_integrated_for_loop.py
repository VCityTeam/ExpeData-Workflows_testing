import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition"))

from hera_utils import hera_assert_version

hera_assert_version("5.6.0")

################ Environment (including cluster) independent code (well almost)
if __name__ == "__main__":
    from hera.workflows import DAG, Task, models, Parameter, Workflow

    from utils import whalesay_container
    from database import threedcitydb_start_db_container
    from database_aggregated import define_import_boroughs_to_3dcitydb_template

    from pagoda_environment_definition import environment
    from input_2012_tiny_import_dump import inputs
    from experiment_layout import layout

    ##### EXPERIMENT DESIGN NOTE: refer to "EXPERIMENT_DESIGN.md" for priming
    # vintage over boroughs in the databases.

    layout_instance = layout(inputs.constants)
    db_import_boroughs_template_names = {}
    for vintage in inputs.parameters.vintages:
        db_import_boroughs_template_name = "db-import-boroughs-template-" + str(vintage)
        define_import_boroughs_to_3dcitydb_template(
            environment,
            layout_instance,
            vintage,
            inputs.parameters.boroughs,
            db_import_boroughs_template_name,
        )
        db_import_boroughs_template_names[vintage] = db_import_boroughs_template_name

    with Workflow(generate_name="import-gml-", entrypoint="main") as w:
        threedcitydb_containers = {}
        for vintage in inputs.parameters.vintages:
            threedcitydb_start_db_c = threedcitydb_start_db_container(
                environment,
                inputs.constants,
                layout(inputs.constants).database(vintage),
            )
            threedcitydb_containers[vintage] = threedcitydb_start_db_c

        with DAG(name="main"):
            for vintage in inputs.parameters.vintages:
                start_db_t = Task(
                    name="start-db-daemon-" + str(vintage),
                    template=threedcitydb_containers[vintage],
                )

                # DESIGN NOTES: refer above on why vintage loop comes before
                # the borough loop and why that borough loop gets integrated
                # (and hidden away) into the following WorkflowTemplate

                import_vintage_boroughs_t = Task(
                    name="import-" + str(vintage) + "-boroughs",
                    template_ref=models.TemplateRef(
                        name="workflow-import-" + str(vintage),
                        template=db_import_boroughs_template_names[vintage],
                    ),
                    arguments={"dbhostaddr": start_db_t.ip},
                )

                whalesay_input_dir_t = Task(
                    name="whalesayinputdir" + str(vintage) + "-boroughs",
                    template=whalesay_container,
                    arguments={
                        "message": "Imported vintage "
                        + str(vintage)
                        + " ".join(inputs.parameters.boroughs)
                    },
                )

                start_db_t >> import_vintage_boroughs_t >> whalesay_input_dir_t
    w.create()
