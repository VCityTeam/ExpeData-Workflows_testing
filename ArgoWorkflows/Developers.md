# Developers additional information

<!-- TOC -->

- [Install utils](#install-utils)
- [Running the examples](#running-the-examples)
- [Running the ongoing issues/failures](#running-the-ongoing-issuesfailures)
- [Tooling](#tooling)
  - [On OSX](#on-osx)

<!-- /TOC -->

## Install utils

```bash
# Install kub eval refer to https://www.kubeval.com/installation/
brew install kubeval
```

## Running the examples

Refer to the
[cluster independent running instructions](With_CLI_Generic/Readme.md#running-the-examples)

## Running the ongoing issues/failures

Refer to the
[cluster independent running instructions](With_CLI_Generic/Readme.md#running-the-ongoing-issuesfailures)

## Tooling

### On OSX

```bash
brew install lens
```

Launch it as an app. Authenticate (SSO) either with github or google.
Declare the cluster with the "+" button that offers the `sync with files`
sub-button and point it to your `ArgoWorkflows/On_PaGoDA_cluster/pagoda_kubeconfig.yaml`
cluster configuration file.
