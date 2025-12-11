chart_labels = {
    "co2": "Stężenie dwutlenku węgla",
    "humidity": "Wilgotność",
    "pm10": "Stężenie cząsteczek PM10",
    "pm1": "Stężenie cząsteczek PM1",
    "pm25": "Stężenie cząsteczek PM2.5",
    "pressure": "Ciśnienie",
    "sla": "SLA (Service Level Agreement)",
    "temp": "Temperatura",
    "virusRisk": "Ryzyko Wirusowe",
    "voc": "Stężenie Lotnych Związków Organicznych",
}

metrics = [x for x in chart_labels.keys()]

sensor_headers = [
    "time",
    "device_name",
] + metrics
