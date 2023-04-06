# Running the implemented Argo workflows on the PAGoDA cluster

<!-- TOC depthfrom:2 orderedlist:false depthto:4 -->

- [General note](#general-note)
- [Cluster preparation](#cluster-preparation)
  - [Retrieve your cluster credentials at the Kubernetes "level"](#retrieve-your-cluster-credentials-at-the-kubernetes-level)
  - [Retrieve your cluster credentials at the Argo server "level"](#retrieve-your-cluster-credentials-at-the-argo-server-level)
  - [Install docker on your desktop](#install-docker-on-your-desktop)
  - [Registering the container images](#registering-the-container-images)
  - [Define an argo server namespace](#define-an-argo-server-namespace)
  - [Volumes and context creation](#volumes-and-context-creation)
- [Accessing results](#accessing-results)

<!-- /TOC -->

## General note

Otherwise explicitly mentioned, all the configuration files required for
configuring/accessing/dealing-with the PAGoDA cluster should be located in this
directory (that is the directory holding this file).

## Cluster preparation

### Retrieve your cluster credentials at the Kubernetes "level"

The credentials of the Kubernetes cluster of PAGoDA platform must be retrieved
through the rancher server of the PAGoDA platform.
In order to do so, open a web browse to
<https://rancher2.pagoda.os.univ-lyon1.fr/>
and use the `Keycloak` login mode to provide your LIRIS lab credentials (the
ones defined in LIRIS'
[ldap](https://en.wikipedia.org/wiki/Lightweight_Directory_Access_Protocol)
server).

Among the (Kubernetes) clusters (pre configured by the rancher administrator
select the pagoda cluster (or pagoda-test) e.g. by opening the top-left
menu and selecting the ad-hoc entry within the `Explore Cluster` tab.

Once in the pagoda cluster page, download the `KubeConfig` file associated
to this pagoda cluster. For this use one of the buttons in the right section
of the upper row of the page and place the content e.g. in a
`pagoda_kubeconfig.yaml` file (in this current directory).

Assert you have access to the pagoda (Kubernetes) cluster with the commands

```bash
cd $(git rev-parse --show-cdup)/ArgoWorkflows/Run_on_PAGoDA
export KUBECONFIG=`pwd`/pagoda_kubeconfig.yaml     # Make it an absolute path
kubectl get nodes
```

### Retrieve your cluster credentials at the Argo (server) "level"

The credentials of the Argo server of the PAGoDA platform must also be retrieved
through the UI of the Argo server of the PAGoDA platform.
For this web browse to <https://argowf.pagoda.os.univ-lyon1.fr/> and use
the `Single Sign ON` login mode to provide your LIRIS lab credentials (just as
for the Kubernetes cluster credential, these credentials are the ones defined
in LIRIS'
[ldap](https://en.wikipedia.org/wiki/Lightweight_Directory_Access_Protocol)
server).

Once logged in, select the `User` Tab within the left icon bar and within the
`Using Your Login With The CLI` section of the page use the `Copy to clipboard`
button to retrieve your credentials and place the content e.g. in a
`pagoda_argo.bash` file.
For your convenience `pagoda_argo.bash.templ` template file is provided (in this
directory): it defines all the required environment variables to run the
workflows except for the access token values.

Optionally, within that `pagoda_argo.bash` you might consider overwriting the
definition of the `KUBECONFIG` (shell) environment variable (that is defaulted
to `/dev/null`) with the **absolute** path to the above retrieved
`pagoda_kubeconfig.yaml` file. The path needs to be absolute for `argo` based
commands to be effective even when changing directory which you can assert by
doing

Additionally, if your argo workflow project uses a namespace that is not default
`argo` namespace you should probably overwrite the `ARGO_NAMESPACE` entry
(of the `pagoda_argo.bash` file) with the name of of your specific argo project.

Once the environment variables designating/configuring your argo server are
properly defined within your `pagoda_argo.bash` shell script, then activate them
with the command

```bash
source ./pagoda_argo.bash
```

and [assert that the argo server is ready](../With_CLI_Generic/Readme.md#asserting-argo-server-is-ready)


### Install docker on your desktop

Unlike on a [Minikube cluster](../On_Minikube_cluster/Readme.md#expose-built-in-docker-command)
the PaGoDA cluster doesn't offer a docker daemon (because of the cluster sits
behind FW that imposes the usage of an
[http proxy](https://en.wikipedia.org/wiki/Proxy_server) that in turn
complicates the Dockerfile writing).

You will thus need to install [install docker on your desktop](../With_CLI_Generic/Readme.md#installing-docker-on-your-desktop).

### Registering the container images
Unlike on Minikube, PaGoDa requires the additional stage of pushing the
container images to a docker registry that is accessible (not behind some
firewall). A possible solution is to use the docker registry offered by the
PAGoDA platform itself.



### Define an argo server namespace

Refer to the platform independent commands in order to
[define an argo namespace](../With_CLI_Generic/Readme.md#defining-an-argo-server-namespace).

FIXME: when minikube is running on the desktop (for having a docker server) then
setting the context with

```bash
kubectl config set-context --current --namespace=$ARGO_NAMESPACE
```

returns
`Context "minikube" modified`.

### Volumes and context creation

```bash
cd $(git rev-parse --show-cdup)/ArgoWorkflows/Run_on_PAGoDA
# Creation of the workflow I/O placeholder (including results)
kubectl -n argo apply -f define_pvc_pagoda.yaml
# Assert volume was properly created (the name vcity-pvc comes from
# define_pvc_pagoda.yaml):
kubectl -n argo get pvc vcity-pvc
# Define cluster specific variables
kubectl -n argo apply -f define_http_proxy_configmap.yml
```

The purpose of the above `define_http_proxy_configmap.yml` "Configmap" is to
define the environment variables that are required for the usage of the http
protocol when within PAGoDA cluster hosting domain (refer e.g. to
[using Lyon1 http proxy](https://perso.liris.cnrs.fr/emmanuel.coquery/mydocs/docs/ucbl/proxy/))
allowing for the http retrieval of out-of-cluster data (e.g. with wget).

## Accessing results

One can

- either browse the results (at shell level) from within an ad-hoc container 
  with (refer to [the header](define_zombie_pod_for_PV_navigation_with_bash.yaml)
  for further details)

  ```bash
  # Create pod
  k -n argo apply -f define_zombie_pod_for_PV_navigation_with_bash.yaml
  # Assert pod was created
  k -n argo get pod vcity-pvc-ubuntu-pod
  k -n argo exec -it vcity-pvc-ubuntu-pod -- bash
  # And then `cd /vcity-data/` and navigate with bash...
  k -n argo delete -f define_zombie_pod_for_PV_navigation_with_bash.yaml
  ```

- or copy the results to the commanding desktop with the following commands

  ```bash
  k -n argo apply -f define_zombie_pod_for_PV_navigation_with_browser.yaml
  kubectl -n argo cp vcity-pvc-nginx-pod:/var/lib/www/html/junk/stage_1/2012/LYON_8EME_2012 junk
  k -n argo delete -f define_zombie_pod_for_PV_navigation_with_browser.yaml
  ```
