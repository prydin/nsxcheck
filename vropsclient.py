import requests
import json

import atexit


# import tools.cli as cli

class VRopsClient:
    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    url_base = ""

    token = ""

    def __init__(self, url_base, username, password):
        # Get security token
        #
        self.url_base = url_base + "/suite-api/api"
        credentials = json.dumps({"username": username, "password": password})
        result = requests.post(url=self.url_base + "/auth/token/acquire",
                               data=credentials,
                               verify=False, headers=self.headers)
        if result.status_code != 200:
            print(str(result.status_code) + " " + str(result.content))
            exit(1)
        json_data = json.loads(result.content)
        token = json_data["token"]
        self.headers["Authorization"] = "vRealizeOpsToken " + token

    def get(self, url):
        print(self.url_base + url)
        result = requests.get(url=self.url_base + url,
                              headers=self.headers,
                              verify=False)
        return result

    def post(self, url, data):
        result = requests.post(url=self.url_base + url,
                               headers=self.headers,
                               verify=False,
                               data=data)
        return result

    def resource_id_by_ip(self, ip):
        query = {
            "propertyConditions": {
                "conjunctionOperator": "OR",
                "conditions": [{
                    "key": "net:4000|ip_address",
                    "operator": "EQ",
                    "stringValue": ip,
                    "others": [],
                    "otherAttributes": {}
                }],
                "others": [],
                "otherAttributes": {}
            }
        }
        result = self.post("/resources/query", json.dumps(query))
        if result.status_code != 200:
            raise Exception("HTTP Error %d: %s" % (result.status_code, result.content))
        return json.loads(result.content)["resourceList"][0]["identifier"]


    def resource_id_by_name(self, name):
        query = {
            "name": [ name ]
        }
        result = self.post("/resources/query", json.dumps(query))
        if result.status_code != 200:
            raise Exception("HTTP Error %d: %s" % (result.status_code, result.content))
        return json.loads(result.content)["resourceList"][0]["identifier"]

    def push_event(self, resource, message, event_type):
        event = {
            "eventType": event_type,
            "resourceId": resource,
            "message": message,
            "managedExternally": True
        }
        print("Sending event: " + json.dumps(event))
        result = self.post("/events", json.dumps(event))
        if result.status_code != 200:
            raise Exception("HTTP Error %d: %s" % (result.status_code, result.content))
        print(result)
