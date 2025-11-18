import requests, os, schedule, csv, time, json, functools
from emailSender import send_air_quality_email, send_statuses_email
from chartGenerator import generate_sensor_charts
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
SAMPLES_URL = f"https://ext-api.airthings.com/v1/locations/{os.getenv('LOCATION_ID')}/latest-samples"
AT_USERNAME = os.getenv("AIRTHINGS_USERNAME")
AT_PASSWORD = os.getenv("AIRTHINGS_PASSWORD")
AUTH_URL = "https://accounts-api.airthings.com/v1/token"
HEADERS = {
    "Content-Type": "application/json",
}


def save_data(device_name, sensor_data):
    dt = datetime.fromtimestamp(sensor_data.get("time", datetime.now().timestamp()))
    year = dt.strftime("%Y")
    month = dt.strftime("%m")

    dir_path = os.path.join("data", year)
    os.makedirs(dir_path, exist_ok=True)
    file_path = os.path.join(dir_path, f"{month}.csv")

    file_exists = os.path.isfile(file_path)
    with open(file_path, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            # TODO: Configurable metrics here and in chartGenerator.py
            writer.writerow(
                [
                    "time",
                    "device_name",
                    "co2",
                    "humidity",
                    "pm10",
                    "pm1",
                    "pm25",
                    "pressure",
                    "sla",
                    "temp",
                    "virusRisk",
                    "voc",
                ]
            )
        writer.writerow(
            [
                sensor_data.get("time", datetime.now().timestamp()),
                device_name,
                sensor_data.get("co2", 0),
                sensor_data.get("humidity", 0),
                sensor_data.get("pm10", 0),
                sensor_data.get("pm1", 0),
                sensor_data.get("pm25", 0),
                sensor_data.get("pressure", 0),
                sensor_data.get("sla", 0),
                sensor_data.get("temp", 0),
                sensor_data.get("virusRisk", 0),
                sensor_data.get("voc", 0),
            ]
        )


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
        save_data(device_name, device_data)
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
    return sorted(device_statuses, key=lambda key: key[0])


def auth():
    payload = {
        "client_id": "accounts",
        "grant_type": "password",
        "password": AT_PASSWORD,
        "username": AT_USERNAME,
    }

    response = requests.post(
        url=AUTH_URL, data=json.dumps(payload), headers=HEADERS, verify=False
    )
    if response.ok:
        return response.json()["access_token"]

    raise Exception(
        f"Authentication failed with status code {response.status_code} - {response.content}, try again later"
    )


def collect_samples(token, process_data_fnc, retry=True):
    try:
        sample_headers = {**HEADERS, "authorization": f"Bearer {token}"}

        resp = requests.get(SAMPLES_URL, headers=sample_headers, timeout=10)
        if resp.ok:
            return process_data_fnc(resp.json())

        if resp.status_code == 401 and retry:
            print(f"{datetime.now()} | Token has expired, retrying to authenticate")
            token = auth()
            collect_samples(token, process_data_fnc, False)
        elif not resp.ok:
            print(f"{datetime.now()} | Request failed with status {resp.status_code}")
    except Exception as e:
        print(f"{datetime.now()} | Exception during collection: {e}")


def send_device_statuses(token):
    try:
        device_statuses = collect_samples(token, process_device_statuses)
        send_statuses_email(device_statuses)
    except Exception as e:
        print(f"{datetime.now()} | Exception during sending statuses of devices: {e}")


def main():
    print(f"{datetime.now()} | Starting sample collector...")

    try:
        token = auth()
        schedule.every(5).minutes.do(
            functools.partial(collect_samples, token, process_device_data)
        )
        schedule.every().day.at("08:00").do(
            functools.partial(send_device_statuses, token)
        )
        schedule.every().day.at("08:00").do(generate_sensor_charts)
        schedule.every().day.at("08:00").do(send_air_quality_email)

        while True:
            schedule.run_pending()
            time.sleep(30)
    except Exception as e:
        print(f"{datetime.now()} | Exception: {e}\nExiting.")


if __name__ == "__main__":
    main()
