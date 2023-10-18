import sys, os

sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition")
)
from hera_utils import hera_assert_version

hera_assert_version("5.6.0")

####

if __name__ == "__main__":
    from pagoda_environment_definition import environment
    from input_2012_tiny_import_dump import inputs
    from experiment_layout import layout

    from collect import collect_container_constructor
    from utils import print_script, ip_http_check_container
    from hera.workflows import DAG, Task, Workflow

    layout = layout(inputs)
    vintage = inputs.parameters.vintages
    borough = inputs.parameters.boroughs
    with Workflow(generate_name="fullcollect-", entrypoint="dag") as w:
        ip_http_check_c = ip_http_check_container(environment)
        collect_c = collect_container_constructor(
            environment,
            inputs,
            results_dir=layout.collect_output_dir(vintage, borough),
        )
        with DAG(name="dag"):
            check_ip_connectivity_t = Task(
                name="iphttpcheck", template=ip_http_check_c
            )
            collect_t = Task(name="collect", template=collect_c)
            print_t = print_script(
                name="print-results",
                arguments=collect_t.get_parameter("msg").with_name("message"),
            )
            check_ip_connectivity_t >> collect_t >> print_t
    w.create()
