import sys, os

sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition")
)

from hera_utils import hera_assert_version

hera_assert_version("5.6.0")

from pagoda_cluster_definition import environment


#################### Cluster independent code
if __name__ == "__main__":
    from input_2012_tiny_import_dump import parameters
    from atomic_steps import generate_compute_tileset_configuration_file
    from database import (
        define_db_check_template,
        threedcitydb_start_db_container,
    )

    from hera.workflows import DAG, models, Parameter, Task, Workflow

    define_db_check_template(environment.cluster, parameters)
    with Workflow(
        generate_name="write-configuration-file-", entrypoint="main"
    ) as w:
        threedcitydb_start_db_c = threedcitydb_start_db_container(
            environment.cluster, parameters
        )
        with DAG(name="main") as s:
            start_db_t = Task(
                name="start-db-daemon", template=threedcitydb_start_db_c
            )
            threed_city_db_check_t = Task(
                name="threed-city-db-check",
                template_ref=models.TemplateRef(
                    name="workflow-checkdb",
                    template="db-check-template",
                ),
                arguments={"dbhostaddr": start_db_t.ip},
            )
            generate_configuration_t = generate_compute_tileset_configuration_file(
                name="bozo",
                arguments=[
                    Parameter(name="vintage", value=parameters.vintage),
                    Parameter(
                        name="database_name",
                        value=parameters.database.name,
                    ),
                    Parameter(
                        name="hostname",
                        value="{{tasks.threed-city-db-check.outputs.parameters.dbip}}",
                    ),
                    Parameter(
                        name="password", value=parameters.database.password
                    ),
                    Parameter(name="user", value=parameters.database.user),
                    Parameter(name="port", value=parameters.database.port),
                    Parameter(
                        name="target_directory",
                        value=parameters.experiment_output_dir,
                    ),
                ],
            )

            start_db_t >> threed_city_db_check_t >> generate_configuration_t

    w.create()
