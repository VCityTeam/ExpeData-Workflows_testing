import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import types
import pagoda
cluster=pagoda.define_cluster()


########
parameters = types.SimpleNamespace(
  borough='LYON_8EME',
  pattern='BATI',
  experiment_output_dir='junk',
  vintage='2012',
)

results_dir=os.path.join(
  parameters.experiment_output_dir,
  "stage_1", 
  parameters.vintage,
  parameters.borough+"_"+parameters.vintage
)

def disk_usage():
    import os
    print(f'Available storage:\n{os.popen("df -h").read()}')

from hera import Task, Workflow
from hera import ImagePullPolicy

def define_workflow():
  with Workflow("collect-", generate_name=True) as w:
    Task("firsttask", disk_usage)
    Task(
      "second",
      image=cluster.docker_registry + "vcity/collect_lyon_data:0.1",
      image_pull_policy=ImagePullPolicy.IfNotPresent,
      command=["python3"],
      inputs=["entrypoint.py",
                "--borough",     parameters.borough,
                "--pattern",     parameters.pattern,
                "--results_dir", results_dir,
                "--vintage",     parameters.vintage,
                "--volume",      "bozo"]    # Was parameters.persistedVolume
    )
  w.create()

define_workflow()
