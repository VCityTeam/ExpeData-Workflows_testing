import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from hera_utils import parse_arguments
from environment import construct_environment

args = parse_arguments()
environment = construct_environment(args)

####### The workflow starts here
from hera.workflows import script


@script()
def sleep_while_db_boots():
    import time

    time.sleep(30)


if __name__ == "__main__":
    from hera.workflows import Container, DAG, Task, Workflow

    with Workflow(generate_name="sleep-and-exit-", entrypoint="dag-entry") as w:
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
