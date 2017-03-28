# fabfile
# Fabric command definitions for Archipelago management.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Tue Mar 28 15:53:48 2017 -0400
#
# Copyright (C) 2016 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: fabfile.py [] benjamin@bengfort.com $

"""
Fabric command definitions for Archipelago management.
"""

##########################################################################
## Imports
##########################################################################

from os import path
from fabric.api import env, run, cd, parallel, settings, put, sudo


##########################################################################
## Environment
##########################################################################

# Load hosts from a private hosts file
with open('hosts.txt', 'r') as hosts:
    env.hosts = [
        host.strip()
        for host in hosts
        if host.strip() != ""
    ]

env.user = "bengfort"
env.forward_agent = True

# Project repository
repository = "git@github.com:bbengfort/hierarchical-consensus.git"

# Important paths on remote machines
workspace = "/home/bengfort/workspace/go/src/github.com/bbengfort/"
project = path.join(workspace, "hierarchical-consensus")
profile = path.join(project, '.alia_profile')
entries = "/data/alia/entries.log"


##########################################################################
## Alia Commands
##########################################################################

@parallel
def deploy():
    """
    Pull the most recent version of the repository and source the profile
    """
    with cd(project):
        run("git pull")
        run("godep restore")
        run("go install ./cmd/alia/")


@parallel
def serve():
    """
    Run the alia consensus group replica servers
    """
    raise NotImplementedError("not yet implemented")


@parallel
def shutdown():
    """
    Shutdown the alia consensus group replica servers
    """
    raise NotImplementedError("not yet implemented")


@parallel
def ingest(outpath="."):
    """
    Collect the logs from all the remotes and save them locally
    """
    local_path = path.join(outpath, "entries.%(host)s.log")
    get(entries, local_path)


##########################################################################
## Cluster Management Commands
##########################################################################

@parallel
def copyto(localpath, remotepath, sudo=False):
    """
    Copy a file from the local to the remote
    """
    put(localpath, remotepath, use_sudo=sudo)


@parallel
def aptget(*packages):
    """
    Install packages using apt-get install using sudo.
    """
    packages = " ".join(packages)
    sudo("apt-get install -y {}".format(packages))


@parallel
def hostname():
    """
    Prints out the hostname of all machines
    """
    run("uname -a")
