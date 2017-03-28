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
from fabric.api import env, run, cd, parallel, settings


##########################################################################
## Environment
##########################################################################

# Load hosts from a private hosts file
with open('hosts.txt', 'r') as hosts:
    env.hosts = [
        "bengfort@{}".format(host.strip())
        for host in hosts
        if host.strip != ""
    ]

env.forward_agent = True

# Project repository
repository = "git@github.com:bbengfort/hierarchical-consensus.git"

# Important paths on remote machines
workspace = "/home/bengfort/workspace/go/src/github.com/bbengfort/"
project = path.join(workspace, "hierarchical-consensus")
profile = path.join(project, '.alia_profile')
entries = "/data/alia/entries.log"


##########################################################################
## Commands
##########################################################################

def deploy():
    """
    Pull the most recent version of the repository and source the profile
    """
    with cd(project):
        run("git pull")
        run("godep restore")
        run(". {}".format(profile))


def serve():
    """
    Run the alia consensus group replica servers
    """
    with cd(project):
        run("echo $GOPATH")


def hostname():
    """
    Prints out the hostname of all machines
    """
    run("uname -a")
