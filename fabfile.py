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

from fabric.api import env, run, parallel


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

##########################################################################
## Commands
##########################################################################

def hostname():
    """
    Prints out the hostname of all machines
    """
    run("uname -a")
