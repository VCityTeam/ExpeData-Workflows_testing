import os, sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition"))
from hera_utils import hera_assert_version

hera_assert_version("5.6.0")

#################### Cluster independent code
if __name__ == "__main__":
    from hera.workflows import DAG, Task, Parameter, Workflow
    from utils import convert_message_to_output_parameter
    from split_buildings import split_buildings_container

    from pagoda_environment_definition import environment
    from input_2012_tiny_import_dump import inputs
    from experiment_layout import layout

    layout_instance = layout(inputs.constants)

    with Workflow(generate_name="split-buildings-", entrypoint="dag") as w:
        split_buildings_c = split_buildings_container(environment)
        with DAG(name="dag"):
            for vintage in inputs.parameters.vintages:
                for borough in inputs.parameters.boroughs:
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

                    # The original `split-buildings` container does not define an output
                    # file that holds the name of the resulting file. This makes it hard
                    # to transmit that information (the name of the resulting file) to the next
                    # task of the workflow that requires that filename as one of its inputs.
                    # In order to circumvent that shortcoming of the `split-buildings` container
                    # we add a post-treament whose single purpose is to write that result
                    # file (holding filename(s).
                    # This inital limited task is thus complemented with an adhoc post-treament
                    # task.
                    output_dir = os.path.join(
                        environment.persisted_volume.mount_path,
                        layout_instance.split_buildings_output_dir(vintage, borough),
                    )
                    write_output_t: Task = convert_message_to_output_parameter(
                        name="write-output-"
                        + layout_instance.container_name_postend(vintage, borough),
                        arguments=Parameter(name="message", value=output_dir),
                    )
                    split_buildings_t >> write_output_t

                    # FIXME Somehow we gave up on collecting outputs to plug them
                    # at AW level as inputs for the next task because the so-called
                    # fanout-fanin techniques e.g.
                    # https://github.com/argoproj-labs/hera/blob/main/examples/workflows/dynamic_fanout_fanin.py
                    # do NOT work when there is more than a single fanout task.
                    # For example if we add the following lines
                    #     print_t = print_list_script(
                    #         name="print-results",
                    #         arguments=write_output_t.get_parameter("message"),
                    #     )
                    #     write_output_t >> print_t
                    # then (and as expected) Hera would complain about/with
                    #     templates.dag sorting failed:
                    #        duplicated nodeName print-results
    w.create()
