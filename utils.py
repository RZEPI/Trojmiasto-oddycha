import os, csv
from datetime import datetime

import pandas as pd

from config import polish_month_names


def get_date_parts_str(date: datetime = None):
    if date is None:
        date = datetime.now()

    year = date.strftime("%Y")
    month = date.strftime("%m")
    return year, month


def save_data_csv(file_path, headers, data):
    file_exists = os.path.isfile(file_path)
    with open(file_path, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(headers)

        writer.writerow(data)


def find_csv_for_date(target_date: datetime, base_dir: str, suffix: str = ""):
    year, month = get_date_parts_str(target_date)
    csv_path = os.path.join(base_dir, year, f"{month}{suffix}.csv")
    if not os.path.exists(csv_path):
        print(f"{datetime.now()} | Error: No CSV found for {target_date} at {csv_path}")
    return csv_path


def get_df_for_date(target_date: datetime, csv_file_path: str):
    df = pd.read_csv(csv_file_path)

    df["datetime"] = pd.to_datetime(df["time"], unit="s")
    df["date"] = df["datetime"].dt.date

    df = df[df["date"] == target_date.date()]
    if df.empty:
        print(f"{datetime.now()} | Error: No data found for {target_date.date()}")
        return
    return df


def load_statuses(target_date: datetime):
    statuses = []
    file_path = find_csv_for_date(target_date, base_dir="data", suffix="_status")
    df = get_df_for_date(target_date, file_path)
    df = df.drop(["time", "datetime", "date"], axis=1)

    if not df.empty:
        headers = df.columns.tolist()
        for device_name in headers:
            statuses.append((device_name, df[device_name].iloc[-1]))
    return statuses


def month_number_to_polish_name(month_number):
    return polish_month_names[month_number - 1]
