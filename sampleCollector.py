import requests, os, json, csv
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
SAMPLES_URL = f"https://ext-api.airthings.com/v1/locations/{os.getenv('LOCATION_ID')}/latest-samples"
HEADERS = {
    "accept": "application/json",
    "authorization": f"Bearer {os.getenv('TOKEN')}",
}

def save_data(device_name, sensor_data):
    dt = datetime.fromtimestamp(sensor_data['time'])
    year = dt.strftime("%Y")
    month = dt.strftime("%m")

    dir_path = os.path.join("data", year, month)
    os.makedirs(dir_path, exist_ok=True)
    file_path = os.path.join(dir_path, f"{month}.csv")

    file_exists = os.path.isfile(file_path)
    with open(file_path, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            #TODO: read headers from configured keys
            writer.writerow(["time", "co2", "humidity", "pm10", "pm1", "pm25", "pressure", "sla", "temp", "virusRisk", "voc"])
        writer.writerow([sensor_data['time'], sensor_data['co2'], sensor_data['humidity'], sensor_data['pm10'],
                         sensor_data['pm1'], sensor_data['pm25'], sensor_data['pressure'], sensor_data['sla'],
                         sensor_data['temp'], sensor_data['virusRisk'], sensor_data['voc']])

def process_device_data(data):
    for device in data['devices']:
        device_name = device['segment']['name']

        if device_name == "Space_1":
            continue
        
        if device['data'] is None:
            #TODO: report no device data at timestamp to .log file
            print(f"Device {device_name} has no data.")
            continue

        device_data = device['data']
        if device_data['battery'] < 10:
            #TODO: report low battery by email
            print(f"Device {device_name} has low battery: {device_data['battery']}%")

        #TODO: Prepare charts
        print(f"Saving data for {device_name}... ", end="")
        save_data(device_name, device_data)
        print(f"Done.")

        #TODO: Remove debug print
        print(device_data)
        print("\n")

def main():
    response = requests.get(SAMPLES_URL, headers=HEADERS)
    if response.ok:
        data = response.json()
        process_device_data(data)
    else:
        print(f"Request failed with status: {response.status_code}")
        print(response.json())

if __name__ == "__main__":
    main()
