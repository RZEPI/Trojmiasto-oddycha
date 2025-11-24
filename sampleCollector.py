import requests, os, schedule, csv, time, json, functools
from emailSender import send_daily_email
from chartGenerator import generate_sensor_charts
from dotenv import load_dotenv
from datetime import datetime
from config import metrics, sensor_headers
from utils import get_date_parts_str, save_data_csv


load_dotenv()
SAMPLES_URL = f"https://ext-api.airthings.com/v1/locations/{os.getenv('LOCATION_ID')}/latest-samples"
AUTH_URL = "https://accounts-api.airthings.com/v1/token"
HEADERS_BASE = {
    "Content-Type": "application/json",
}

SEND_TIME = "08:00"


def save_sensor_data(device_name, sensor_data):
    date = datetime.fromtimestamp(sensor_data.get("time", datetime.now().timestamp()))
    year, month = get_date_parts_str(date)

    dir_path = os.path.join("data", year)
    os.makedirs(dir_path, exist_ok=True)
    file_path = os.path.join(dir_path, f"{month}.csv")

    sensor_row = [
        sensor_data.get("time", datetime.now().timestamp()),
        device_name,
    ]

    for metric in metrics:
        sensor_row.append(sensor_data.get(metric, 0))

    save_data_csv(file_path, sensor_headers, sensor_row)


def save_device_statuses(statuses):
    year, month = get_date_parts_str()

    dir_path = os.path.join("data", year)
    os.makedirs(dir_path, exist_ok=True)
    file_path = os.path.join(dir_path, f"{month}_status.csv")

    headers = ["time"]
    row = [int(datetime.now().timestamp())]
    for device_name, device_status in statuses:
        headers.append(device_name)
        row.append(device_status)

    save_data_csv(file_path, headers, row)


def process_device_data(data):
    for device in data["devices"]:
        device_name = device["segment"]["name"]

        if device_name == "Space_1":
            continue

        if device["data"] is None:
            # TODO: report no device data at timestamp to .log file
            print(f"{datetime.now()} | Device {device_name} has no data.")
            continue

        device_data = device["data"]
        if device_data["battery"] == 0:
            print(f"{datetime.now()} | Device {device_name} is offline, skipping.")
            continue
        if device_data["battery"] < 10:
            print(
                f"{datetime.now()} | Device {device_name} has low battery: {device_data['battery']}%"
            )

        print(f"{datetime.now()} | Saving data for {device_name}... ", end="")
        save_sensor_data(device_name, device_data)
        print(f"Done.")


def process_device_statuses(data):
    device_statuses = []
    for device in data["devices"]:
        device_name = device["segment"]["name"]
        if device_name == "Space_1":
            continue

        battery_state = device["data"].get("battery", 0)
        device_state = "online"
        if battery_state <= 0:
            device_state = "offline"
        elif battery_state <= 10:
            device_state = "low battery"
        device_statuses.append((device_name, device_state))
    sorted_statuses = sorted(device_statuses, key=lambda key: key[0])
    save_device_statuses(sorted_statuses)


def auth():
    payload = {
        "grant_type":"client_credentials",
        "client_id":f"{os.getenv('CLIENT_ID')}",
        "client_secret":f"{os.getenv('CLIENT_SECRET')}",
        "scope": ["read:device"]
    }

    response = requests.post(
        url=AUTH_URL,
        data=json.dumps(payload),
        headers=HEADERS_BASE,
        timeout=10,
    )
    if response.ok:
        return response.json()["access_token"]

    raise Exception(
        f"Authentication failed with status code {response.status_code} - {response.content}, try again later"
    )


def collect_samples(process_data_fnc, retry=True):
    try:
        global token
        sample_headers = {**HEADERS_BASE, "authorization": f"Bearer {token}"}

        resp = requests.get(SAMPLES_URL, headers=sample_headers, timeout=10)
        if resp.ok:
            return process_data_fnc(resp.json())

        if resp.status_code == 401 and retry:
            print(f"{datetime.now()} | Token has expired, retrying to authenticate")
            token = auth()
            collect_samples(process_data_fnc, False)
        elif not resp.ok:
            print(f"{datetime.now()} | Request failed with status {resp.status_code}")
    except Exception as e:
        print(f"{datetime.now()} | Exception during collection: {e}")


def main():
    print(f"{datetime.now()} | Starting sample collector...")

    global token
    if token is None:
        token = auth()

    collect_samples(process_device_statuses)

    try:
        schedule.every(5).minutes.do(
            functools.partial(collect_samples, process_device_data)
        )
        schedule.every().day.at(SEND_TIME).do(
            functools.partial(collect_samples, process_device_statuses)
        )
        schedule.every().day.at(SEND_TIME).do(generate_sensor_charts)
        schedule.every().day.at(SEND_TIME).do(send_daily_email)

        while True:
            schedule.run_pending()
            time.sleep(30)
    except Exception as e:
        print(f"{datetime.now()} | Exception: {e}\nExiting.")


if __name__ == "__main__":
    token = None
    main()
