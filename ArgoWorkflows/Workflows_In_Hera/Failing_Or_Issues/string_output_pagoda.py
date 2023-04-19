import sys, os

sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition")
)
from pagoda_cluster_definition import define_cluster

cluster = define_cluster()

####################################
# Following code submitted to Hera: refer to
# https://github.com/argoproj-labs/hera/issues/559
####################################

from hera import Parameter, Task, Workflow

def dummy():
    ...

def consume(msg: str):
    print(f"Message was: {msg}")

### The following workflow tries to transmit a simple string from
# task t1 (as output) to task t2 (as input):

with Workflow("io-", generate_name=True) as w:
    # The following task will fail at submission stage with
    #    templates.d.outputs.parameters.msg.path must be specified for 
    #    Script templates
    t1 = Task(
        "d", dummy, outputs=[Parameter("msg", value="some_valuable_message")]
    )
    t2 = Task("c", consume, args={"msg": t1.get_parameter("msg")})

    t1 >> t2

w.create()

# Note: defining task t2 as 
#    t2 = Task("c", consume, inputs=[t1.get_parameter("msg")])
# also fails at submission stage with
#    templates.d.outputs.parameters.msg.path must be specified for 
#    Script templates
# Note that using inputs instead of args is a bit broader context because
# "inputs" can be flown to the container parameters whereas "args" can only
# be flown to the command standing in the container.