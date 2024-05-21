# Running workflows with Hera on PaGoDA<!-- omit from toc -->

## Table of content<!-- omit from toc -->

- [Preparing the execution context](#preparing-the-execution-context)
  - [Retrieve your cluster credentials (at k8s level)](#retrieve-your-cluster-credentials-at-k8s-level)
    - [Persisting your Argo server configuration at shell level](#persisting-your-argo-server-configuration-at-shell-level)
    - [Persisting your Argo server configuration at the Python level](#persisting-your-argo-server-configuration-at-the-python-level)
  - [Further installation steps](#further-installation-steps)
- [Run the workflows](#run-the-workflows)
- [Accessing the workflow results](#accessing-the-workflow-results)
- [Developers](#developers)
  - [Concerning the levels of failure](#concerning-the-levels-of-failure)

## Preparing the execution context

### Retrieve your cluster credentials (at k8s level)

You will first need to retrieve your
[PaGoDA cluster credentials at the Kubernetes "level"](../On_PaGoDA_cluster/Readme.md#retrieve-your-cluster-credentials-at-the-kubernetes-level).
You should now have a `KUBECONFIG` variable (probably pointing to some
`../Run_on_PAGoDA/pagoda_kubeconfig.yaml` configuration file) and the
commands `kubectl get nodes` or `kubectl get pods -n argo` should be
returning some content.

Hera accesses the argo-workflows server through the k8s API (as opposed to the
dedicated argo API that is used by the argo CLI). Running an Hera script thus
requires credentials for the argo-workflows server (accessed at k8s API).

In addition to your `KUBECONFIG` credentials (
[refer e.g. here](../On_PaGoDA_cluster/Readme.md#retrieve-your-cluster-credentials-at-the-kubernetes-level))
you must also ask your cluster admin to provide you with three information

1. the URL designating the argo server
2. the (k8s level) namespace where argo-workflows stands.
3. the service account for accessing argo-workflows.

The first two items can be
[retrieved through the argo UI](../On_PaGoDA_cluster/Readme.md#retrieve-your-cluster-credentials-at-the-argo-server-level).
You are left with obtaining the name of service account, for accessing
argo-workflows, from your cluster admin.

Because each workflow that you'll launch will require the above information,
the default mechanism used by Hera is the one proposed by ArgoWorkflows that
consists in retrieving this information out of conventional environment
variables.
In order to persist that configuration information, you can either (among
other means):

- stick with environment variables that you will persist at your shell level
- use the means offered by Python, since Hera is Python based.

#### Persisting your Argo server configuration at shell level

When working with e.g. the
[`bash`](<https://en.wikipedia.org/wiki/Bash_(Unix_shell)>)
you define your environment variables in the following manner

```bash
export ARGO_SERVER=argowf.pagoda.os.univ-lyon1.fr:443
export ARGO_NAMESPACE=argo
export ARGO_SERVICE_ACCOUNT=argo-pagoda-user
export KUBECONFIG=./pagoda_kubeconfig.yaml
```

Instead you can persist those environment variables in a e.g.
`Workflows_In_Hera/hera.bash` (a default configuration template file
[`hera.bash.tmpl` is provided here](hera.bash.tmpl) is provided as an
example). Then you "import" that file into your current active shell

- either with the `export $(grep -v '^#' hera.bash | xargs)` command
- or by defining a function (in your `~/.bashrc` or `~/.bash_aliases`) of the
  form
  ```bash
  importenv() {
  set -a
  source "$1"
  set +a
  }
  ```
  and invoking it from your shell.

#### Persisting your Argo server configuration at the Python level

If you decide to use Python to persist your argo server configuration, and
because that configuration file will be parsed by the
[ConfigParser](https://docs.python.org/3/library/configparser.html)
Python library, you should use the
[so called `Shlex`](https://docs.python.org/3/library/shlex.html#module-shlex)
syntax.
A default configuration template file
[`hera.config.tmpl` is provided here](hera.config.tmpl). Customize that
file to suit your local cluster/platform and place it in the
`Workflows_In_Hera/hera.config` file.

### Further installation steps

- [Install docker on your desktop](../With_CLI_Generic/Readme.md#installing-docker-on-your-desktop) (
  [Here is why](../On_PaGoDA_cluster/Readme.md#install-docker-on-your-desktop)
  you need to do so)
- [Build the required container images](../With_CLI_Generic/Readme.md#buildpull-the-required-containers)
- [Push the container images to the (local) registry](../On_PaGoDA_cluster/Readme.md#registering-the-container-images)
- [Assert the existence of a persistent volume claim](../On_PaGoDA_cluster/Readme.md#volumes-and-context-creation). This is done at the k8s level and consists
  in checking for the existence of the ad-hoc `configmap`
- [Install HERA](../With_HERA_Generic/Readme.md#install-hera-and-its-dependencies)

## [Run the workflows](../With_HERA_Generic/Readme.md#running-workflows)

## [Accessing the workflow results](../On_PaGoDA_cluster/Readme.md#accessing-results)

## [Developers](../With_HERA_Generic/Readme.md#developers)

### Concerning the levels of failure

When a workflow submitted at Hera or AW level errors/fails/lags a key
difficulty lies in understanding the level at which the difficulty stands.
Indeed, the difficulty can be

- at HERA/AW user level (problem is in between the Hera user and some k8s
  ressource): for example a PVC was required but k8s cannot provide it, or
  an erroneous (not findable in the docker registry) container name was
  prescribed but the user (but AW waits for a container that does not exist),
- at ArgoWorkflow server level (problem lies in between the AW server and some
  k8s ressource of the server): the AW server cannot access the k8s name
  service or a network service is order to create the pods and the sub-network
  is needs to create (due e.g. to some erroneous access right). Or the AW
  server waits for a specific node (with a specific amount of memory) that is
  not available.
- at k8s level (problem is at k8s level): k8s has a dangling or sporadic node.

When a workflow (execution fails), the debugging information is scattered at
AW or k8s level. And this debugging information (quite often) remains hidden
to the HERA end user.
Here a short list of possible causes of failure

- some (workflow) pod remains blocked/idle with an `Init:0/1` status. The cause:
  as shown by the `k describe pod <pod-name>` command, the following warning
  states
  ```
  [...] Failed to create pod sandbox: rpc error [...] plugin type="calico"
  failed [...] error getting ClusterInformation: Get
  "https://10.43.0.1:443/apis/crd.projectcalico.org/v1/clusterinformations/default":
  dial tcp 10.43.0.1:443: connect: connection refused
  ```
- a workflow submitted with success at HERA level doesn't appear in AW-UI. Yet
  when looking for the "well known" (one has to know the workflow description)
  pod name with ` k get pods | grep <well-known-pod-name>` one finds
  ```bash
  NAME                           READY   STATUS      RESTARTS   AGE
  <well-known-pod-name>-11456    0/2     Error       0          41m
  ```
  that is the pod was launched but it errored (without AW logs reporting it).
