import sys, os

sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition")
)

from hera_utils import hera_assert_version

hera_assert_version("5.6.0")

####### Cluster independent

if __name__ == "__main__":
    from pagoda_environment_definition import environment
    from input_2012_tiny_import_dump import inputs
    from experiment_layout import layout

    from utils import whalesay_container
    from database import threedcitydb_start_db_container

    from database_aggregated import (
        define_db_check_template,
        define_import_bouroughs_to_3dcitydb_template,
    )

    from hera.workflows import DAG, Task, models, Parameter, Workflow

    vintage = inputs.parameters.vintage
    boroughs = inputs.parameters.boroughs
    # FIXME should be database(vintage)
    database = inputs.database_2012
    layout_instance = layout(inputs)

    define_db_check_template(environment, database)
    define_import_bouroughs_to_3dcitydb_template(
        environment, database, layout_instance, vintage, boroughs
    )
    with Workflow(generate_name="import-gml-", entrypoint="main") as w:
        threedcitydb_start_db_c = threedcitydb_start_db_container(
            environment, inputs.constants, database
        )
        with DAG(name="main"):
            start_db_t = Task(
                name="start-db-daemon", template=threedcitydb_start_db_c
            )

            threed_city_db_check_t = Task(
                name="threed-city-db-check",
                template_ref=models.TemplateRef(
                    name="workflow-import-boroughs",
                    template="import-boroughs-template",
                ),
                arguments={"dbhostaddr": start_db_t.ip},
            )

            whalesay_input_dir_t = Task(
                name="whalesayinputdir",
                template=whalesay_container,
                arguments={"message": "Importing vintage " + vintage},
            )

            start_db_t >> threed_city_db_check_t >> whalesay_input_dir_t
    w.create()
