from hera.workflows import script


@script()
def sleep_while_db_boots():
    import time

    time.sleep(60)


if __name__ == "__main__":
    import sys, os

    sys.path.append(
        os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition")
    )
    from pagoda_cluster_definition import define_cluster
    from hera.workflows import Container, DAG, Task, Workflow

    cluster = define_cluster()
    with Workflow(
        generate_name="sleep-and-exit-", entrypoint="dag-entry"
    ) as w:
        whalesay_c = Container(
            name="whalesay",
            image="docker/whalesay:latest",
            command=["cowsay", "A good nap and to bed."],
        )
        with DAG(name="dag-entry"):
            sleep_t = sleep_while_db_boots(name="sleepawhile")
            whalesay_t = Task(
                name="whalesay",
                template=whalesay_c,
            )
            sleep_t >> whalesay_t
    w.create()
