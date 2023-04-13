import os
from hera import (
    ConfigMapEnvFrom,
    ImagePullPolicy,
    Parameter,
    Task,
    ValueFrom,
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
#    and materialize it some form
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
# When the provider of the Task that wraps the guilty container has some
# knowledge of the container outputs layout, that developer can prodive a
# post-treatment Task that produces that output strucutre file (in a effort
# of "normalization" of the container with a perspective of workflow usage).
#
# The following write_output_task Task constructor implement this
# post-treatment strategy by writing the necessary file. Its code can be
# seen as an Hera rewrite of the following docker one-liner
#  docker run --mount type=bind,source="$(pwd)",target=/tmp \
#         -t python:3.11.3-bullseye python -c
#         "with open('/tmp/test_write.log', 'a') as log: log.write('Message\n')"
def write_output_task(cluster, content):
    dummy_file = "/tmp/junk"
    command = (
        "with open('"
        + dummy_file
        + "', 'a') as log: log.write('"
        + content
        + "')"
    )
    task = Task(
        "writeoutput",
        image="python:3.11.3-bullseye",
        image_pull_policy=ImagePullPolicy.Always,
        env=[
            # Assumes the corresponding config map is defined in the k8s cluster
            ConfigMapEnvFrom(config_map_name=cluster.configmap, optional=False)
        ],
        command=["python", "-c", command],
        outputs=[Parameter("msg", value_from=ValueFrom(path=dummy_file))],
    )
    return task


if __name__ == "__main__":
    import sys, os

    sys.path.append(
        os.path.join(
            os.path.dirname(__file__), "..", "Workflow_PaGoDa_definition"
        )
    )
    from pagoda_cluster_definition import define_cluster

    def consume(msg: str):
        print(f"Message was: {msg}")

    cluster = define_cluster()
    with Workflow("fullcollect-", generate_name=True) as w:
        write_output_t = write_output_task(
            cluster, content="Some_nice_message"
        )
        t2 = Task("c", consume, inputs=[write_output_t.get_parameter("msg")])
        write_output_t >> t2
    w.create()
