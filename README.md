# Check status of NSX-V Edges

This simple script checks the status of NSX-V edges and reports any redeployments or size changes as events to vRealize Operations.

## Usage
```bash
usage: nsxcheck.py [-h] [--config CONFIG] [--nsxurl NSXURL] [--nsxuser NSXUSER]
               [--nsxpassword NSXPASSWORD] [--vropsurl VROPSURL]
               [--vropsuser VROPSUSER] [--vropspassword VROPSPASSWORD]
               [--forever]

```

Configuration can be done either through a config file or directly through parameters. The ```--forever``` flag
lets the collector stay running indefintely collecting every 60 seconds. Without the flag, the collector run once and
saves the state in a temporary file. The latter mode is ideal for scheduling the script using e.g. cron or
vRealize Orchestrator.

### Configuration file format
```yaml
vrops:
  url: https://vrops.corp.local
  user: admin
  password: secret

nsx:
  url: https://nsx.corp.local
  user: admin
  password: secret
```
