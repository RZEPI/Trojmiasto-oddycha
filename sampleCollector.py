import requests, os, schedule, csv, time
from emailSender import send_daily_email
from chartGenerator import generate_sensor_charts
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
            #TODO: Configurable metrics here and in chartGenerator.py
            writer.writerow(["time", "device_name", "co2", "humidity", "pm10", "pm1", "pm25", "pressure", "sla", "temp", "virusRisk", "voc"])
        writer.writerow([sensor_data['time'], device_name, sensor_data['co2'], sensor_data['humidity'], sensor_data['pm10'],
                         sensor_data['pm1'], sensor_data['pm25'], sensor_data['pressure'], sensor_data['sla'],
                         sensor_data['temp'], sensor_data['virusRisk'], sensor_data['voc']])

def process_device_data(data):
    for device in data['devices']:
        device_name = device['segment']['name']

        if device_name == "Space_1":
            continue
        
        if device['data'] is None:
            #TODO: report no device data at timestamp to .log file
            print(f"{datetime.now()} | Device {device_name} has no data.")
            continue

        device_data = device['data']
        if device_data['battery'] < 10:
            #TODO: report low battery by email
            print(f"{datetime.now()} | Device {device_name} has low battery: {device_data['battery']}%")

        print(f"{datetime.now()} | Saving data for {device_name}... ", end="")
        save_data(device_name, device_data)
        print(f"Done.")

def collect_samples():
    try:
        resp = requests.get(SAMPLES_URL, headers=HEADERS, timeout=10)
        if resp.ok:
            process_device_data(resp.json())
        else:
            print(f"{datetime.now()} | API error: {resp.status_code}")
    except Exception as e:
        print(f"{datetime.now()} | Exception during collection: {e}")

def main():
    print(f"{datetime.now()} | Starting sample collector...")
    
    schedule.every(5).minutes.do(collect_samples)
    schedule.every().day.at("08:00").do(generate_sensor_charts)
    schedule.every().day.at("08:00").do(send_daily_email)

    collect_samples() 
    while True:
        schedule.run_pending()
        time.sleep(30)

if __name__ == "__main__":
    main()
