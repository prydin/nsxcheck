# Check status of NSX-V Edges

This simple script checks the status of NSX-V edges and reports any redeployments or size changes as events to vRealize Operations.

## Usage
```bash
python nsxcheck.py [path to config file]
```

### Configuration file format
```yaml
vrops:
  url: https://vrops.corp.local
  username: admin
  password: secret

nsx:
  url: https://nsx.corp.local
  username: admin
  password: secret
```
