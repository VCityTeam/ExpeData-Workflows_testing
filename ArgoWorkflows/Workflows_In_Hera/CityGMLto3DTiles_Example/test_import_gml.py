import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition"))

from hera_utils import hera_assert_version

hera_assert_version("5.6.0")

################ Environment (including cluster) independent code (well almost)
if __name__ == "__main__":
    from hera.workflows import DAG, Task, models, Parameter, Workflow

    from database import (
        threedcitydb_start_db_container,
        import_citygml_file_to_db_container,
    )
    from database_aggregated import define_db_check_template

    from pagoda_environment_definition import environment
    from input_2012_tiny_import_dump import inputs
    from experiment_layout import layout

    # EXPERIMENT DESIGN NOTE: refer to "EXPERIMENT_DESIGN.md" for priming
    # vintage over boroughs in the databases.

    layout_instance = layout(inputs.constants)
    db_check_template_names = {}
    for vintage in inputs.parameters.vintages:
        db_check_template_name = "db-check-template-" + str(vintage)
        define_db_check_template(
            environment,
            layout_instance.database(vintage),
            vintage,
            template_name=db_check_template_name,
        )
        db_check_template_names[vintage] = db_check_template_name

    with Workflow(generate_name="import-gml-", entrypoint="main") as w:
        threedcitydb_containers = {}
        for vintage in inputs.parameters.vintages:
            threedcitydb_start_db_c = threedcitydb_start_db_container(
                environment,
                layout_instance.database(vintage),
            )
            threedcitydb_containers[vintage] = threedcitydb_start_db_c

        import_containers = {}
        for vintage in inputs.parameters.vintages:
            import_citygml_file_to_db_c = import_citygml_file_to_db_container(
                environment, layout_instance.database(vintage)
            )
            import_containers[vintage] = import_citygml_file_to_db_c

        with DAG(name="main"):
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
                start_db_t >> threed_city_db_check_t

                for borough in inputs.parameters.boroughs:
                    import_vintage_borough_t = Task(
                        name="import-citygml-files-to-db"
                        + layout_instance.container_name_postend(vintage, borough),
                        template=import_containers[vintage],
                        arguments=[
                            Parameter(
                                name="database_ip_address",
                                value=start_db_t.ip,
                            ),
                            Parameter(
                                name="filenames",
                                value=os.path.join(
                                    environment.persisted_volume.mount_path,
                                    layout_instance.strip_gml_output_dir(
                                        vintage, borough
                                    ),
                                    layout_instance.strip_gml_output_filename(
                                        vintage, borough
                                    ),
                                ),
                            ),
                        ],
                    )

                    # We need to flow the IP dynamic parameter
                    start_db_t >> import_vintage_borough_t
                    # Database assertion must be effective prior importing.
                    # The following line is thus NOT for some parameter flow
                    # but only to imposer some ordering to be respected.
                    threed_city_db_check_t >> import_vintage_borough_t
    w.create()
