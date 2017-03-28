# Archipelago

**Fabric file and environment for managing the archipelago cluster.**

## Getting Started

This repository simply hosts a simple fabric file for management commands on remote hosts in the cluster. To use it, install Fabric as follows:

```
$ pip install fabric
```

You can then run commands as follows:

```
$ fab hostname
```

And they will execute on the entire cluster.

## Basics

Run the deploy command to pull the latest version of the project:

```
$ fab deploy
```

This should run a bunch of commands on all hosts in parallel, pulling the most recent version of the repository and updating the dependencies with `godep`. The servers can all be run simultaneously as follows:

```
$ fab serve
```

This command will run the alia serve command in the background using supervisord. The replicas can then be shutdown using the shutdown command:

```
$ fab shutdown
```

Finally the data (the replicated logs) can be ingested to a local directory as follows:

```
$ fab ingest:path/to/logs
```

Note that this command will download the logs from every host, saving them with their associated host name.

## Management

There are a couple of management tasks implemented:

```
$ fab copyto:local,remote
```

Copies a file from the local path to the remote path on all hosts. If administrative permissions are required:

```
$ fab --sudo-password $PASSWORD copyto:local,remote,sudo=True
```

Finally you can apt-get install packages on all machines with:

```
$ fab --sudo-password $PASSWORD aptget:pkga,pkgb,pkgc
```

Use with care though, as this may require input from the user. 
