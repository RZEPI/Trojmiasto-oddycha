import smtplib, os, glob
from dotenv import load_dotenv
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from config import chart_labels
from utils import load_statuses

load_dotenv()


def send_daily_email(date: datetime = None):
    if date is None:
        date = datetime.now() - timedelta(days=1)

    sender = os.getenv("SENDER")
    recipient = os.getenv("RECIPIENT")
    subject = f"Airthings report for {date.date()}"

    msg = MIMEMultipart("related")
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = subject

    alt_part = MIMEMultipart("alternative")
    msg.attach(alt_part)

    text = "Your email client does not support HTML emails."
    alt_part.attach(MIMEText(text, "plain"))

    html = f"""
    <html>
    <body>
        <p style="font-size:1.2em; color:#777;">
            Szanowni Państwo, <br>
            poniżej zestawienie pomiarów sensorów Airthings z budynku Silk z dnia {date.date()}</b>.
        </p>
        <p style="font-size:1.2em; color:#777;">
            Statusy urządzeń:
        </p>
        <hr>
            <ul style="list-style-type:none;">
    """

    statuses = load_statuses(date)

    for device_name, device_status in statuses:
        color = "#FF5454"
        if device_status == "low battery":
            device_status = "słaba bateria"
            color = "#FF5100"
        elif device_status == "online":
            color = "#3ED557"
        html += f"<li>{device_name}: <span style='color:{color};'>{device_status}</span></li>"

    charts_dir = os.path.join("charts", str(date.date()))
    if not os.path.exists(charts_dir):
        print(f"{datetime.now()} | Error: No charts found for {date.date()}")
        return

    sensors = [
        d for d in os.listdir(charts_dir) if os.path.isdir(os.path.join(charts_dir, d))
    ]
    images_attached = {}
    for sensor in sensors:
        sensor_dir = os.path.join(charts_dir, sensor)
        chart_files = glob.glob(os.path.join(sensor_dir, "*.png"))
        html += f"<h2>Sensor: {sensor}</h2>"
        for chart_path in chart_files:
            cid = f"{sensor}_{os.path.basename(chart_path).replace('.', '_')}"
            html += f"<h3>{chart_labels.get(os.path.splitext(os.path.basename(chart_path))[0], 'N/A')}</h3>"
            html += f'<img src="cid:{cid}" style="width:100%; max-width:600px; border:1px solid #ccc;"><br><br>'
            images_attached[cid] = chart_path

    html += "<hr></body></html>"
    alt_part.attach(MIMEText(html, "html"))

    for cid, path in images_attached.items():
        with open(path, "rb") as f:
            img = MIMEImage(f.read())
            img.add_header("Content-ID", f"<{cid}>")
            img.add_header(
                "Content-Disposition", "inline", filename=os.path.basename(path)
            )
            msg.attach(img)

    with smtplib.SMTP(os.getenv("SMTP_SERVER"), os.getenv("SMTP_PORT")) as server:
        server.starttls()
        server.login(sender, os.getenv("SMTP_PASSWORD"))
        server.send_message(msg)

    print(f"{datetime.now()} | Email sent for {date.date()}")


if __name__ == "__main__":
    target_date = datetime.now()
    send_daily_email(target_date)
