import sys, os

sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition")
)
from hera_utils import hera_assert_version

hera_assert_version("5.6.0")

####
# This script will FAIL (it is not expected to run): refer to the comments
# below for an explanations on the reasons for this failure.
####

if __name__ == "__main__":
    from pagoda_environment_definition import environment
    from input_2012_tiny_import_dump import inputs
    from experiment_layout import layout

    from collect import collect_container_constructor
    from utils import print_list_script, ip_http_check_container
    from hera.workflows import DAG, Task, Workflow

    layout = layout(inputs)
    vintage = 2012
    boroughs = ["LYON_1ER", "LYON_8EME"]
    with Workflow(generate_name="fullcollect-", entrypoint="dag") as w:
        ip_http_check_c = ip_http_check_container(environment)
        collect_c = collect_container_constructor(
            environment,
            inputs.constants,
        )
        with DAG(name="dag"):
            check_ip_connectivity_t = Task(
                name="iphttpcheck", template=ip_http_check_c
            )
            collect_loop_t = Task(
                name="collect",
                template=collect_c,
                arguments={
                    "vintage": vintage,
                    "borough": "{{item}}",
                    # We here would like to locate the expression of the
                    # resulting directory, that depends on the borough looping
                    # parameter, at the python level. Not only python is our
                    # priviledged language for such an expression (thanks to
                    # Hera) but we also need to reuse such an expression. If
                    # we were to express such a derived name (refer to the
                    # layout.collect_output_dir() function definition) at the
                    # Hera/AW level then we would need to repeat such a
                    # (experiment level) design choice.
                    # We thus would like to write something of the form of the
                    # next line that defines "results_dir". This would of
                    # course fail because the python interpretation stage
                    # precedes the AW interpretation stage (don't forget Hera
                    # generaters yaml files for you).
                    # This strategy is thus a dead end.
                    "results_dir": layout.collect_output_dir(
                        vintage, "{{item}}"
                    ),
                },
                with_items=boroughs,
            )
            print_t = print_list_script(
                name="print-results",
                arguments=collect_loop_t.get_parameter("msg").with_name(
                    "messages"
                ),
            )
            check_ip_connectivity_t >> collect_loop_t >> print_t
    w.create()
