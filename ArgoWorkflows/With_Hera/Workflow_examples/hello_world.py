from hera.workflow import Workflow
from hera.task import Task

def define_workflow():
  def hello():
      print("Hello, Hera!")

  with Workflow("hello-hera-", generate_name=True) as w:
      Task("pythonprint", hello)
      Task(
        "cowsayprint", 
        image="docker/whalesay", 
        command=["cowsay", "Moo Hera"]
      )
  w.create()



