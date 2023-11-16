import os, sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition"))
from hera_utils import hera_assert_version

hera_assert_version("5.6.0")

###
if __name__ == "__main__":
    from hera.workflows import DAG, Task, Parameter, Workflow

    from strip_gml import strip_gml_container
    from utils import print_script, convert_message_to_output_parameter

    from pagoda_environment_definition import environment
    from input_2012_tiny_import_dump import inputs
    from experiment_layout import layout

    layout_instance = layout(inputs.constants)

    with Workflow(generate_name="strip-gml-", entrypoint="dag") as w:
        strip_gml_c = strip_gml_container(environment)
        with DAG(name="dag"):
            for vintage in inputs.parameters.vintages:
                for borough in inputs.parameters.boroughs:
                    strip_gml_t = Task(
                        name="strip-gml-"
                        + layout.container_name_postend(vintage, borough),
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

                    # The original `strip-gml` container does not define an output
                    # file that holds the name of the resulting file. This makes it hard
                    # to transmit that information (the name of the resulting file) to
                    # the next task in the workflow that requires that filename as one
                    # of its inputs.
                    # In order to circumvent that shortcoming of the `strip-gml`
                    # container, we add a post-treament (to `strip-g,;`) whose
                    # single purpose is to write that result file (holding filename(s)).
                    # This inital limited task is thus complemented with an adhoc
                    # post-treament task.
                    output_dir = os.path.join(
                        environment.persisted_volume.mount_path,
                        layout_instance.strip_gml_output_dir(vintage, borough),
                    )
                    write_output_t: Task = convert_message_to_output_parameter(
                        name="write-output-"
                        + layout.container_name_postend(vintage, borough),
                        arguments=Parameter(name="message", value=output_dir),
                    )
                    strip_gml_t >> write_output_t
                    # FIXME CLEAN ME
                    # # print_t = print_script(
                    # #     name="print-results",
                    # #     arguments=write_output_t.get_parameter("message"),
                    # # )
                    # strip_gml_t >> write_output_t  # >> print_t
    w.create()
