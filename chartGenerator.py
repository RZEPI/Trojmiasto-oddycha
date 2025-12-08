import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from config import metrics
from utils import find_csv_for_date, get_df_for_date


def generate_sensor_charts(target_date: datetime = None, base_dir="data"):
    if target_date is None:
        target_date = datetime.now() - timedelta(days=1)

    csv_file_path = find_csv_for_date(target_date, base_dir)
    df = get_df_for_date(target_date, csv_file_path)

    if df is None:
        print(
            f"{datetime.now()} | Error: No data about any sensors found for {target_date} at {csv_file_path}"
        )
        return

    for device, group in df.groupby("device_name"):
        group = group.sort_values("datetime")

        for metric in metrics:
            if metric not in ["pm1", "pm10", "pm25"]:
                continue

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
