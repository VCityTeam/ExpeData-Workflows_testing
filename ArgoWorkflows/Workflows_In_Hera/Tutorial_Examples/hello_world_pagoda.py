import sys, os

sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition")
)
from pagoda_cluster_definition import define_cluster

define_cluster()

#### 
from hera import(Workflow, Task)

def hello():
    print("Hello, Hera!")

with Workflow("hello-world-", generate_name=True) as w:
    Task("pythonprint", hello)
    Task(
      "cowsayprint", 
      image="docker/whalesay", 
      command=["cowsay", "Moo Hera"]
    )
w.create()

