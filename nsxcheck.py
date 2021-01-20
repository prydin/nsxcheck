import nsxclient
from vropsclient import VRopsClient
import time
import yaml
import sys
import argparse
import tempfile
import os
import json

parser = argparse.ArgumentParser(description='NSXcheck');
parser.add_argument('--config', help='Config file')
parser.add_argument('--nsxurl', help='The NSX manager URL')
parser.add_argument('--nsxuser', type=str, help='The NSX manager user')
parser.add_argument('--nsxpassword', help='The NSX manager password')
parser.add_argument('--vropsurl', help='The NSX manager URL')
parser.add_argument('--vropsuser', type=str, help='The NSX manager user')
parser.add_argument('--vropspassword', help='The NSX manager password')
parser.add_argument('--forever', help='Run forever', type=bool, default=False)

args = parser.parse_args()

nsxUrl = ''
nsxUser = ''
nsxPassword = ''
vropsUrl = ''
vropsUser = ''
vropsPassword = ''

# Config using file?
if args.config:
    with open(args.config) as file:
        config = yaml.full_load(file)

    nsxConf = config['nsx']
    vropsConf = config['vrops']
    nsxUrl = nsxConf['url']
    nsxUser = nsxConf['user']
    nsxPassword = nsxConf['password']

    vropsUrl = vropsConf['url']
    vropsUser = vropsConf['user']
    vropsPassword = vropsConf['password']
else:
    nsxUrl = args.nsxurl
    nsxUser = args.nsxuser
    nsxPassword = args.nsxpassword
    vropsUrl = args.vropsurl
    vropsUser = args.vropsuser
    vropsPassword = args.vropspassword

# Did we get enough config?
if not (nsxUrl and nsxUser and nsxPassword and vropsUrl and vropsUser and vropsPassword):
    print("URL, user and password must be specified for NSX and vR Ops")
    parser.print_usage()
    exit(1)



nsx = nsxclient.NSXClient(nsxUrl, nsxUser, nsxPassword)
vrops = VRopsClient(vropsUrl, vropsUser, vropsPassword)

def send_event(message, edge):
    resource_id = vrops.resource_id_by_name(edge['name'])
    vrops.push_event(resource_id, message, 'NOTIFICATION')
    print('%s - %s' % (message, edge['name']))

def run_forever():
    edge_table = {}
    period = 60 # Sample every 60 seconds

    while True:
        t0 = time.time()
        collect(edge_table)

        # Wait whatever time is left of the period
        delay = period - (time.time() - t0)
        if delay > 0:
            time.sleep(delay)


def collect(edge_table):
    remaining = set(edge_table.keys())
    edges = nsx.get_edges()
    for edge in edges['edgePage']['data']:
        key = edge['name']
        if key in edge_table:
            previous = edge_table[key]

            # Object id changed?
            if edge['objectId'] != previous['objectId']:
                send_event("Edge redeployed", edge)

            # Size changed?
            oldSize = previous['appliancesSummary']['applianceSize']
            newSize = edge['appliancesSummary']['applianceSize']
            if oldSize != newSize:
                send_event("Edge resized from %s to %s" % (oldSize, newSize), edge)

            # We've dealt with this, so remove it from the set of potentially dangling edges
            remaining.remove(key)
        edge_table[key] = edge

    # Check if we had more edges in our previous run (i.e. edges disappeared on us)
    for key in remaining:
        send_event("Edge removed", edge_table[key])
        edge_table.pop(key)


def run_once():
    dir = tempfile.gettempdir()
    p = os.path.join(dir, 'nsxstate.json')
    if os.path.exists(p):
        with open(p) as file:
            edge_table = json.load(file)
    else:
        edge_table = {}
    collect(edge_table)
    with open(p, "w") as file:
        json.dump(edge_table, file)

if args.forever:
    while True:
        try:
            run_forever()
        except KeyboardInterrupt:
            print("Aborted by operator")
            sys.exit(0)
        except Exception as e:
            print("Error occurred. Trying again in 60 seconds. Error: % s" % str(e))
            time.sleep(60)
else:
    run_once()





