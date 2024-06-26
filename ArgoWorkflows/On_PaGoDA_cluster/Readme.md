# Running the implemented Argo workflows on the PAGoDA cluster<!-- omit from toc -->

## TOC<!-- omit from toc -->

- [General note](#general-note)
- [Cluster preparation](#cluster-preparation)
  - [Retrieve your cluster credentials at the Kubernetes "level"](#retrieve-your-cluster-credentials-at-the-kubernetes-level)
  - [Retrieve your cluster credentials at the Argo (server) "level"](#retrieve-your-cluster-credentials-at-the-argo-server-level)
  - [Install docker on your desktop](#install-docker-on-your-desktop)
  - [Registering the container images](#registering-the-container-images)
  - [Define an argo server namespace](#define-an-argo-server-namespace)
  - [Volumes and context creation](#volumes-and-context-creation)
- [Accessing results](#accessing-results)

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
kubectl get pods
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

Unlike on Minikube, PaGoDa requires the additional stage of (tagging and)
pushing the container images to a docker registry that is accessible (not
behind some firewall). A possible solution is to use the docker registry
offered by the PAGoDA platform itself.

Once the [local images are build/pulled](../With_CLI_Generic/Readme.md#buildpull-the-required-containers))
you first need to tag them with a tag of the form
`harbor.pagoda.os.univ-lyon1.fr/vcity/<MYIMAGENAME>:<MYVERSION>` prior to
pushing them to the registry. The resulting tagging commands are

```bash
docker tag vcity/collect_lyon_data harbor.pagoda.os.univ-lyon1.fr/vcity/collect_lyon_data:0.1
docker tag vcity/3duse             harbor.pagoda.os.univ-lyon1.fr/vcity/3duse:0.1
docker tag vcity/citygml2stripper  harbor.pagoda.os.univ-lyon1.fr/vcity/citygml2stripper:0.1
docker tag vcity/py3dtilers        harbor.pagoda.os.univ-lyon1.fr/vcity/py3dtilers:0.1
docker tag vcity/iphttpcheck       harbor.pagoda.os.univ-lyon1.fr/vcity/iphttpcheck:0.1
docker tag refstudycentre/scratch-base    harbor.pagoda.os.univ-lyon1.fr/vcity/refstudycentre:latest
docker tag 3dcitydb/3dcitydb-pg:13-3.1-4.1.0 harbor.pagoda.os.univ-lyon1.fr/vcity/3dcitydb-pg:13-3.1-4.1.0
docker tag 3dcitydb/impexp:4.3.0   harbor.pagoda.os.univ-lyon1.fr/vcity/impexp:4.3.0
docker tag postgres:15.2           harbor.pagoda.os.univ-lyon1.fr/vcity/postgres:15.2
```

Eventually
[`docker login`](https://docs.docker.com/engine/reference/commandline/login/)
to the PAGoDA platform docker registry (the login/password should be provided
to you by the PAGoDA admin since authentication is not yet hooked-up with the
LIRIS ldap)

```bash
docker login harbor.pagoda.os.univ-lyon1.fr/vcity --username <my-username>
```

Then push the resulting tagged images with e.g.

```bash
docker push harbor.pagoda.os.univ-lyon1.fr/vcity/collect_lyon_data:0.1
docker push harbor.pagoda.os.univ-lyon1.fr/vcity/3duse:0.1
docker push harbor.pagoda.os.univ-lyon1.fr/vcity/citygml2stripper:0.1
docker push harbor.pagoda.os.univ-lyon1.fr/vcity/py3dtilers:0.1
docker push harbor.pagoda.os.univ-lyon1.fr/vcity/iphttpcheck:0.1
docker push harbor.pagoda.os.univ-lyon1.fr/vcity/refstudycentre:latest
docker push harbor.pagoda.os.univ-lyon1.fr/vcity/3dcitydb-pg:13-3.1-4.1.0
docker push harbor.pagoda.os.univ-lyon1.fr/vcity/impexp:4.3.0
docker push harbor.pagoda.os.univ-lyon1.fr/vcity/postgres:15.2
```

Note: if you wish to list the pushed (available) images on the pagoda container
registry (as you do with a local registry with the `docker images` command) you
will alas need to use the UI and web-browse
`https://harbor.pagoda.os.univ-lyon1.fr`. Indeed it
[seems docker doesn't allow remote registry image consultation](https://stackoverflow.com/questions/28320134/how-can-i-list-all-tags-for-a-docker-image-on-a-remote-registry).

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
  cd $(git rev-parse --show-cdup)/ArgoWorkflows/On_PaGoDA_cluster
  # Create pod
  k -n argo apply -f define_zombie_pod_for_PV_navigation_with_bash.yaml
  # Assert pod was created
  k -n argo get pod vcity-pvc-ubuntu-pod
  k -n argo exec -it vcity-pvc-ubuntu-pod -- bash
  # And then `cd /vcity-data/` and navigate with bash...
  ```

  Eventually (when the work session is over), free the allocated pod

  ```bash
  k -n argo delete -f define_zombie_pod_for_PV_navigation_with_bash.yaml
  ```

- or copy the results to the commanding desktop with the following commands

  ```bash
  cd $(git rev-parse --show-cdup)/ArgoWorkflows/On_PaGoDA_cluster
  k -n argo apply -f define_zombie_pod_for_PV_navigation_with_browser.yaml
  kubectl -n argo cp vcity-pvc-nginx-pod:/var/lib/www/html/junk/stage_1/2012/LYON_8EME_2012 junk
  k -n argo delete -f define_zombie_pod_for_PV_navigation_with_browser.yaml
  ```

  When the pod deletion fails (and appears with "Terminating" status in
  `k get pods`) then forcing the deletion can be done with

  ```bash
  k delete pod vcity-pvc-ubuntu-pod --force
  ```
