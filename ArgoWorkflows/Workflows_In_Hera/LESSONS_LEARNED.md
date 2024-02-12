# Lessons learned

<!-- TOC -->

- [HERA/AW related lessons learned](#heraaw-related-lessons-learned)
  - [Pre and post conditions](#pre-and-post-conditions)
  - [Parameters vs environment variables](#parameters-vs-environment-variables)
  - [Concerning the flowing of parameters](#concerning-the-flowing-of-parameters)
  - [Concerning loops](#concerning-loops)
- [Non HERA related lessons learned](#non-hera-related-lessons-learned)
  - [Concerning the difficulty of asserting database availability](#concerning-the-difficulty-of-asserting-database-availability)

<!-- /TOC -->

## HERA/AW related lessons learned

### Pre and post conditions

Ideally, every task should have an 
[explicit postcondition](https://en.wikipedia.org/wiki/Postcondition)
enabling a success/failure test at run time. Because it is not always possible
to modify the core of task to include the postcondition, a recommandable good
practice is to have a separate postcondition task that possibly exploits the
content of `results.json` output file.

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

#### Rules of the thumb

- Constants should be transmitted at the python level.
- input parameters that do _not_ require to be flown through 
  Workflow-templates should be transmitted at the python level (for the 
  above mentioned convenience reason).
- input parameters _requiring_ to be flown through Workflow-templates can
  adopt three methods (by order of preference i.e. favoring simplicity)
  1. For parametrized-build-time situation, flow the parameters through python
  2. (a) Run time parameter passing with ArgoWorkflows parameters
  2. (b) Still at python level, use mangled template names
- Eventually, what is dynamic (e.g. the IP number of a service pod) must
  be flown at the Hera/ArgoWorkflows level

### Concerning loops

As expressed in the comments of 
[Failing_Or_Issues/test_collect_fail_first.py](Failing_Or_Issues/test_collect_fail_first.py)
[Failing_Or_Issues/test_collect_fail_second.py](Failing_Or_Issues/test_collect_fail_second.py),
the notational syntax of AW does NOT allow to express in Python (at Hera level)
some experimental logic that is to be evaluated at AW runtime.
For example the directory layout of the pipeline must be expressed with
[AW expressions](https://argoproj.github.io/argo-workflows/variables/#expression)
which exposes Hera underlying mechanisms and constrains Hera users to know (and
mix) both Python and AW-expressions.

Thus if we wish to stick to a single language for expressing the experimental
logic (that is Python as offered by Hera) we need to drop the native AW way for
expressing loops and instead express such loops in Python. Such a scheme has
two main drawbacks:
- [fan-in](https://github.com/argoproj-labs/hera/blob/main/examples/workflows/dynamic_fanout_fanin.py)
  techniques cannot use Hera/AW syntactic "sugar" (which might not be such a
  loss given the current, as of version 5.X, notational intricacies) and they
  thus require a dedicated task to be manually written,
- because such loops are realized at AW construction stage (when the YAML files
  are generated) the pipeline topology/structure is fixed and Hera evaluation
  stage as opposed to AW running stage i.e. dynamically.

When possible (i.e. when the pipeline topology/structure is known at Hera 
evaluation stage), the expression of looping structures in Python has 
nevertheless an advantage: nested loops are much easier to express since they
do not require to 
[declare a WorkflowTemplate for the inner loop](../Workflows_In_Yaml/Failing_Or_Issues/nested-loops-issue.yml). 

## Non HERA related lessons learned

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