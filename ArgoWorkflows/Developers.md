# Developers additional information

<!-- TOC -->

- [Install utils](#install-utils)
- [Running the examples](#running-the-examples)
- [Running the ongoing issues/failures](#running-the-ongoing-issuesfailures)
- [Debugging database related Containers](#debugging-database-related-containers)
  - [Learning with postgres](#learning-with-postgres)
  - [Improving on 3DCityDB](#improving-on-3dcitydb)
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

## Debugging database related Containers

### Learning with postgres
In order to get acquainted with the `postgres` database container, one can 
consider a simpler context than the one of Hera. We might first explore things
at the docker-desktop level (as opposed to a k8s environment) which boils down
to the following commands

```bash
docker run --mount type=bind,source="$(pwd)"/citydb-lyon-2012,target=/var/lib/postgresql/data -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:13
docker ps  # Should yield en new entry with e.g. 0.0.0.0:5432->5432/tcp
lsof -i -P | grep -i "listen" | grep 5432   # On Un*x
psql -l -p 5432 -h 134.214.143.170 -U postgres -W -d citydb-lyon-2012
```

In case you get a message of the form
```bash
no pg_hba.conf entry for host "172.17.0.1", user "postgres", database "postgres"
```
you might wish to edit the `citydb-lyon-2012/pg_hba.conf` file and place
a line (if not already there) of the form

```bash             
host all all 127.17.0.1/32 trust
```

and then relaunch docker container and probe it again with

```bash
psql -l -p 5432 -h 134.214.143.170 -U postgres -W -d citydb-lyon-2012
```

The next snag might be error messages of the form
```bash
psql: error: connection to server at "134.214.143.170", port 5432 failed: Connection refused
```

for which you might inquire for the possible presence of a local firewall.

### Improving on 3DCityDB
In order to debug/play-with a 3DCityDB server in a local context
```bash
docker run --mount type=bind,source=`pwd`/citydb-lyon-2012,target=/var/lib/postgresql/data -e POSTGRES_PASSWORD=postgres -e POSTGRES_USER=postgres -e SRID=3946 -e POSTGRES_DB=citydb-lyon-2012 -p 5432:5432 3dcitydb/3dcitydb-pg:13-3.1-4.1.
docker exec -it 8837df0fcb7c /usr/lib/postgresql/13/bin/psql -U postgres -W -d citydb-lyon-2012 -c "SELECT * FROM citydb.building"
```

## Tooling

### On OSX

```bash
brew install --cask openlens
```

or alternatively `brew install lens`.

Launch it as an app. Authenticate (SSO) either with github or google.
Declare the cluster with the "+" button that offers the `sync with files`
sub-button and point it to your `ArgoWorkflows/On_PaGoDA_cluster/pagoda_kubeconfig.yaml`
cluster configuration file.
