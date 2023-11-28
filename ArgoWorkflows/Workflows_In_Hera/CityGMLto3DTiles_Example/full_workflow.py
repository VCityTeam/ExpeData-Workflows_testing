import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition"))
from hera_utils import hera_assert_version

hera_assert_version("5.6.0")


if __name__ == "__main__":
    from hera.workflows import DAG, models, Parameter, Task, Workflow
    from collect import collect_container_constructor
    from strip_gml import strip_gml_container
    from split_buildings import split_buildings_container
    from database import (
        threedcitydb_start_db_container,
        import_citygml_file_to_db_container,
    )
    from database_aggregated import define_db_check_template
    from compute_tileset import (
        generate_compute_tileset_configuration_file,
        compute_tileset_container,
    )
    from utils import (
        convert_message_to_output_parameter,
        print_script,
        ip_http_check_container,
    )

    from pagoda_environment_definition import environment
    from input_2012_tiny_import_dump import inputs
    from experiment_layout import layout

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

    with Workflow(generate_name="full-workflow-", entrypoint="dag") as w:
        ### Container defintions
        ip_http_check_c = ip_http_check_container(environment)
        collect_c = collect_container_constructor(
            environment,
            inputs.constants,
        )
        strip_gml_c = strip_gml_container(environment)
        split_buildings_c = split_buildings_container(environment)

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

        compute_tileset_containers = {}
        for vintage in inputs.parameters.vintages:
            compute_tileset_c = compute_tileset_container(
                environment,
                layout_instance.compute_tileset_output_dir(vintage),
                layout_instance.compute_tileset_configuration_filename(vintage),
                "compute-tileset-" + str(vintage),
            )
            compute_tileset_containers[vintage] = compute_tileset_c

        ### DAG (and workflow definition) starts here:
        with DAG(name="dag"):
            check_ip_connectivity_t = Task(name="iphttpcheck", template=ip_http_check_c)
            state_one_end_t = print_script(
                name="stage-one-end",
                arguments={"message": "End of collecting stage (1)."},
            )
            stage_four_end_t = print_script(
                name="stage-four-end",
                arguments={"message": "End of importation stage (4)."},
            )
            workflow_end_t = print_script(
                name="workflow-end",
                arguments={"message": "End of workflow."},
            )

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
                    #### Stage 1: collect
                    results_dir = os.path.join(
                        environment.persisted_volume.mount_path,
                        layout_instance.collect_output_dir(vintage, borough),
                    )
                    collect_t = Task(
                        name="collect-"
                        + layout_instance.container_name_postend(vintage, borough),
                        template=collect_c,
                        arguments={
                            "vintage": vintage,
                            "borough": borough,
                            "results_dir": results_dir,
                        },
                    )
                    check_ip_connectivity_t >> collect_t >> state_one_end_t

                    #### Stage 2: split
                    split_buildings_t = Task(
                        name="split-buildings"
                        + layout_instance.container_name_postend(vintage, borough),
                        template=split_buildings_c,
                        arguments={
                            "input_filename": os.path.join(
                                environment.persisted_volume.mount_path,
                                layout_instance.split_buildings_input_filename(
                                    vintage, borough
                                ),
                            ),
                            "output_dir": os.path.join(
                                environment.persisted_volume.mount_path,
                                layout_instance.split_buildings_output_dir(
                                    vintage, borough
                                ),
                            ),
                            "output_filename": layout_instance.split_buildings_output_filename(
                                vintage, borough
                            ),
                        },
                    )
                    output_dir = os.path.join(
                        environment.persisted_volume.mount_path,
                        layout_instance.split_buildings_output_dir(vintage, borough),
                    )
                    write_split_output_t: Task = convert_message_to_output_parameter(
                        name="write-split-output-"
                        + layout_instance.container_name_postend(vintage, borough),
                        arguments=Parameter(name="message", value=output_dir),
                    )
                    state_one_end_t >> split_buildings_t >> write_split_output_t

                    #### Stage 3: strip
                    strip_gml_t = Task(
                        name="strip-gml-"
                        + layout_instance.container_name_postend(vintage, borough),
                        template=strip_gml_c,
                        arguments={
                            "input_filename": os.path.join(
                                environment.persisted_volume.mount_path,
                                layout_instance.split_buildings_output_dir(
                                    vintage, borough
                                ),
                                layout_instance.split_buildings_output_filename(
                                    vintage, borough
                                ),
                            ),
                            "output_dir": os.path.join(
                                environment.persisted_volume.mount_path,
                                layout_instance.strip_gml_output_dir(vintage, borough),
                            ),
                            "output_filename": layout_instance.strip_gml_output_filename(
                                vintage, borough
                            ),
                        },
                    )
                    output_dir = os.path.join(
                        environment.persisted_volume.mount_path,
                        layout_instance.strip_gml_output_dir(vintage, borough),
                    )
                    write_strip_output_t: Task = convert_message_to_output_parameter(
                        name="write-strip-output-"
                        + layout_instance.container_name_postend(vintage, borough),
                        arguments=Parameter(name="message", value=output_dir),
                    )
                    write_split_output_t >> strip_gml_t >> write_strip_output_t

                    # Stage 4: import
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

                    threed_city_db_check_t >> import_vintage_borough_t
                    write_strip_output_t >> import_vintage_borough_t
                    import_vintage_borough_t >> stage_four_end_t

                #### Stage 5: compute tileset
                database = layout_instance.database(vintage)
                generate_configuration_t = generate_compute_tileset_configuration_file(
                    name="generate-tileset-configuration" + str(vintage),
                    arguments={
                        "claim_name": environment.persisted_volume.claim_name,
                        "mount_path": environment.persisted_volume.mount_path,
                        "vintage": vintage,
                        "database_name": database.name,
                        "database_hostname": start_db_t.ip,
                        "database_password": database.password,
                        "database_user": database.user,
                        "database_port": database.port,
                        "target_directory": os.path.join(
                            environment.persisted_volume.mount_path,
                            layout_instance.compute_tileset_output_dir(vintage),
                        ),
                    },
                )
                stage_four_end_t >> generate_configuration_t

                compute_tileset_t = Task(
                    name="compute-tileset-" + str(vintage),
                    template=compute_tileset_containers[vintage],
                )
                generate_configuration_t >> compute_tileset_t
                compute_tileset_t >> workflow_end_t

    w.create()
