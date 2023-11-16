import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition"))
from hera_utils import hera_assert_version

hera_assert_version("5.6.0")

####
# Looping design notes: refer to the trial versions in
#
####

if __name__ == "__main__":
    from hera.workflows import DAG, Task, Workflow
    from collect import collect_container_constructor
    from utils import print_script, ip_http_check_container

    from pagoda_environment_definition import environment
    from input_2012_tiny_import_dump import inputs
    from experiment_layout import layout

    layout_instance = layout(inputs.constants)

    with Workflow(generate_name="collect-vintages-boroughs-", entrypoint="dag") as w:
        ip_http_check_c = ip_http_check_container(environment)
        collect_c = collect_container_constructor(
            environment,
            inputs.constants,
        )
        with DAG(name="dag"):
            check_ip_connectivity_t = Task(name="iphttpcheck", template=ip_http_check_c)
            dummy_fanin_t = print_script(
                name="print-results",
                arguments={"message": "End of collecting stage."},
            )

            for vintage in inputs.parameters.vintages:
                for borough in inputs.parameters.boroughs:
                    results_dir = os.path.join(
                        environment.persisted_volume.mount_path,
                        layout_instance.collect_output_dir(vintage, borough),
                    )
                    collect_t = Task(
                        name="collect-"
                        + layout.container_name_postend(vintage, borough),
                        template=collect_c,
                        arguments={
                            "vintage": vintage,
                            "borough": borough,
                            "results_dir": results_dir,
                        },
                    )
                    check_ip_connectivity_t >> collect_t >> dummy_fanin_t
    w.create()
