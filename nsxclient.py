import requests
import json
from requests.auth import HTTPBasicAuth


class NSXClient:
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    def __init__(self, url, user, password):
        self.url = url
        self.auth = HTTPBasicAuth(user, password)

    def get_edges(self):
        r = requests.get(url=self.url + "/api/4.0/edges", verify=False, headers=self.headers,
                         auth=self.auth)
        if r.status_code != 200:
            raise Exception("HTTP Error %d: %s" % (r.status_code, r.content))
        return r.json()