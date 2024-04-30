import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from hera_utils import parse_arguments
from environment import construct_environment

args = parse_arguments()
environment = construct_environment(args)

#############
from hera.workflows import (
    DAG,
    models,
    Parameter,
    script,
    Workflow,
)

# The need:
# Some containers do provide a file summarizing the (file) outputs of their
# computations e.g. a "results.json" file (with the ad-hoc fields) referencing
# all the files that were produced. Such a "results.json" file contains the
# knowledge of the structure of the results that is required by a downstream
# application/computation to exploit the results. Such an output description
# file (specially when it is in JSON format) can be used by Hera by using the
# the AW `ValueFrom` expression.
#
# But what are the workarounds when a container does _not_ provide its outputs
# structure ? The need is now decomposed in two steps
#  - first, capture this information (the knowledge of the output structure)
#    and materialize it in some form
#  - second, flow that information to the downstream task that will exploit it
#    as its input.
#
# Solution A/ : Have the Argo workflow produce and expose the result.
# This is the strategy used by the split-buildings-template in the
#    Workflow_CityGMLto3DTiles_Example/workflow-template/atomic-steps.yml
# workflow. Its output, that goes
#     outputs:
#     parameters:
#     - name: resulting-filenames
#       value: "{{inputs.parameters.output_dir}}/{{inputs.parameters.output_filename}}"
# re-exposes the resulting filenamese as a parameter for the next Task to use.
# Alas this doesn't seem to work since at this stage Hera doesn't offer the
# equivalent of the "Value" class/expression. Refer to
#     Failing_Or_Issues/flowing_input_parameters_to_output.py
#
# Solution B/ : Have Hera (python) produce and flow the result
# This plan-B alas also fails because it seems equally difficult to pass
# a string (or any other python variable value) as an input parameter to an
# Hera expressed Task. Refer to
#     Failing_Or_Issues/string_output.py
# And trying to define an `outputs=[]` with RawFactory is not well
# well documented: refer to
#     Failing_Or_Issues/raw_archive.py
#
# Solution C/ : Have Hera produce this output file
# When the provider of the Task that wraps the "guilty" container has some
# knowledge of the container outputs layout, that developer can prodive a
# post-treatment Task that produces that output strucutre file (in a effort
# of "normalization" of the container with a perspective of workflow usage).
#
# The following write_output_task Task constructor implements this
# post-treatment strategy by writing the necessary file. Its code can be
# seen as an Hera rewrite of the following docker one-liner
#  docker run --mount type=bind,source="$(pwd)",target=/tmp \
#         -t python:3.11.3-bullseye python -c
#         "with open('/tmp/test_write.log', 'a') as log: log.write('Message\n')"
#
# Historical note: eventually (after evolving code from Hera version 4.4.1) the
# following code is almost identical to the one of
# https://github.com/argoproj-labs/hera/blob/main/examples/workflows/dag_with_script_output_param_passing.py


@script(
    outputs=[Parameter(name="result", value_from=models.ValueFrom(path="/tmp/junk"))]
)
def write_output(content):
    dummy_file = "/tmp/junk"
    with open(dummy_file, "a") as log:
        log.write(str(content))


@script()
def consume(msg):
    print(msg)
    # FAIL note: for some strange reason defining the body as this function
    # as
    #      print(f"Message was: {msg}")
    # will provoque Hera to fail at submission stage.


with Workflow(generate_name="write-output-", entrypoint="d") as w:
    with DAG(name="d"):
        write_output_t = write_output(
            arguments=Parameter(
                name="content",
                value="Some_nice_message",
            )
        )
        consume_t = consume(
            arguments=write_output_t.get_parameter("result").with_name("msg")
        )
        write_output_t >> consume_t
w.create()
