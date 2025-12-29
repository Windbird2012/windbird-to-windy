import os
import requests
from datetime import datetime, timezone

# --- CONFIG ---
PIOU_ID = 2012                     # ID de ta Windbird
WINDY_API_KEY = os.environ["WINDY_API_KEY"]
STATION_ID = os.environ.get("WINDY_STATION", "0")

# --- MAIN ---
def main():
    # 1) Lire les données Pioupiou / Windbird
    r = requests.get(
        f"https://api.pioupiou.fr/v1/live/{PIOU_ID}",
        timeout=20
    )
    r.raise_for_status()
    data = r.json()

    m = data["data"]["measurements"]

    wind_kmh = float(m.get("wind_speed_avg", 0) or 0)
    gust_kmh = float(m.get("wind_speed_max", 0) or 0)
    winddir = int(m.get("wind_heading", 0) or 0)

    # 2) Conversion km/h → m/s
    wind = wind_kmh / 3.6
    gust = gust_kmh / 3.6

    # 3) Date UTC (recommandé par Windy)
    dateutc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # 4) Envoi vers Windy Stations
    url = f"https://stations.windy.com/pws/update/{WINDY_API_KEY}"
    params = {
        "station": STATION_ID,
        "wind": round(wind, 2),
        "gust": round(gust, 2),
        "winddir": winddir,
        "dateutc": dateutc,
    }

    w = requests.get(url, params=params, timeout=20)
    w.raise_for_status()

    print("✅ Données envoyées à Windy")
    print("Vent moyen:", round(wind, 2), "m/s")
    print("Rafales:", round(gust, 2), "m/s")
    print("Direction:", winddir, "°")

# --- RUN ---
if __name__ == "__main__":
    main()
