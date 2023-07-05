import os
from hera.workflows import Container, ExistingVolume, models


if __name__ == "__main__":
    import sys, os

    sys.path.append(
        os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition")
    )
    from pagoda_cluster_definition import define_cluster
    from utils import whalesay_container, convert_message_to_output_parameter
    from hera_utils import hera_assert_version

    hera_assert_version("5.1.3")

    from input_2012_tiny_import_dump import parameters
    from experiment_layout import layout
    from database import (
        threedcitydb_start_db_container,
        db_isready_container,
        db_probe_catalog_container,
        import_citygml_file_to_db_container,
    )
    from hera.workflows import DAG, Task, Parameter, Workflow

    cluster = define_cluster()
    with Workflow(generate_name="import-gml-", entrypoint="dag") as w:
        # IMPROVE: in the following code, all what concerns the launching of
        # the 3DCityDB is a copy of 3dcirtydb_start_db.py code. We hence
        # don't respect the DRY principle... FIXME
        threedcitydb_start_db_c = threedcitydb_start_db_container(
            cluster, parameters
        )
        whalesay_c = whalesay_container()
        db_isready_c = db_isready_container(
            cluster, parameters, "shellprobing"
        )
        db_probe_c = db_probe_catalog_container(
            cluster, parameters, "catalogprobing"
        )
        # Above was the 3DCityDB related containers. Below is the rest of the
        # pipeline that consummes the 3DCityDB
        import_gml_c = import_citygml_file_to_db_container(
            cluster,
            parameters,
            input_filename=os.path.join(
                layout.strip_gml_output_dir(parameters),
                layout.strip_gml_output_filename(parameters),
            ),
        )

        with DAG(name="dag"):
            # IMPROVE: in the following code, all what concerns the launching of
            # the 3DCityDB is a copy of 3dcirtydb_start_db.py code. We hence
            # don't respect the DRY principle... FIXME
            threedcitydb_start_t = Task(
                name="startthreedcitydb", template=threedcitydb_start_db_c
            )
            whalesay_hostaddr_t = Task(
                name="whalesayhostaddr",
                template=whalesay_c,
                arguments={"a": threedcitydb_start_t.ip},
            )
            db_isready_t = Task(
                name="shellprobing",
                template=db_isready_c,
                arguments={"hostaddr": threedcitydb_start_t.ip},
            )
            db_probe_t = Task(
                name="catalogprobing",
                template=db_probe_c,
                arguments={"hostaddr": threedcitydb_start_t.ip},
            )
            (
                threedcitydb_start_t
                >> whalesay_hostaddr_t
                >> db_isready_t
                >> db_probe_t
            )
            # IMPROVE follow-up: above was the 3DCityDB related containers.
            # Below is the rest of the pipeline that consummes the 3DCityDB.
            #
            # We must have an a priori knowledge of the experiment file layout
            # in order to point to the input directory (holding the input files)
            strip_gml_output_dir = os.path.join(
                parameters.persistedVolume,
                layout.split_buildings_output_dir(parameters),
            )
            write_output_t: Task = convert_message_to_output_parameter(
                arguments=Parameter(name="message", value=strip_gml_output_dir)
            )
            whalesay_input_dir_t = Task(
                name="whalesayinputdir",
                template=whalesay_c,
                arguments=write_output_t.get_parameter("a").with_name("a"),
            )
            #### FIXME : the list of files to be imported MUST be a parameter
            # of this next task instead of being passed at container
            # definition !
            import_gml_t = Task(
                name="importgml",
                template=import_gml_c,
                arguments={"hostaddr": threedcitydb_start_t.ip},
            )
            (
                db_probe_t
                >> write_output_t
                >> whalesay_input_dir_t
                >> import_gml_t
            )
    w.create()
