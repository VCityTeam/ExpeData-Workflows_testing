# Lessons learned<!-- omit from toc -->

## Table of content<!-- omit from toc -->

- [ArgoWorkflows lessons learned (that are also valid at HERA level)](#argoworkflows-lessons-learned-that-are-also-valid-at-hera-level)
  - [Concerning pre and post conditions](#concerning-pre-and-post-conditions)
  - [Parameters vs environment variables](#parameters-vs-environment-variables)
  - [Concerning dynamic loops input retrieval](#concerning-dynamic-loops-input-retrieval)
- [HERA (specific) lessons](#hera-specific-lessons)
  - [Concerning the flowing of parameters](#concerning-the-flowing-of-parameters)
    - [Flowing constants](#flowing-constants)
    - [Input parameters flown through `WorkflowTemplates`](#input-parameters-flown-through-workflowtemplates)
    - [Rules of the thumb for flowing parameters](#rules-of-the-thumb-for-flowing-parameters)
  - [Concerning the uniqueness of Container names](#concerning-the-uniqueness-of-container-names)
  - [Concerning loops](#concerning-loops)
    - [Expression of the need](#expression-of-the-need)
    - ["Dynamic" for-loops in HERA require AW logic expression](#dynamic-for-loops-in-hera-require-aw-logic-expression)
    - ["Static" for-loops expressed in Python: possible but with restrictions](#static-for-loops-expressed-in-python-possible-but-with-restrictions)
    - [Python expressed nested static for-loop restriction](#python-expressed-nested-static-for-loop-restriction)
  - [Daemon task](#daemon-task)
- [Lessons learned for container based workflows](#lessons-learned-for-container-based-workflows)
  - [Disclose reproducibility information encapsulated by container](#disclose-reproducibility-information-encapsulated-by-container)
  - [Concerning the difficulty of asserting database availability](#concerning-the-difficulty-of-asserting-database-availability)

## ArgoWorkflows lessons learned (that are also valid at HERA level)

### Concerning pre and post conditions

Ideally, every task should have an
[explicit postcondition](https://en.wikipedia.org/wiki/Postcondition)
enabling a success/failure test at run time. Because it is not always possible
to modify the core of a task in order to include the postcondition, a
recommandable good practice consists in expressing the postcondition as
a separate task that possibly exploits the content of `results.json` output
file.
The same argument is valid for pre-conditions.

### Parameters vs environment variables

First, let us remind that parameters (that belong to the experiment level)
should be properly separated from the environment (and/or the implementation
details). Such a separation can go up to creating two separated files: a first
one for the parameters and a second one for the environment.
In the testing examples a typical setup goes:

```python
    from pagoda_environment_definition import environment
    from input_2012_tiny_import_dump import parameters
    from experiment_layout import layout
```

### Concerning dynamic loops input retrieval

Let us consider a workflow where the parameter range of loop is only known
at AW run-time (for example the range depends on a previous task output whose
output itself depends on some conditional).
Additionally, let us assume that this dynamic loop parameter is e.g. the result
of previous python (script) task.
Then in order for the loop
Then this "dynamic" for-loop must be retrieve its expressed in the AW logic through HERA
in order for the AW runtime to properly evaluate the range boundaries and for
the AW engine to build the required number of container (and their respective
parameters values).

TO BE FINISHED FIXME FIXME FIXME

## HERA (specific) lessons

### Concerning the flowing of parameters

They are at least to way of flowing the workflow (run time) parameters:

- at the **Hera level** (that is in ArgoWorkflows): the inconvenience is that
  flowing parameter values from the initial CLI (or input file) values down to
  the container's creation can be pretty expensive (in terms of written code).
  Not only does Hera's inputs/arguments passing syntax (`inputs=[Parameter...]`)
  prove to be quite verbose and even sometimes cumbersome, but it also leaves a
  footprint when flown/traversing the WorkFlowTemplate declarations.
- at the **python level**, which has all the notational advantages of the python
  language (think of string manipulation in ArgoWorkflows vs string
  manipulation in python not to mention it's many packages). Yet this is not
  always possible e.g. for dynamic values (that is values only discovered at
  runtime as opposed to Hera submission time) like the IP number of service pod
  or for the iterated values of a loop expressed at the ArgoWorkflow level.

The following is a set of recommendations in order to drive this choice in
favor of a simpler Hera code. Their logic boils down to: "Whenever if possible
prefer python over the ArgoWorkflows ways of things.

#### Flowing constants

Constants (that is input parameters that have singular values and are shared
by all the containers as opposed to multi-valued parameters that required to
be swept) can easily be flown at the python level.

#### Input parameters flown through `WorkflowTemplates`

Input parameters that must be flown through `WorkflowTemplates` face an
ArgoWorkflows related specific constraint. This constraint arises from the
fact that any WorkflowTemplate e.g.

```python
def define_some_workflow(input_parameter):
  with WorkflowTemplate(
      name="workflow-name",
      entrypoint="template-name",
  ) as w:
    # Make some usage of the input_parameter
    [...]
```

is technically translated to become the `template-name` template (i.e. the
template named `template-name`) within some ArgoWorkflows (yaml) file (and
labeled with as `kind: WorkflowTemplate`).
If such a template depends on the `input_parameter` (that will thus take
different values) then, in fact, there are as many such templates as they
are input parameter values.

In order to disambiguate such templates, the a priori "easy" solution is thus
to have a single template while transmitting the input_parameters values at
the Hera level notational level (`inputs=[Parameter...]`), that is at run
time (dynamical parameter). The parametrized template definition thus becomes

```python
# Solution 1: run time parameter passing
def define_some_workflow():     # <--- note the absence of input_parameter
  with WorkflowTemplate(
      name="my-workflow-name",
      entrypoint="template-name",
  ) as w:
      [...]
      with DAG(
        name="template-name",
        inputs=[Parameter(name="input_parameter")]   # Passed at run time
      ) as d:
          [...]
```

Such a solution nevertheless implicitly assumes that all the tasks of such
a workflow, as well as all the sub `WorkflowTemplates` and `Tasks` they
(recursively) use, are able to accept the dynamical parameter, which might
not always be the case. For example is you are using many database server
containers, because you need to distinguish many database, then such servers
containers must accept a run time a (disambiguating) parameter. Yet the
providers of the database probably didn't have in mind such a use case. In
which case it shall be your responsibility (as writer of the `Workflow`) to
either find some technical means (e.g. a wrapper) or to use another solution
(refer below).

A second solution is available only when the topology of the workflow is known
at build time. The assumption is thus that the connectivity of the Workflow
is not discovered dynamically (at runtime) but known at build time, although
this connectivity shall depend on an input parameter. For example this
parametrized-build-time assumption is asserted when the concerned parameter
appears in a (Workflow) for loop. But this assumption does not hold e.g. when
such a parameter is blended with some run-time results and placed within
the `if` condition of the (Workflow).
So assuming that the parametrized-build-time assumption is held, then we
can fold back to flowing and then using that parameter at the python level
by keeping the parameter dependent control-flow (e.g. the for loop) in
order to build the ad-hoc Workflow connectivity. This means, that in our for
loop example use case, we then build (with a Python loop) e.g. sequential or
parallel sequence of tasks.
Note that this forbids the usage of the ArgoWorkflows's
[loop result aggregation feature](https://argoproj.github.io/argo-workflows/walk-through/loops/#accessing-the-aggregate-results-of-a-loop).

```python
# Solution 2: parametrized-build-time assumption
with Workflow([...], entrypoint="main") as w:

    with DAG(name="main"):
        tasks = list()
        # Only usage of the parameter is at the python level which includes
        # the control flow level (transposed to a Workflow topology)
        for param in input_parameter:
            task_param = Task(
              name="some-task-name"+param,
              [...do some stuff...]
            tasks.append(task_param)
            # Then use tasks to hard-wire the required dag topology...
        )
```

A more cumbersome, and third, solution consists in explicitly
[mangling](https://en.wikipedia.org/wiki/Name_mangling) all the required
templates (names) by declining their name e.g

```python
# Solution 3: mangled template names
def define_some_workflow(input_parameter):
  template_name="template-name"+str(input_parameter)  # Name mangling
  with WorkflowTemplate(
      name="my-workflow-name",
      entrypoint=template_name,                # Mangled name used here
  ) as w:
      [...]
      with DAG(name=template_name):   # <--- note the absence of input=[]
          [...]
```

The inconvenient, of this mangling way of things, is that the calling code is
constrained to use the same mangling scheme e.g.

```python
with Workflow([...], entrypoint="main") as w:

    with DAG(name="main"):
        tasks = list()
        for param in input_parameter:
            # Mangled name but use the exact SAME mangling scheme
            mangled_template_name="template-name"+str(input_parameter)
            task_param = Task(
              name="some-task-name"+param,
              template_ref=models.TemplateRef(
                  name="my-workflow-name",
                  template=mangled_template_name,   # Used here
            )
            tasks.append(task_param)
            # Then use tasks to hard-wire the required dag topology...
        )
```

#### Rules of the thumb for flowing parameters

- Constants should be transmitted at the python level.
- input parameters that do _not_ require to be flown through
  Workflow-templates should be transmitted at the python level (for the
  above mentioned convenience reason).
- input parameters _requiring_ to be flown through Workflow-templates can
  adopt three methods (by order of preference i.e. favoring simplicity)
  1. For parametrized-build-time situation, flow the parameters through python
  2. (a) Run time parameter passing with ArgoWorkflows parameters
  3. (b) Still at python level, use mangled template names
- Eventually, what is dynamic (e.g. the IP number of a service pod) must
  be flown at the Hera/ArgoWorkflows level

### Concerning the uniqueness of Container names

The name argument of a `Container()` definition must be unique across a full
workflow as illustrated by the
Failing_Or_Issues/issue_duplicate_container_name.py workflow.
If we thus need to "burn in" some parameters within a set of different
containers all sharing the same image (think of the database argument for the
`db_isready_container()` container creation function), then we must generate
different container names (in order to avoid container name collisions).
Refer to
[issue_duplicate_container_name.py](./Failing_Or_Issues/issue_duplicate_container_name.py)
for an illustration of this issue and a possible workaround.

### Concerning loops

#### Expression of the need

As expressed in the comments of
[Failing_Or_Issues/test_collect_fail.py](./Failing_Or_Issues/test_collect_fail.py)
the notational syntax of AW does NOT allow to express in Python (at Hera level)
some experimental logic that is to be evaluated at AW runtime.
For example the directory layout of the pipeline must be expressed with
[AW expressions](https://argoproj.github.io/argo-workflows/variables/#expression)
which exposes Hera underlying mechanisms and constrains Hera users to know (and
mix) both Python and AW-expressions.

Thus if we wish to stick to a single language for expressing the experimental
logic (that is Python as offered by Hera) we need to drop the native AW way for
expressing loops and instead express such loops in Python.

#### "Dynamic" for-loops in HERA require AW logic expression

Let us consider a workflow where the parameter range is only known at AW
run-time: for example the range depends on a previous task output whose
output itself depends on some conditional.
Then this "dynamic" for-loop must be expressed in the AW logic through HERA
in order for the AW runtime to properly evaluate the range boundaries and for
the AW engine to build the required number of container (and their respective
parameters values).

Providing such a HERA/Python for-loop syntax (in Python and on top of HERA)
would require that HERA provides a Python API for triggering containers at
runtime. This is beyond reach of HERA that is not an engine but "just" a
translator or code-generator with AW as target language.
Exeunt HERA/Python dynamic for-loops.

#### "Static" for-loops expressed in Python: possible but with restrictions

We now consider the particular for-loop case where **the pipeline
topology/structure is known at Hera evaluation stage**, that is where the
range of the for-loop is know at HERA submission stage.

Then the for-loop can be expressed in Python (without using HERA/AW expression).
One quite strong advantage of such a notational practice is for nested loops
that are much easier to express since they do not require to
[declare a WorkflowTemplate for the inner loop](../Workflows_In_Yaml/Failing_Or_Issues/nested-loops-issue.yml).

Yet, expressing for-loops in Python has a main drawbacks: workflows requiring
[fan-in](https://github.com/argoproj-labs/hera/blob/main/examples/workflows/dynamic_fanout_fanin.py)
techniques cannot use Hera/AW syntactic "sugar".
This might not be such a loss given the current, as of version 5.X, notational
intricacies. But still fan-in techniques require a dedicated task to be
manually written, which can quickly become quite cumbersome and most often
impossible as illustrated by the
[Failing_Or_Issues/test_collect_fail.py](./Failing_Or_Issues/test_collect_fail.py).

#### Python expressed nested static for-loop restriction

When the inner loop depends on the ranging parameter then one must define a
`WorkflowTemplate` for the inner loop. This constrain is a consequence of AW
approach that in order to flow a context variable to a loop one must explicitly
declare it and thus transform the loop to become a function (that is a
`WorkflowTemplate`).

### Daemon task

Some database related `WorkflowTemplates` might need to express the creation of
a database server that should outlive their template scope. For example one
might need to encapsulate within a `WorkflowTemplate` the powering up of a
database, its initialization with a model, the assertion that some usage tests
are effective. This allows the `WorkflowTemplate` caller to hide the technical
details of database creation.

Alas it is not possible to integrate the starting of the database within
such a `WorkflowTemplate` because, as stated in the
[ArgoWorkflows documentation](https://argoproj.github.io/argo-workflows/walk-through/daemon-containers/)
the (started) daemons will be automatically destroyed when the `WorkflowTemplate`
exits the template scope in which the daemon was invoked.

## Lessons learned for container based workflows

### Disclose reproducibility information encapsulated by container

By default a container based workflow language/engine, that is a workflow
whose basic building blocks are container, is most often blind to the what
gets encapsulated within those executable building blocks (containers).
When a (container) image is taken from some registry
(e.g. [`dockerhub`](https://hub.docker.com/)), and depending on the degree
of transparency that the conceivers of the container wished to offer,
it is sometimes possible to retrieve some constituting elements. This ranges
from its original `Dockerfile` (as sometimes offered by the developers through
third party registry websites), its constituting files
([`docker export` or `docker save`](https://stackoverflow.com/questions/44769315/how-to-see-docker-image-contents))
(although [multi-stage builds](https://docs.docker.com/build/building/multi-stage/)
are done to reduce the traces/footprint), to few tidbits
([`docker inspect`](https://docs.docker.com/reference/cli/docker/inspect/)).
If you are driven by reproducibility concerns, you will of course carefully
select the images you use in your pipelines by asserting they offer some basic
reproducibility criteria (how they are build, that is where is their
Dockerfile and associated build context, where are the versioned sources,
including the sources of their recursive dependencies).

But for the containers that you develop (and distribute) you should ease this
process for your run-time users (which might include yourself in a couple
years, months or even days) by offering the minimal traceability in a
**container technology neutral** manner.
For example you might design you main container executable to produce a
`results.json` (or any low-tech, human readable or open data format) file
that summarizes e.g.

- the version of the sources used to build that executable,
- the original repository (including the building context/mechanism),
- the arguments used when running the executable,
- a list of the used inputs,
- a list of the produced outputs,
- execution "time", memory or disk footprints,
- ...

It could be that such a container-neutral/human-readable file is directly
offered by the executable that is embarked in the image.
When not, because the developer in charge of offering the image (e.g. the
Dockerfile and more generally the building context) has access to that
information, this developer should provide (e.g. through
[CMD](https://docs.docker.com/reference/dockerfile/#cmd) or
[ENTRYPOINT](https://docs.docker.com/reference/dockerfile/#entrypoint)
wrappers) that container disclosure `results.json` file.

### Concerning the difficulty of asserting database availability

In order to define the
[various probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
for a database pod, one might use the k8s equivalent of

```bash
docker run -t postgres:15 bash -c "export PGPASSWORD=smdb ; psql --user smdb --host 10.42.204.224 --port 5444 --dbname smdb -c 'SELECT * FROM pg_catalog.pg_tables'"
```

One of the difficulties is to designate the host that should be checked in
a portable (pod independent) manner. In the above request the host was
specified with it's IP number (that varies accros pipeline invocations).
But if one tries to use e.g. `0.0.0.0`, `localhost` or `127.0.0.1` instead of
the IP of the pod then the request (and thus the probe)...

Notes:

- [Customizing the host file looks kludgy](https://kubernetes.io/docs/tasks/network/customize-hosts-file-for-pods/)
- [here is a k8s related issue](https://github.com/kubernetes/kubernetes/issues/86504) that proposes (to be tested) to remove any reference to the host flag...
