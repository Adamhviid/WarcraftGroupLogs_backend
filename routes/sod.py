from flask import request, jsonify, Blueprint
from redis.exceptions import ConnectionError
import redis
import requests
import json
import os

from auth import sod_access_token

sod = Blueprint("sod", __name__)

r = redis.from_url(os.getenv("REDIS_URL"))


@sod.route("/clear_redis", methods=["POST"])
def clear_redis():
    r.flushall()
    return "OK"


@sod.route("/get_redis", methods=["GET"])
def get_redis_keys():
    keys = r.keys()
    keys = [key.decode("utf-8") for key in keys]  # type: ignore
    return jsonify(json.dumps(keys))


@sod.route("/get_character_data", methods=["POST"])
def get_character_data():
    data = request.get_json()
    name = data.get("name")
    server = data.get("server")
    region = data.get("region")
    zone = data.get("zone")

    key = f"sod:{name}:{server}:{region}:{zone}"

    try:
        character_data = r.get(key)
    except ConnectionError:
        character_data = None

    if character_data is not None:
        character_data = character_data.decode("utf-8")  # type: ignore
        return jsonify(json.loads(character_data))

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
            "Authorization": f"Bearer {sod_access_token()}",
        },
        json={"query": query},
    )
    result = response.json()
    character_data = result.get("data", {}).get("characterData", {}).get("character")
    noData = False

    if not character_data:
        noData = True
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

    finishedObject = jsonify(
        {
            "name": name,
            str(zone): {
                "result": character_data,
            },
        }
    )

    if not noData:
        r.set(key, json.dumps(finishedObject.get_json()))
        r.expire(key, 3600)

    return finishedObject
