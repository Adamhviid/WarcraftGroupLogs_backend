from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import requests
from urllib.parse import urlencode

from auth import get_access_token

load_dotenv()

app = Flask(__name__)
CORS(app)

if __name__ == "__main__":
    app.run()


@app.route("/")
def hello_world():
    return "Hello, World!"


@app.route("/get_character_data", methods=["POST"])
def get_character_data():

    data = request.get_json()
    name = data.get("name")
    server = data.get("server")
    region = data.get("region")
    zone = data.get("zone")

    print(name, server, region, zone)

    query = f"""
    query {{
        characterData {{
            character(name: "{name}", serverSlug: "{server}", serverRegion: "{region}") {{
                classID
                healerRankings: zoneRankings(zoneID: {zone}, role: Healer, metric: hps)
                tankRankings: zoneRankings(zoneID: {zone}, role: Tank, metric: dps)
                dpsRankings: zoneRankings(zoneID: {zone}, role: DPS, metric: dps)
            }}
        }}
    }}
    """
    response = requests.post(
        "https://sod.warcraftlogs.com/api/v2/client",
        headers={
            "Authorization": f"Bearer {get_access_token()}",
        },
        json={"query": query},
    )
    result = response.json()

    character_data = result.get("data", {}).get("characterData", {}).get("character")
    if not character_data:
        character_data = {
            "classID": 1,
            "healerRankings": {
                "bestPerformanceAverage": None,
                "medianPerformanceAverage": None,
                "rankings": [],
            },
            "tankRankings": {
                "bestPerformanceAverage": None,
                "medianPerformanceAverage": None,
                "rankings": [],
            },
            "dpsRankings": {
                "bestPerformanceAverage": None,
                "medianPerformanceAverage": None,
                "rankings": [],
            },
        }

    return jsonify(
        {
            "name": name,
            "result": character_data,
        }
    )
