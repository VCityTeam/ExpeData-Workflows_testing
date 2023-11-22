import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition"))

from hera_utils import hera_assert_version

hera_assert_version("5.6.0")


#################### Cluster independent code
if __name__ == "__main__":
    from hera.workflows import DAG, models, Parameter, Task, Workflow
    from compute_tileset import (
        generate_compute_tileset_configuration_file,
        compute_tileset_container,
    )
    from database_aggregated import define_db_check_template
    from database import threedcitydb_start_db_container

    from pagoda_environment_definition import environment
    from input_2012_tiny_import_dump import inputs
    from experiment_layout import layout

    layout_instance = layout(inputs.constants)
    db_check_template_names = {}
    for vintage in inputs.parameters.vintages:
        db_check_template_name = "db-check-template-" + str(vintage)
        define_db_check_template(
            environment,
            layout(inputs.constants).database(vintage),
            vintage,
            template_name=db_check_template_name,
        )
        db_check_template_names[vintage] = db_check_template_name

    with Workflow(generate_name="compute-tileset-", entrypoint="main") as w:
        threedcitydb_containers = {}
        for vintage in inputs.parameters.vintages:
            threedcitydb_start_db_c = threedcitydb_start_db_container(
                environment,
                layout_instance.database(vintage),
            )
            threedcitydb_containers[vintage] = threedcitydb_start_db_c

        compute_tileset_containers = {}
        for vintage in inputs.parameters.vintages:
            compute_tileset_c = compute_tileset_container(
                environment,
                layout_instance.compute_tileset_output_dir(vintage),
                layout_instance.compute_tileset_configuration_filename(vintage),
                "compute-tileset-" + str(vintage),
            )
            compute_tileset_containers[vintage] = compute_tileset_c

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
                start_db_t >> threed_city_db_check_t

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

                start_db_t >> generate_configuration_t

                compute_tileset_t = Task(
                    name="compute-tileset-" + str(vintage),
                    template=compute_tileset_containers[vintage],
                )

                threed_city_db_check_t >> compute_tileset_t
                generate_configuration_t >> compute_tileset_t
    w.create()
