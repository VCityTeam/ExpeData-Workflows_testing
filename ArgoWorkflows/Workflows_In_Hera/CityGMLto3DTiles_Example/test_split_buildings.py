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

                    # LIMIT: with AW, loops must be expressed through dedicated
                    # commands (`with_items` together with `{{item}}`). Hera
                    # offers its AW native counterpart. But when using Hera we
                    # also sometimes (when the loop bound are known at Hera
                    # submission stage) have the freedom to express loops at the
                    # Python level (although the topology/breadth of the loop
                    # will then not be driven at runtime).
                    # When using AW loops language mechanism, AW offers a
                    # technique for so-called fanout-fanin techniques refer to
                    # https://github.com/argoproj-labs/hera/blob/main/examples/workflows/dynamic_fanout_fanin.py
                    # If we chose to express the loop natively in Python, we
                    # must have an equivalent of the fanout-fanin technique.
                    # The question is then: what is this equivalent ?
                    #
                    # In the above design of the present workflow, we chose to
                    # express the for loop in Python. But we (might) still need
                    # to collect the outputs of the tasks that are part of the
                    # loop (for example in order to plug such values into the
                    # next task's input).
                    #
                    # As a first trial, if we add the following lines
                    #     print_t = print_list_script(
                    #         name="print-results",
                    #         arguments=write_output_t.get_parameter("message"),
                    #     )
                    #     write_output_t >> print_t
                    # to the python for loop then (and as expected) Hera would
                    # complain about/with the following message
                    #     templates.dag sorting failed:
                    #        duplicated nodeName print-results
                    #
                    # As a second trial, we might try to decline the name of
                    # the task as e.g. in
                    #     print_t = print_list_script(
                    #         name="print-results"+ str(borough),
                    #         arguments=write_output_t.get_parameter("message"),
                    #     )
                    #     write_output_t >> print_t
                    # which shall work but with the wrong semantics: they are
                    # many print_t tasks that thus cannot be a fanin task
                    # (because they are many fanout tasks for a single fanin
                    # task).
                    #
                    # Eventually the only solutions seems to create a fanin
                    # task whose input is not flown at the AW/Hera level but
                    # that will collect its input out of the outputs files
                    # of the fanout tasks: this fanin task will thus require
                    # the knowledge of where the files describing the result
                    # of a fanout task are located (as well as their structure).
                    # And it will require this knowledge for each of the fanout
                    # task i.e. it will require the knowledge of loop (resulting
                    # files) layout.
    w.create()
