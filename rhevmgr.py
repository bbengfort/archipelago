#!/usr/bin/env python
# rhevmgr
# Accesses the API to manage the state of VMs on the cluster.
#
# Author:   Benjamin Bengfort <bengfort@cs.umd.edu>
# Created:  Wed Mar 29 20:53:47 2017 -0400
#
# Copyright (C) 2016 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: rhevmgr.py [] benjamin@bengfort.com $

"""
Accesses the API to manage the state of VMs on the cluster.
"""

##########################################################################
## Imports
##########################################################################

import os
import sys
import csv
import bs4
import time
import requests
import argparse

from dotenv import load_dotenv, find_dotenv
from collections import Counter


##########################################################################
## Environment
##########################################################################

# Load the dotenv file
load_dotenv(find_dotenv())

# Fetch environment variables
USERNAME = os.environ.get("RHEV_USERNAME", "")
PASSWORD = os.environ.get("RHEV_PASSWORD", "")

RHEVURL  = "https://rhevmgr.cs.umd.edu/api/vms/"

##########################################################################
## Helper Functions
##########################################################################

def hosts(fobj):
    """
    Parses the hosts file, returning a hostname, vmid pair.
    """
    for line in fobj:
        line = line.strip()
        if not line or line.startswith("#"): continue
        yield line.split()


def fetch(url, username=USERNAME, password=PASSWORD):
    """
    Performs a GET request for the given XML with basic authentication and
    the required headers, then parses the XML and returns the soup.
    """
    headers = {'Content-Type': 'application/xml'}
    resp = requests.get(url, auth=(username,password), headers=headers)
    resp.raise_for_status()

    return bs4.BeautifulSoup(resp.content, "lxml")


def action(vmid, method, data=None, username=USERNAME, password=PASSWORD):
    """
    Performs a POST request with the specified data using basic authentication
    and required headers, then parses the XML and returns the soup.
    """
    vmurl = "{}{}/{}".format(RHEVURL, vmid, method)
    data  = data or "<action />"

    headers = {'Content-Type': 'application/xml'}
    resp = requests.post(
        vmurl, data=data, auth=(username,password), headers=headers
    )
    resp.raise_for_status()

    return bs4.BeautifulSoup(resp.content, "lxml")


def pelem(elem):
    """
    Helper to extract text from a bs4 element
    """
    if elem is not None:
        return elem.text
    return ""


##########################################################################
## Commands
##########################################################################

def up(args):
    count = Counter()

    for name, vmid in hosts(args.hosts):
        # Compute the URL and fetch the soup
        try:
            soup  = action(vmid, "start", None, args.user, args.passwd)
        except Exception as e:
            count["error"] += 1
            print("{: >16}: {}".format(name, e))
            continue

        try:
            state = pelem(soup.action.status.state)
        except:
            state = "unknown"

        # Output and rate limit
        count[state] += 1
        print("{: >16}: {}".format(name, state))
        time.sleep(0.1)

    counts = ", ".join(["{} {}".format(elem[1], elem[0]) for elem in count.most_common()])
    return "{} vms sent the start command: {}".format(sum(count.values()), counts)


def down(args):
    count = Counter()

    for name, vmid in hosts(args.hosts):
        # Compute the URL and fetch the soup
        soup  = action(vmid, "stop", None, args.user, args.passwd)
        state = pelem(soup.action.status.state)

        # Output and rate limit
        count[state] += 1
        print("{: >16}: {}".format(name, state))
        time.sleep(0.1)

    counts = ", ".join(["{} {}".format(elem[1], elem[0]) for elem in count.most_common()])
    return "{} vms sent the stop command: {}".format(sum(count.values()), counts)


def status(args):
    count = Counter()

    # Get the status of each host one at a time
    for name, vmid in hosts(args.hosts):

        # Compute the URL and fetch the soup
        vmurl = "{}{}/".format(RHEVURL,vmid)
        soup  = fetch(vmurl, args.user, args.passwd)
        state = pelem(soup.vm.status.state)

        # Output and rate limit
        count[state] += 1
        print("{: >16}: {}".format(name, state))
        time.sleep(0.1)

    counts = ", ".join(["{} {}".format(elem[1], elem[0]) for elem in count.most_common()])
    return "status of {} vms: {}".format(sum(count.values()), counts)


def listvms(args):
    soup = fetch(RHEVURL, args.user, args.passwd)

    if args.xml:
        args.output.write(soup.prettify())
        return

    writer = csv.writer(args.output, delimiter="\t")
    for idx, vmelem in enumerate(soup.find_all('vm')):
        vmid = vmelem['id']
        name = pelem(vmelem.find('name'))
        descr = pelem(vmelem.find('description'))
        mem = pelem(vmelem.find('memory'))
        cpus = int(vmelem.cpu.topology['sockets']) * int(vmelem.cpu.topology['cores'])
        writer.writerow([
            name, vmid, mem, cpus, descr
        ])

    return "wrote {} vms to {}".format(idx+1, args.output.name)


##########################################################################
## Main Method
##########################################################################

if __name__ == '__main__':

    # Create the default arguments for all commands
    parent = argparse.ArgumentParser(add_help=False)
    parent_args = {
        ('-H', '--hosts'): {
            "metavar": "PATH",
            "type": argparse.FileType('r'), "default": "hosts.txt",
            "help": "specify the hosts file with nodes and IDs",
        },
        ('-U', '--user'): {
            "default": USERNAME, "type": str,
            "help": "specify the RHEV Manager username",
        },
        ('-P', '--passwd'): {
            "default": PASSWORD, "type": str,
            "help": "specify the RHEV Manager password",
        },
    }

    for args, kwargs in parent_args.iteritems():
        parent.add_argument(*args, **kwargs)


    # Create the parser
    parser = argparse.ArgumentParser(
        description="accesses the RHEV API to manage nodes on the cluster",
        epilog="see README.md for more details on usage",
        parents=[parent],
    )

    # Create the subparsers
    subparsers = parser.add_subparsers(
        title="commands", description="management commands and queries"
    )

    # Define the commands and arguments
    commands = {
        "up": {
            "description": "bring all nodes in the cluster up",
            "func": up,
            "args": {},
        },
        "down": {
            "description": "suspend all nodes in the cluster",
            "func": down,
            "args": {},
        },
        "status": {
            "description": "fetch the state of all nodes",
            "func": status,
            "args": {},
        },
        "list": {
            "description": "list the available VMs",
            "func": listvms,
            "args": {
                ("-o", "--output"): {
                    "type": argparse.FileType("w"), "default": sys.stdout,
                    "help": "specify the location to write vms to",
                },
                ("-x", "--xml"): {
                    "action": "store_true", "default": False,
                    "help": "output the entire XML response from the API",
                }
            },
        }
    }

    # Add the subparsers and define their arguments.
    for cmd, args in commands.iteritems():
        subparser = subparsers.add_parser(cmd, description=args['description'])
        for pargs, kwargs in args['args'].iteritems():
            subparser.add_argument(*pargs, **kwargs)
        subparser.set_defaults(func=args['func'])

    # Handle the input from the command line
    args = parser.parse_args()
    try:
        msg = args.func(args) or ""
        parser.exit(0, msg+"\n")
    except Exception as e:
        parser.error(str(e))
