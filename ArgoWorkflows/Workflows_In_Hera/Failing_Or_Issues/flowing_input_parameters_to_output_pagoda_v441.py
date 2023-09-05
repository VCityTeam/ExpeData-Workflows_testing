import sys, os

sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition")
)
from pagoda_cluster_definition import define_cluster

cluster = define_cluster()

####################################
# Submitted to
# https://github.com/argoproj-labs/hera/discussions/561
####################################

from hera import ConfigMapEnvFrom, Parameter, Task, Workflow


def consume(msg: str):
    print(f"Message was: {msg}")


with Workflow("valueusage") as w:
    t1 = Task(
        "cowsayprint",
        image="docker/whalesay",
        env=[
            ConfigMapEnvFrom(config_map_name=cluster.configmap, optional=False)
        ],
        inputs=[{"first": "thirst", "second": "thecond"}],
        command=[
            "cowsay",
            # Following gets nicely said by the cow:
            "{{inputs.parameters.first}}/{{inputs.parameters.second}}",
        ],
        # But how to translate the following AW-yaml version
        #   outputs:
        #     parameters:
        #     - name: msg
        #       value: "{{inputs.parameters.first}}/{{inputs.parameters.second}}"
        outputs=["????????????????????"],
    )
    t2 = Task("c", consume, inputs=[t1.get_parameter("msg")])
    t1 >> t2

w.create()
