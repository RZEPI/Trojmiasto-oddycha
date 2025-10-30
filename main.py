import requests
import os
import json
from time import sleep
from datetime import datetime

LOCATION_ID = "679c2be5-f6a8-4257-b26a-3adf31db4f7b"
USER_GROUP = "9bcd8d27-c997-436a-acf3-dea7478e6bcc"
AIRTHINGS_URL = f"https://dashboard-api.airthin.gs/v1/locations/{LOCATION_ID}/spaces?userGroupId={USER_GROUP}&groupType=business"
MINUTES_SLEEP = 10

AUTH_KEY = os.environ.get("AUTH_KEY")
exit = False


def parse_space(space_dict):
    parsed_space = {}
    parsed_space["name"] = space_dict["name"]
    parsed_space["devices"] = []
    for device in space_dict["devices"]:
        device_data = {}
        device_data["name"] = device["segmentName"]
        device_values = device["currentSensorValues"]
        device_data["status"] = device.get("healthStatus", "offline")
        if device_data["status"] != "offline":
            metrics = {}
            for value in device_values:
                metric_name = value["type"]
                metric_value = value.get("value", "N/A")
                metrics[metric_name] = metric_value
            device_data["metrics"] = metrics
        parsed_space["devices"].append(device_data)

    return parsed_space


def save_data(spaces):
    now = datetime.now()
    filename = f"data_{now}.json".replace(" ", "_").replace(":", "_")
    with open(file=filename, mode="w") as f:
        f.write(json.dumps(spaces, indent=3))


def app():
    while not exit:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {AUTH_KEY}",
        }
        response = requests.get(AIRTHINGS_URL, headers=headers, verify=False)
        if response.ok:
            data = response.json()
            spaces = data["spaces"][1:]
            parsed_spaces = []
            for space in spaces:
                space_data = parse_space(space)
                parsed_spaces.append(space_data)
            save_data(parsed_spaces)
        else:
            print(f"Request failed with status: {response.status_code}")
            print(response.json())
        sleep(MINUTES_SLEEP * 60)


if __name__ == "__main__":
    app()
