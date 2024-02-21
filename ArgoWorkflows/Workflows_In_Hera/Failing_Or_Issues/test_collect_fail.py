import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition"))
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
            # The following line (defining results_dir in function of vintage
            # and boroughts parameters) makes no sense: this is because we here
            # need to loop on the boroughs values.
            # In order to fix this issue, we cannot declare as many containers
            # as they are values of boroughs. The reason this is that such a
            # choice (defining many containters) goes against the notational
            # syntax of the AW loops (refer below to the with_items argument
            # of the collect_loop_t tasks.)
            #
            # Thus a second approach
            # 1. needs to pass the results_dir as an "inputs" parameter (that is
            #    at AW level) just as the vintage and borough parameters are
            #    passed in the "arguments" parameter of the collect_loop_t Task,
            #    (refer below to the collect_loop_t declaration).
            # 2. also requires that the collect_container_constructor() code
            #    to be modified accordingly (that is to accept a third
            #    results_dir inputs parameter).
            # Eventually this was the solution used in order to realize the
            # current version of test_collect.py
            results_dir=layout.collect_output_dir(vintage, boroughs),
        )
        with DAG(name="dag"):
            check_ip_connectivity_t = Task(name="iphttpcheck", template=ip_http_check_c)
            collect_loop_t = Task(
                name="collect",
                template=collect_c,
                arguments={"vintage": vintage, "borough": "{{item}}"},
                with_items=boroughs,
            )
            print_t = print_list_script(
                name="print-results",
                arguments=collect_loop_t.get_parameter("msg").with_name("messages"),
            )
            check_ip_connectivity_t >> collect_loop_t >> print_t
    w.create()
