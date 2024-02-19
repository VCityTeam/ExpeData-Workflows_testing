# Running workflows with Hera on PaGoDA

**TOC**
<!-- TOC -->

- [Preparing the execution context](#preparing-the-execution-context)
  - [Retrieve your cluster credentials at k8s level](#retrieve-your-cluster-credentials-at-k8s-level)
  - [Further installation steps](#further-installation-steps)
- [Run the workflows](#run-the-workflows)
  - [Accessing the workflow results](#accessing-the-workflow-results)
- [Developers](#developers)

<!-- /TOC -->

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
[retrieved through the argo UI](#retrieve-your-cluster-credentials-at-the-argo-server-level)
and correspond respectively to the `ARGO_SERVER` and the `ARGO_NAMESPACE`
environment variables.
You are left with obtaining the name of service account, for accessing 
argo-workflows, from your cluster admin.

Because each workflow that you'll launch will require the above information,
place them in an environment variables file e.g. `Workflows_In_Hera/.env` 
(a default configuration file [`.env.tmpl` is provided here](env.tmpl)):

```bash
ARGO_SERVER=argowf.pagoda.os.univ-lyon1.fr:443
ARGO_NAMESPACE=argo
ARGO_SERVICE_ACCOUNT=argo-pagoda-user
KUBECONFIG=./pagoda_kubeconfig.yaml
```

Then you "import" that file into your current shell by
- either with the `export $(xargs < .env)`
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

### [Accessing the workflow results](../On_PaGoDA_cluster/Readme.md#accessing-results)

## [Developers](../With_HERA_Generic/Readme.md#developers)