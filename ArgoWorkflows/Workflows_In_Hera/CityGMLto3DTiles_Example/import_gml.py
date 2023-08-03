import sys, os

sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition")
)
from pagoda_cluster_definition import cluster

from hera_utils import hera_assert_version

hera_assert_version("5.6.0")

####### Cluster independent

if __name__ == "__main__":
    from input_2012_tiny_import_dump import parameters
    from experiment_layout import layout
    from utils import whalesay_container
    from utils import convert_message_to_output_parameter
    from database import (
        threedcitydb_start_db_container,
        import_citygml_file_to_db_container,
        define_db_check_template,
    )

    from hera.workflows import DAG, Task, models, Parameter, Workflow

    define_db_check_template(cluster, parameters)
    with Workflow(generate_name="import-gml-", entrypoint="main") as w:
        threedcitydb_start_db_c = threedcitydb_start_db_container(
            cluster, parameters
        )
        import_gml_c = import_citygml_file_to_db_container(cluster, parameters)
        with DAG(name="main"):
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

            # We must have an a priori knowledge of the experiment file layout
            # in order to point to the input directory (holding the input files)
            strip_gml_output_dir = os.path.join(
                parameters.persistedVolume,
                layout.strip_gml_output_dir(parameters),
            )
            write_output_t: Task = convert_message_to_output_parameter(
                arguments=Parameter(name="message", value=strip_gml_output_dir)
            )
            whalesay_input_dir_t = Task(
                name="whalesayinputdir",
                template=whalesay_container,
                arguments=write_output_t.get_parameter("message").with_name(
                    "message"
                ),
            )
            #### FIXME : the list of files to be imported MUST be a parameter
            # of this next task instead of being passed at container
            # definition !
            import_gml_t = Task(
                name="importgml",
                template=import_gml_c,
                arguments=[
                    Parameter(
                        name="hostaddr",
                        value="{{tasks.threed-city-db-check.outputs.parameters.dbip}}",
                    ),
                    Parameter(
                        name="filenames",
                        value=os.path.join(
                            layout.strip_gml_output_dir(parameters),
                            layout.strip_gml_output_filename(parameters),
                        ),
                    ),
                ],
            )
            (
                start_db_t
                >> threed_city_db_check_t
                >> write_output_t
                >> whalesay_input_dir_t
                >> import_gml_t
            )
    w.create()
