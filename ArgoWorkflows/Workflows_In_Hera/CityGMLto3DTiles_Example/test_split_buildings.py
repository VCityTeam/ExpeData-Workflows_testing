import os, sys

sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition")
)
from hera_utils import hera_assert_version

hera_assert_version("5.6.0")

#################### Cluster independent code
if __name__ == "__main__":
    from split_buildings import split_buildings_container
    from pagoda_environment_definition import environment
    from input_2012_tiny_import_dump import inputs
    from experiment_layout import layout

    layout_instance = layout(inputs)
    vintage = inputs.parameters.vintage
    # borough = inputs.parameters.borough
    # boroughs = inputs.parameters.boroughs

    from utils import print_script, convert_message_to_output_parameter
    from hera.workflows import DAG, Task, Parameter, Workflow

    with Workflow(generate_name="split-buildings-", entrypoint="dag") as w:
        split_buildings_c = split_buildings_container(environment)
        with DAG(name="dag"):
            for borough in inputs.parameters.boroughs:
                split_buildings_t = Task(
                    name="split-buildings" + borough.replace("_", "-"),
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
                # FIXME Somehow we gave up on collecting outputs to plug them
                #       at AW level as inputs for the next task
                #
                #
                # The original `split-buildings` container does not define an output
                # file that holds the name of the resulting file. This makes it hard
                # to transmit that information (the name of the resulting file) to the next
                # taks in the workflow that requires that filename as one of its inputs.
                # In order to circumvent that shortcoming of the `split-buildings` container
                # we add a posttreament that whose single purpose is to write that result
                # file (holding filename(s).
                # This inital limited task is thus complemented with an adhoc post-treament
                # task.
                # output_dir = os.path.join(
                #     environment.persisted_volume.mount_path,
                #     layout_instance.split_buildings_output_dir(
                #         vintage, borough
                #     ),
                # )
                # write_output_t: Task = convert_message_to_output_parameter(
                #     name=SHOULD_BE_DECLINED_BUT_IS_THIS_POSSIBLE_WITH_A_SCRIPT_?????
                #     arguments=Parameter(name="message", value=output_dir)
                # )
                # print_t = print_script(
                #     name="print-results",
                #     arguments=write_output_t.get_parameter("message"),
                # )
                # split_buildings_t >> write_output_t >> print_t
    w.create()
