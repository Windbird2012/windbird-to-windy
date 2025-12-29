import os
import requests
from datetime import datetime, timezone

WINDY_API_KEY = os.environ["WINDY_API_KEY"]

# Association balises Pioupiou -> stations Windy
SOURCES = [
    {"piou_id": 2012, "station": "0"},
    {"piou_id": 1415, "station": "1"},
]

def fetch_piou(piou_id):
    r = requests.get(f"https://api.pioupiou.fr/v1/live/{piou_id}", timeout=20)
    r.raise_for_status()
    return r.json()["data"]["measurements"]

def push_windy(station, wind, gust, winddir, dateutc):
    url = f"https://stations.windy.com/pws/update/{WINDY_API_KEY}"
    params = {
        "station": station,
        "wind": round(wind, 2),
        "gust": round(gust, 2),
        "winddir": winddir,
        "dateutc": dateutc,
    }
    w = requests.get(url, params=params, timeout=20)
    w.raise_for_status()

def main():
    dateutc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    for src in SOURCES:
        m = fetch_piou(src["piou_id"])

        wind_kmh = float(m.get("wind_speed_avg", 0) or 0)
        gust_kmh = float(m.get("wind_speed_max", 0) or 0)
        winddir = int(m.get("wind_heading", 0) or 0)

        wind = wind_kmh / 3.6
        gust = gust_kmh / 3.6

        push_windy(src["station"], wind, gust, winddir, dateutc)

        print(
            f"✅ PIOU {src['piou_id']} → station {src['station']} | "
            f"wind={wind:.2f} m/s gust={gust:.2f} m/s dir={winddir}°"
        )

if __name__ == "__main__":
    main()
