# [Argo Workflows](https://argoproj.github.io/argo-workflows/) language features

## References

- [Argo Workflows github hosted docs](https://argoproj.github.io/argo-workflows/)
- [Official workflow examples](https://github.com/argoproj/argo-workflows/tree/master/examples)

## Language features

### Conditional execution

- [flip-coin Source](https://github.com/argoproj/argo-workflows/blob/master/examples/coinflip-recursive.yaml)
- Testing: `argo submit --watch https://raw.githubusercontent.com/argoproj/argo-workflows/master/examples/coinflip-recursive.yaml`
- Note: conditions are expressed in Go and evaluated with [goevaluate](https://github.com/Knetic/govaluate).

### Workflow structure

Workflows can be assembled out of  

- [steps](https://github.com/argoproj/argo-workflows/tree/master/examples#steps) i.e. a linear structure (succession of steps) with the possibility for some steps to run in parallel with others: example [dag-diamond-steps.yaml](https://github.com/argoproj/argo-workflows/blob/master/examples/dag-diamond-steps.yaml)
- [tasks](https://github.com/argoproj/argo-workflows/tree/master/examples#dag) in which case the described workflows are [DAGs](https://en.wikipedia.org/wiki/Directed_acyclic_graph) (possibly with multiple roots/entry-points e.g. [dag-multiroot.yaml](https://github.com/argoproj/argo-workflows/blob/master/examples/dag-multiroot.yaml)): example [dag-daemon-task.yaml](https://github.com/argoproj/argo-workflows/blob/master/examples/dag-daemon-task.yaml)

Note: the combination of steps/tasks with conditional execution allows for **dynamic workflow structures** (that is structures that are determined along the workflow execution) refer to e.g. [dag-conditional-parameters.yaml](https://github.com/argoproj/argo-workflows/blob/master/examples/dag-conditional-parameters.yaml), [dag-enhanced-depends.yaml](https://github.com/argoproj/argo-workflows/blob/master/examples/dag-enhanced-depends.yaml) or [dag-coinflip.yaml](https://github.com/argoproj/argo-workflows/blob/master/examples/dag-coinflip.yaml)

### [Fixtures](https://en.wikipedia.org/wiki/Test_fixture#Software)

AW provides so called [daemon containers](https://github.com/argoproj/argo-workflows/tree/master/examples#daemon-containers) whose "existence can persist across multiple steps or even the entire workflow" (as opposed to so called [sidecars](https://github.com/argoproj/argo-workflows/tree/master/examples#sidecars)).

### [Iterations](https://github.com/argoproj/argo-workflows/tree/master/examples#loops)

Looping can occur on lists of items ([withItems](https://argoproj.github.io/argo-workflows/fields/#workflowstep)), lists of sets of items, on generated lists ([withParam](https://argoproj.github.io/argo-workflows/fields/#workflowstep)).

By default the execution of the tasks of the loop is done in parallel. Yet it is possible to [constrain the workflow](https://gitanswer.com/argo-workflows-execute-loop-in-sequentially-go-1000666110) with a [mutex on the task](https://github.com/argoproj/argo-workflows/blob/master/examples/synchronization-mutex-tmpl-level.yaml), in order to obain a sequetial execution.

### Parameter/artifact passing

#### Input parameters

- Parameter native types (that is within the workflow description): [objects, strings, booleans, arrays](https://argoproj.github.io/argo-workflows/core-concepts/)
- Parameter [defined within the workflow](https://github.com/argoproj/argo-workflows/blob/master/examples/arguments-parameters.yaml)
- Parameters can be overloaded (so called argument-parameter) from the CLI with
  the [`-p CLI flag`](https://github.com/argoproj/argo-workflows/blob/master/examples/arguments-parameters.yaml#L9)
- Some parameter preprocessing can be done at the workflow level through the
  usage of the
  [parameter aggregation idiom](https://github.com/argoproj/argo-workflows/blob/master/examples/parameter-aggregation.yaml)

#### Output parameters

- [artifact: files saved by a container](https://argoproj.github.io/argo-workflows/core-concepts/)

### Various language features

- [Retrying failed/errored steps](https://github.com/argoproj/argo-workflows/tree/master/examples#retrying-failed-or-errored-steps)

### Technical notes

### Concerning Port forwarding

Assume we wish to describe a workflow that consumes two postgres database
(servers). When using `docker-compose` we would need to distinguish the two
instances of postgres container through the usage
[port redirection/forwarding](https://docs.docker.com/config/containers/container-networking/).
For example the first postgres container could publish default port `5432` (on
the native host) while the second instance would use port forwarding to publish
its port as e.g. `5433` (on the native host with a redirection to the container
internal port `5432`).

Within the kubernetes way of things, each pods gets attributed with its own
IP number. The distinction between the two postgres instances can thus be done
at the IP level has opposed to the port level (on condition that such container
do not run on the same pod ?).
This might explain why AW documentation doesn't seem to offer a syntax for
redirection
([`containerPort`](https://argoproj.github.io/argo-workflows/fields/#containerport)
look like a simple exposure of a port as opposed to redirection).

---

## Tasks

The Tasks term is here used with its
[k8s terminology](https://kubernetes.io/docs/tasks/).

### Task: data persistence, mounting a host directory into the guest with Minikube

When developing docker containers on a desktop host, and in order to offer
persistence (for data generated by the container), docker offers to mount a
host directory into the container through
[docker "bind mounts"](https://docs.docker.com/storage/bind-mounts/).

k8s mechanism for persistence uses the notion of
[persistent volume](https://kubernetes.io/docs/concepts/storage/persistent-volumes/).
When developing on a Minikube host (e.g. using a VM on desktop host),
[minikube is configured to persist files stored under a limited set of host directories](https://minikube.sigs.k8s.io/docs/handbook/persistent_volumes/) (e.g `/data`, `/tmp/hostpath_pv` ...).
On OSX, and by default, a native (that is _not_ within the VM) user home
directory cannot be used to persist pod data.
But Minikube offers the
[`minikube mount <>`](https://minikube.sigs.k8s.io/docs/handbook/mount/)
to allow for a user home sub-directory (on the host native system) to be
mounted as k8s volume that pods can use to persist their data.
