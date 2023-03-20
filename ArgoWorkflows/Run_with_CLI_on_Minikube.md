# Running the implemented Argo workflows on a desktop with Minikube

<!-- TOC -->

- [Preparing the execution context](#preparing-the-execution-context)
- [Running the workflows](#running-the-workflows)
- [Troubleshooting](#troubleshooting)

<!-- /TOC -->

## Preparing the execution context

- [Prepare the Minikube cluster](On_Minikube_cluster/Readme.md#cluster-preparation)
- [Assert that the Argo server is operational](With_CLI_Generic/Readme.md#asserting-argo-server-is-ready)
- [Build the required container images](With_CLI_Generic/Readme.md#build-the-required-containers)
  (this stage [requires docker](On_Minikube_cluster/Readme.md#expose-built-in-docker-command))
- [Populate the workflow "library" with workflowTemplates](With_CLI_Generic/Readme.md#populate-the-workflow-library-with-workflowtemplates).

## Running the workflows

Hopefully workflow submission commands are cluster independent. Apply them
by following
[those instructions](With_CLI_Generic/Readme.md#running-the-workflows)

---

## Troubleshooting

First try troubleshooting with
[cluster independent troubleshooting notes](With_CLI_Generic/Readme.md#basic-troubleshooting)

In addition, you might try [Minikube's specific troubleshooting nodes](On_Minikube_cluster/Readme.md#troubleshooting-on-the-minikube-cluster).
