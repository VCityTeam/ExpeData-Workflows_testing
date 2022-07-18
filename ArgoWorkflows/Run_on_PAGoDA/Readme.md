# Running the implemented Argo workflows on the PAGoDA cluster

**Page index**
<!-- vscode-markdown-toc -->
* [General note](#Generalnote)
* [Cluster preparation](#Clusterpreparation)
  * [Retrieve your cluster credentials at the Kubernetes "level"](#RetrieveyourclustercredentialsattheKuberneteslevel)
  * [Retrieve your cluster credentials at the Argo (server) "level"](#RetrieveyourclustercredentialsattheArgoserverlevel)
  * [Build the container images and push them to the PAGoDA registry](#BuildthecontainerimagesandpushthemtothePAGoDAregistry)
  * [Define an argo server namespace](#Defineanargoservernamespace)
  * [Volumes and context creation](#Volumesandcontextcreation)
* [Running the workflows](#Runningtheworkflows)
  * [Running the workflow stage by stage: single vintage version](#Runningtheworkflowstagebystage:singlevintageversion)
  * [Running the full workflow](#Runningthefullworkflow)
  * [Running the full workflow with loop in loop](#Runningthefullworkflowwithloopinloop)
* [Accessing the results](#Accessingtheresults)

<!-- vscode-markdown-toc-config
	numbering=false
	autoSave=true
	/vscode-markdown-toc-config -->
<!-- /vscode-markdown-toc -->

## <a name='Generalnote'></a>General note

Otherwise explicitly mentioned, all the configuration files required for running
the numerical experiment on the PAGoDA cluster should be located in the
`ArgoWorkflows/Run_on_PAGoDA/` sub-directory.

## <a name='Clusterpreparation'></a>Cluster preparation

### <a name='RetrieveyourclustercredentialsattheKuberneteslevel'></a>Retrieve your cluster credentials at the Kubernetes "level"

The credentials of the Kubernetes cluster of PAGoDA platform must be retrieved
through the rancher server of the PAGoDA platform.
In order to do so, open a web browse to
<https://rancher.pagoda.os.univ-lyon1.fr/>
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
`pagoda_kubeconfig.yaml` file.

Assert you have access to the pagoda (Kubernetes) cluster with the commands

```bash
export KUBECONFIG=pagoda_kubeconfig.yaml
kubectl get nodes
```

### <a name='RetrieveyourclustercredentialsattheArgoserverlevel'></a>Retrieve your cluster credentials at the Argo (server) "level"

The credentials of the Argo server of the PAGoDA platform must also be retrieved
through the UI of the Argo server of the PAGoDA platform.
For this web browse to <https://argoworkflows.pagoda.os.univ-lyon1.fr/> and use
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
to `/dev/null`) with the path to the above retrieved `pagoda_kubeconfig.yaml`
file.

Additionally, if your argo workflow project uses a namespace that is not default
`argo` namespace you should probably overwrite the `ARGO_NAMESPACE` entry
(of the `pagoda_argo.bash` file) with the name of of your specific argo project.

Once the environment variables designating/configuring your argo server are
properly defined within your `pagoda_argo.bash` shell script, then activate them
with the command

```bash
source ./pagoda_argo.bash
```

and [assert that the argo server is ready](../Run_on_Generic/Readme.md#anchor-assert-argo-server-is-ready)

### <a name='BuildthecontainerimagesandpushthemtothePAGoDAregistry'></a>Build the container images and push them to the PAGoDA registry

<a name="anchor-pagoda-building-containers"></a>

Providing the container images to the argo server is a two step process

1. build the container images
2. push the resulting images to an image registry that is accessible to
   the argo server.  

For the current stage of development of PAGoDA, both steps will make use of the
`docker` command : what is here needed are both docker-CLI and its
"docker-daemon" (server) counterpart.
For this you can

* either install [docker-desktop](https://www.docker.com/products/docker-desktop/)
  (that installs both the docker-CLI and the docker-daemon),
* or [install docker-cli and "point it" to minikube](https://minikube.sigs.k8s.io/docs/tutorials/docker_desktop_replacement/).
  **Warning**: if you happen to use `minikube` to provide you with the `docker`
  command then notice that `minikube` will modify the kubernetes configuration
  file (pointed by the `KUBECONFIG` environment variable) in order to add its
  own entry that will become the new default.
  After installing `minikube`, you might thus assert
  [you are using the proper kubernetes cluster](../Run_on_Generic/Readme.md#anchor-generic-troubleshooting-check-cluster-used)

Once the docker command is available (try using `docker ps`), you can first
proceed with
[building of the required container images](../Run_on_Generic/Readme.md#anchor-build-containers).

Then tag the local image you wish to push with the a tag of the form `harbor.pagoda.os.univ-lyon1.fr/vcity/<MYIMAGENAME>:<MYVERSION>`.
The resulting tagging commands are then

```bash
docker tag vcity/collect_lyon_data harbor.pagoda.os.univ-lyon1.fr/vcity/collect_lyon_data:0.1
docker tag vcity/3duse             harbor.pagoda.os.univ-lyon1.fr/vcity/3duse:0.1
docker tag vcity/citygml2stripper  harbor.pagoda.os.univ-lyon1.fr/vcity/citygml2stripper:0.1
docker tag vcity/py3dtilers        harbor.pagoda.os.univ-lyon1.fr/vcity/py3dtilers:0.1
docker tag refstudycentre/scratch-base      harbor.pagoda.os.univ-lyon1.fr/vcity/refstudycentre:latest
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
docker push harbor.pagoda.os.univ-lyon1.fr/vcity/refstudycentre:latest
```

### <a name='Defineanargoservernamespace'></a>Define an argo server namespace

Refer to the platform independent commands in order to
[define an argo namespace](../Run_on_Generic/Readme.md#anchor-define-argo-namespace).

FIXME: when minikube is running on the desktop (for having a docker server) then
setting the context with

```bash
kubectl config set-context --current --namespace=$ARGO_NAMESPACE
```

returns
`Context "minikube" modified`.

### <a name='Volumesandcontextcreation'></a>Volumes and context creation

```bash
# Creation of the workflow I/O placeholder (including results)
kubectl -n argo create -f define_pvc_pagoda.yaml
# Define cluster specific variables
kubectl -n argo create -f define_http_proxy_configmap.yml
```

The purpose of the above `define_http_proxy_configmap.yml` "Configmap" is to
define the environment variables that are required for the usage of the http
protocol when within PAGoDA cluster hosting domain (refer e.g. to
[using Lyon1 http proxy](https://perso.liris.cnrs.fr/emmanuel.coquery/mydocs/docs/ucbl/proxy/))
allowing for the http retrieval of out-of-cluster data (e.g. with wget).

---

## <a name='Runningtheworkflows'></a>Running the workflows

Alas workflow submission commands are not cluster independent (they should be
[those instructions](../Run_on_Generic/Readme.md#anchor-running-the-workflows)).
This is because (for some type of information) the cluster context needs to
be handled over through CLI parameters.
FIXME: documentent that we cannot use a `--parameter-file context.yaml` because
`argo submit` only accepts a single parameter file and we already provide the
input parameters. Also document that the registry host-name can not be passed
through a Configmap (and why this cannot be).

### <a name='Runningtheworkflowstagebystage:singlevintageversion'></a>Running the workflow stage by stage: single vintage version

Alas (refer to the above FIXME) the
[generic stage by stage instruction](../Run_on_Generic/Readme.md#anchor-running-the-workflows-stage-by-stage)
do not work as is on PAGoDA.

For the time the following submissions should be effective

```bash
cd $(git rev-parse --show-cdup)/ArgoWorkflows
# Following environment variable already defined in Run_on_PAGoDA/pagoda_argo.bash
export KUBE_DOCKER_REGISTRY=dockerRegistryHost=harbor.pagoda.os.univ-lyon1.fr/

# Proceed with the run of each sub-workflows (of the full workflow)
argo submit --watch --log just-collect.yml --parameter-file input-2012-tiny-no_db.yaml -p ${KUBE_DOCKER_REGISTRY}
# The above results should be in the `junk/stage_1/` sub-directory
argo submit --watch --log just-split.yml   --parameter-file input-2012-tiny-no_db.yaml -p ${KUBE_DOCKER_REGISTRY}
# The above results should be in the `junk/stage_2/` sub-directory
argo submit --watch --log just-strip.yml   --parameter-file input-2012-tiny-no_db.yaml -p ${KUBE_DOCKER_REGISTRY}
# The above results should be in the `junk/stage_3/` sub-directory
argo submit --watch --log just-import-to-3dcitydb-and-dump.yml --parameter-file input-2012-tiny-import_dump.yaml
# The above results should be in the `junk/stage_4/` sub-directory
# The purpose of following workflow is to assert that above db dump was correct
argo submit --watch --log just-load-dump.yml       --parameter-file input-2012-tiny-import_dump.yaml
argo submit --watch --log just-compute-tileset.yml --parameter-file input-2012-tiny-import_dump.yaml  -p ${KUBE_DOCKER_REGISTRY}
# The resulting tileset should be located in the `junk/stage_5/` sub-directory
```

### <a name='Runningthefullworkflow'></a>Running the full workflow

```bash
argo submit --watch --log full-workflow.yml --parameter-file input-2012-tiny-import_no_dump.yaml -p ${KUBE_DOCKER_REGISTRY}
```

An example with parallel steps

```bash
argo submit --watch --log full-workflow.yml --parameter-file input-2012-small-import_no_dump.yaml -p ${KUBE_DOCKER_REGISTRY}
```

### <a name='Runningthefullworkflowwithloopinloop'></a>Running the full workflow with loop in loop

The above workflows (depending on their input) are looping on their `boroughs`
input. The following ones are loop-in-looping on their vintages (outside loop)
and their boroughs (inside loop).

```bash
argo submit --watch --log just-prepare-vintages-boroughs.yml --parameter-file input-loop-in-loop-tiny.yaml -p ${KUBE_DOCKER_REGISTRY}
```

---

## <a name='Accessingtheresults'></a>Accessing the results

One can

* either browse the results (at shell level) from within an ad-hoc
container with

  ```bash
  k create -f define_zombie_pod_for_PV_navigation.yaml
  k exec -it vcity-pvc-nginx-pod  -n argo -- bash
  ```

* or copy the results to the commanding desktop with the following command

  ```bash
  kubectl cp vcity-pvc-nginx-pod:/var/lib/www/html/junk/stage_1/2012/LYON_8EME_2012 junk
  ```
