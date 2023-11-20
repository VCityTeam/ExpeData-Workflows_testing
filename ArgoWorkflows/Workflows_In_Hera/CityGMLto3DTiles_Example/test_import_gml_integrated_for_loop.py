import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition"))

from hera_utils import hera_assert_version

hera_assert_version("5.6.0")

################ Environment (including cluster) independent code (well almost)
if __name__ == "__main__":
    from hera.workflows import DAG, Task, models, Parameter, Workflow

    from utils import whalesay_container
    from database import threedcitydb_start_db_container
    from database_aggregated import define_import_boroughs_to_3dcitydb_template

    from pagoda_environment_definition import environment
    from input_2012_tiny_import_dump import inputs
    from experiment_layout import layout

    #### EXPERIMENT DESIGN NOTES (and on of its consequence that is that
    # vintage and borough parameters do NOT play a symetrical role):
    # At some level of abstraction
    # - a boroughs-3Dtiles (of a city) can be seen as the (geographic)
    #   geometrical data the set of boroughs that are considered to describe
    #   that city.
    # - a Temporal-3DTiles can be seen as temporal (vintages being the coarse
    #   grain for time) stack of such boroughs-3Dtiles.
    # Most often when projects work on city data, they first scale up the data
    # by considering a greater number of boroughs (bigger cities). Once
    # geographic scale-up is achieved then (and only then) does time kick-in
    # (through different time based versions of the city).
    # When a city modeling project adopts such a project history (implicitly)
    # inherited ranking of space vs time parameters, and when data size imposes
    # to split among different databases, then a "natural" choice arises:
    # make as many databases are they are vintages (each vintaged-db regrouping
    # all the boroughs).
    # DESIGN CONSEQUENCE: the vintage parameters primes over the borough
    # parameter (because databases are vintaged-databases).

    layout_instance = layout(inputs.constants)
    db_import_boroughs_template_names = {}
    for vintage in inputs.parameters.vintages:
        db_import_boroughs_template_name = "db-import-boroughs-template-" + str(vintage)
        define_import_boroughs_to_3dcitydb_template(
            environment,
            layout_instance,
            vintage,
            inputs.parameters.boroughs,
            db_import_boroughs_template_name,
        )
        db_import_boroughs_template_names[vintage] = db_import_boroughs_template_name

    with Workflow(generate_name="import-gml-", entrypoint="main") as w:
        threedcitydb_containers = {}
        for vintage in inputs.parameters.vintages:
            threedcitydb_start_db_c = threedcitydb_start_db_container(
                environment,
                inputs.constants,
                layout(inputs.constants).database(vintage),
            )
            threedcitydb_containers[vintage] = threedcitydb_start_db_c

        with DAG(name="main"):
            for vintage in inputs.parameters.vintages:
                start_db_t = Task(
                    name="start-db-daemon-" + str(vintage),
                    template=threedcitydb_containers[vintage],
                )

                # DESIGN NOTES: refer above on why vintage loop comes before
                # the borough loop and why that borough loop gets integrated
                # (and hidden away) into the following WorkflowTemplate

                import_vintage_boroughs_t = Task(
                    name="import-" + str(vintage) + "-boroughs",
                    template_ref=models.TemplateRef(
                        name="workflow-import-" + str(vintage),
                        template=db_import_boroughs_template_names[vintage],
                    ),
                    arguments={"dbhostaddr": start_db_t.ip},
                )

                whalesay_input_dir_t = Task(
                    name="whalesayinputdir" + str(vintage) + "-boroughs",
                    template=whalesay_container,
                    arguments={
                        "message": "Imported vintage "
                        + str(vintage)
                        + " ".join(inputs.parameters.boroughs)
                    },
                )

                start_db_t >> import_vintage_boroughs_t >> whalesay_input_dir_t
    w.create()
