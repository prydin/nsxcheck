import nsxclient
from vropsclient import VRopsClient
import time
import yaml
import sys

if len(sys.argv) != 2:
    print("Usage: nsxcheck [config file]")
    sys.exit(1)

with open(sys.argv[1]) as file:
    config = yaml.full_load(file)

nsxConf = config['nsx']
vropsConf = config['vrops']

nsx = nsxclient.NSXClient(nsxConf['url'], nsxConf['username'], nsxConf['password'])
vrops = VRopsClient(vropsConf['url'], vropsConf['username'], vropsConf['password'])

def send_event(message, edge):
    resource_id = vrops.resource_id_by_name(edge['name'])
    vrops.push_event(resource_id, message, 'NOTIFICATION')
    print('%s - %s' % (message, edge['name']))

def run():
    edge_table = {}
    period = 60 # Sample every 60 seconds

    while True:
        t0 = time.time()
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

        # Wait whatever time is left of the period
        delay = period - (time.time() - t0)
        if delay > 0:
            time.sleep(delay)

while True:
    try:
        run()
    except Exception as e:
        print("Error occurred. Trying again in 60 seconds. Error: % s" % str(e))
        time.sleep(60)





