# When workflow uses a for loop with a breadth/range (e.g. the number of
# parallel tasks) that is known at Hera submission stage, then the workflow
# writter has the freedom to express the for loop at the python/Hera level.
# In other terms the workflow writter can circumvent the native AW expression
# of foor loops (refer to "with_item" or "with_param" AW expressions), as
# illustrated by the pipeline of this example.
# Notice that this example further illustates that in such a case, the
# fanout/fanin feature (that is being able to collect the outputs of each
# of the spawn processes) is possible in Python although a bit painfull
# to express.
#
# In addition also notice that the below example IS NOT A TRUE DYNAMIC FOR
# LOOP. Indeed, althgouh the value of the scope variable is randomized it is
# still known at Hera submission stage !
# The QUESTION is then: when the breadth/range of the for loop is (only)
# available at AW run-time stage (we would need the for-loop to range on a
# parameter whose value would be the output of a previous task.) can we still
# express this loop at the python/Hera level ? Or, in such case, do we have to
# "fold back" the native AW expression of foor loops?
#
# LESSON LEARNED: for dynamic for loops, we coulnd't find a mechanism enabling
# the expression of such loops at the python (Hera) level (as opposed to the
# AW level expressed through Hera that is by using "with_item" or "with_param"
# AW expressions). For this to be possible, we tried to define a @script()
# (an AW task) that would be able to trigger other tasks: but Hera doesn't
# seem to offer such a mechanism i.e. to refer to the ongoing workflow to
# (dynamically submit new tasks).
# In other terms, dynamic loops MUST be expressed with the native AW (through
# Hera) for loop syntax (refer e.g.
# https://hera-workflows.readthedocs.io/en/5.11.0/walk-through/loops/)
################

import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition"))

from hera_utils import hera_assert_version

hera_assert_version("5.6.0")

####
import random
from hera.workflows import (
    DAG,
    ExistingVolume,
    Parameter,
    script,
    Task,
    Workflow,
)

# The following import points Hera to the PAgoDA cluster
from pagoda_environment_definition import environment

shared_volume = ExistingVolume(
    name="dummy-name",
    claim_name=environment.persisted_volume.claim_name,
    mount_path="/my-tmp/",  # WARNING: Must be matched (refer below)
)


@script(
    volumes=[shared_volume],
)
def assert_empty_output_directory():
    import glob, sys

    # Because the only way for fanin to assert that all results were properly
    # written/produced is by asserting for the number of result files, a
    # strong precondition is to assert that the result directory is indeed empty.

    # WARNING: following value must match with shared_volume's mount_path
    mount_path = "/my-tmp/"
    # WARNING: both following variables must match with write_output
    # corresponding variables
    experiment_output_dir = mount_path + "junk-loop/"
    result_file_pattern = experiment_output_dir + "result_*.txt"
    result_files = glob.glob(result_file_pattern, recursive=False)
    if len(result_files):
        print("Output directory ", experiment_output_dir, " is not empty.")
        print("The following result files we encountered: ", result_files)
        print("Exiting.")
        sys.exit(1)
    print("Output directory ", experiment_output_dir, " is empty as expected.")


@script(
    volumes=[shared_volume],
    # outputs argument is not present here because outputs are not flown at
    # AW level but through files with conventional names.
)
def write_output(index: int):
    import os

    # WARNING: following value must match with shared_volume's mount_path
    mount_path = "/my-tmp/"
    experiment_output_dir = mount_path + "junk-loop/"
    os.makedirs(experiment_output_dir, exist_ok=True)
    result_file_name = experiment_output_dir + "result_" + str(index) + ".txt"
    if os.path.exists(result_file_name):
        print("WARNING: overwritting existing result file " + result_file_name)
    with open(result_file_name, "w") as log:
        log.write(str(index * index))


@script(
    volumes=[shared_volume],
)
def fanin(scope_as_string):
    import glob, sys

    # The fanin method must assert that all fanout computation tasks produced
    # their due output. There should be as many result files as given by the
    # "scope_as_string" argument of this @script() (that corresponds to
    # "range(scope)" as defined in the Workflow definition).

    ### Count the number of result files
    # WARNING: following value must match with shared_volume's mount_path
    mount_path = "/my-tmp/"
    # WARNING: both following variables must match with write_output
    # corresponding variables
    experiment_output_dir = mount_path + "junk-loop/"
    result_file_pattern = experiment_output_dir + "result_*.txt"
    result_files = glob.glob(result_file_pattern, recursive=False)

    ### If not enough result files than (probably that) some task failed
    scope = int(scope_as_string)
    if len(result_files) < scope:
        print("Missing ", scope - len(result_files), " result files.")
        print("Some fanout task probably failed.")
        print("Exiting.")
        sys.exit(1)

    ### Too many result files means something went really wrong
    if len(result_files) > scope:
        print(
            "Too many result files present. Found ",
            len(result_files),
            "when ",
            scope,
            "were expected.",
        )
        print("Exiting.")
        sys.exit(1)

    ### When the proper number of result files is encountered then get the
    # fanin job done:
    print("Final number of result files (", scope, ") is OK. Processing fanin.")
    sum_of_squares = 0
    for index in range(scope):
        result_file = experiment_output_dir + "result_" + str(index) + ".txt"
        with open(result_file, "r") as result:
            for line in result:
                for x in line.split():
                    result_value = int(x)
                    print(
                        "Fanin collected value: " + str(result_value),
                        " (from file ",
                        result_file,
                        ").",
                    )
                    sum_of_squares += result_value
    print("Fanin task final result (sum of squares) = ", sum_of_squares)


with Workflow(generate_name="fanout-fanin-for-loop-in-python-", entrypoint="main") as w:
    with DAG(name="main"):
        # WATCH OUT: although the breadth "of the fanout" is randomized, it is
        # still known at Hera submission stage. In other terms the breadth is
        # NOT a Workflow dynamic value !
        scope = random.randint(2, 4)
        pre_condition_t: Task = assert_empty_output_directory(
            name="is-output-directory-empty"
        )
        fanin_t: Task = fanin(
            name="fanin", arguments=Parameter(name="scope_as_string", value=scope)
        )
        #### The question was: can be express this for loop in python BUT in
        # a task that spawns some tasks ?
        for i in range(scope):
            current_task: Task = write_output(
                name="writing-" + str(i),
                arguments=Parameter(name="index", value=i),
            )
            pre_condition_t >> current_task >> fanin_t

w.create()
