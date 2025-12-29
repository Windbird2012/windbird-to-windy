import os
import requests

WINDY_API_KEY = os.environ["WINDY_API_KEY"]

SOURCES = [
    {"piou_id": 2012, "station": "0"},
    {"piou_id": 1415, "station": "1"},
]

def fetch_piou(piou_id):
    print(f"🔍 Lecture Pioupiou ID {piou_id}")
    r = requests.get(f"https://api.pioupiou.fr/v1/live/{piou_id}", timeout=20)
    r.raise_for_status()
    data = r.json()["data"]["measurements"]
    print(f"📥 Données brutes {piou_id} :", data)
    return data

def push_windy(station, wind, gust, winddir, dateutc):
    params = {
        "station": station,
        "wind": round(wind, 2),
        "gust": round(gust, 2),
        "winddir": winddir,
        "dateutc": dateutc,
    }

    print(f"📤 Envoi vers Windy (station {station}) :", params)

    url = f"https://stations.windy.com/pws/update/{WINDY_API_KEY}"
    w = requests.get(url, params=params, timeout=20)
    w.raise_for_status()

    print(f"✅ Windy OK pour station {station} (HTTP {w.status_code})")

def main():
    for src in SOURCES:
        m = fetch_piou(src["piou_id"])

        # On utilise l'heure réelle de mesure Pioupiou (meilleur si le cron dérive)
        dateutc = m.get("date")
        print(f"🕒 Date UTC envoyée (piou {src['piou_id']}) :", dateutc)

        wind_kmh = float(m.get("wind_speed_avg", 0) or 0)
        gust_kmh = float(m.get("wind_speed_max", 0) or 0)
        winddir = int(m.get("wind_heading", 0) or 0)

        wind = wind_kmh / 3.6
        gust = gust_kmh / 3.6

        print(
            f"🧮 Calculs {src['piou_id']} | "
            f"wind={wind:.2f} m/s gust={gust:.2f} m/s dir={winddir}°"
        )

        push_windy(src["station"], wind, gust, winddir, dateutc)

if __name__ == "__main__":
    main()
