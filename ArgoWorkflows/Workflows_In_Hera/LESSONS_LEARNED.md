
### Pre and post conditions
 - on doit toujours avoir une post-condition attestant de l'echec/reussite
   ce qui implique un fichier de resultat en json ?

### Concerning the flowing of parameters
They are at least to way of flowing the workflow (run time) parameters:
- at the Hera level (that is in ArgoWorkflows): the inconvenience is that
  flowing parameter values from the initial CLI (or input file) values down to 
  the container's creation can be pretty expensive (in terms of written code).
  Not only does inputs/arguments passing syntax (`inputs=[Parameter...]`) prove
  to be both pretty verbose and sometimes cumbersome, but it also leave a 
  footprint when flown/traversing the WorkFlowTemplate declarations.
- at the python level, which has all the advantages of the python language (and
  it's packages). Yet this is not always possible for dynamic values (that
  is values only discovered at runtime) like a service pod IP number or for the
  iterated value of a loop expressed at the ArgoWorkflow level.  

Here is a set of recommendations in order to simplify your Hera code:
- constants (input parameters that have singular values and are shared by all
  the containers as opposed to multi-valued parameters that required to be
  swept) can be flown at the python level.
- input parameters that must be flown through Workflow-templates should
  either be transmitted at the Hera notational level 
  (`inputs=[Parameter...]`) (recommended) or require quite a dedicated 
  treatment (_not_ recommended). This is because any Worflow-template e.g.
  ```
  def define_some_workflow(input_parameter):
    with WorkflowTemplate(
        name="workflow-name",
        entrypoint="template-name",
    ) as w:
    [...]
```
is technically translated to become the "template-name" template within an 
ArgoWorkflows file (with a leading `kind: WorkflowTemplate` line). If the
template depends on the `input_parameter` (that will thus take different 
values) then there are in pact as many such templates as they are input 
parameter values. 
The "easy" solution is thus to have a single template while transmitting
the input_parameters values at the Hera level, that is
```
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
```.
A more cumbersome solution consists in explicitly "generating" all the 
required templates by declining their name e.g
```
  # Solution 2: mangled template names
  def define_some_workflow(input_parameter):
    template_name="template-name"+str(input_parameter)  # Name mangling
    with WorkflowTemplate(
        name="my-workflow-name",
        entrypoint=template_name,                # Mangled name used here
    ) as w:
        [...]
        with DAG(name=template_name):   # <--- note the absence of input=[] 
            [...]
```.
The inconvenient is here that the calling code is constrained to use the
same mangling scheme e.g.
```
with Workflow([...], entrypoint="main") as w:

    with DAG(name="main"):
        tasks = list()
        for param in input_parameter:
            # Mangled name but use the exact SAME mangling scheme
            mangled_template_name="template-name"+str(input_parameter)
            task_param = Task(
              name="some-task-name"+,
              template_ref=models.TemplateRef(
                  name="my-workflow-name",
                  template=mangled_template_name,   # Used here
            )
            tasks.append(task_param)
            # Then use tasks to hard-wire the required dag topology... 
        )
```
- input parameters that do _not_ require to be flown through 
  Workflow-templates should be transmitted at the python level (for the 
  above mentioned convenience reason).
- Eventually, what is dynamic (e.g. the IP number of a service pod) must
  be flown at the Hera/ArgoWorkflows lebel.
