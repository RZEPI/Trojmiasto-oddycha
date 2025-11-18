import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta


def find_csv_for_date(target_date: datetime, base_dir: str):
    year = target_date.strftime("%Y")
    month = target_date.strftime("%m")
    csv_path = os.path.join(base_dir, year, f"{month}.csv")
    if not os.path.exists(csv_path):
        print(f"{datetime.now()} | Error: No CSV found for {target_date} at {csv_path}")
    return csv_path


def generate_sensor_charts(target_date: datetime = None, base_dir="data"):
    if target_date is None:
        target_date = datetime.now() - timedelta(days=1)

    csv_file_path = find_csv_for_date(target_date, base_dir)
    df = pd.read_csv(csv_file_path)

    df["datetime"] = pd.to_datetime(df["time"], unit="s")
    df["date"] = df["datetime"].dt.date

    df = df[df["date"] == target_date.date()]
    if df.empty:
        print(f"{datetime.now()} | Error: No data found for {target_date.date()}")
        return

    metrics = [
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
    for device, group in df.groupby("device_name"):
        group = group.sort_values("datetime")

        for metric in metrics:
            plt.figure(figsize=(10, 5))
            plt.plot(
                group["datetime"],
                group[metric],
                marker="o",
                linestyle="-",
                label=metric,
            )
            plt.title(f"{metric.upper()} for {device} on {target_date.date()}")
            plt.xlabel("Time")
            plt.ylabel(metric.upper())
            plt.grid(True)
            plt.legend()

            # Format time on x-axis
            ax = plt.gca()
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
            ax.xaxis.set_major_locator(mdates.AutoDateLocator())
            plt.gcf().autofmt_xdate()

            # Save chart
            output_dir = os.path.join("charts", str(target_date.date()), device)
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"{metric}.png")
            plt.tight_layout()
            plt.savefig(output_path)
            plt.close()
            print(f"Chart saved: {output_path}")


if __name__ == "__main__":
    target_date = datetime.now()
    generate_sensor_charts(target_date)
