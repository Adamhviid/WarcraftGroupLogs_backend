from flask import request, jsonify, Blueprint
from redis.exceptions import ConnectionError
import redis
import requests
import json
import os

from auth import get_access_token

api = Blueprint("api", __name__)

r = redis.from_url(os.getenv("REDIS_URL"))

@api.route("/clear_redis", methods=["GET"])
def clear_redis():
    r.flushall()
    return "OK"


@api.route("/get_redis", methods=["GET"])
def get_redis_keys():
    keys = r.keys()
    keys = [key.decode("utf-8") for key in keys]  
    return jsonify(json.dumps(keys))


@api.route("/get_character_data", methods=["POST"])
def get_character_data():
    data = request.get_json()
    name = data.get("name")
    version = data.get("version")
    server = data.get("server")
    region = data.get("region")
    zone = data.get("zone")
    difficulty = data.get("difficulty")

    key = f"{version}:{region}:{server}:{zone}:{difficulty}:{name}".encode("utf-8")

    try:
        character_data = r.get(key)
    except ConnectionError:
        character_data = None

    if character_data is not None:
        character_data = character_data.decode("utf-8")
        return jsonify(json.loads(character_data))

    query = f"""
    query {{
        characterData {{
            character(name: "{name}", serverSlug: "{server}", serverRegion: "{region}") {{
                classID
                healerRankings: zoneRankings(zoneID: {zone}, difficulty: {difficulty}, role: Healer, metric: hps)
                tankRankings: zoneRankings(zoneID: {zone}, difficulty: {difficulty}, role: Tank, metric: dps)
                dpsRankings: zoneRankings(zoneID: {zone}, difficulty: {difficulty}, role: DPS, metric: dps)
            }}
        }}
    }}
    """

    formatted_url = (
        "https://www.warcraftlogs.com"
        if version == "retail"
        else f"https://{version}.warcraftlogs.com"
    )
    
    response = requests.post(
        formatted_url + "/api/v2/client",
        headers={
            "Authorization": f"Bearer {get_access_token(formatted_url)}",
        },
        json={"query": query},
    )

    result = response.json()
    character_data = result.get("data", {}).get("characterData", {}).get("character")
    check_if_no_data = False

    if not character_data:
        check_if_no_data = True
        character_data = {
            "classID": 0,
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

    if not check_if_no_data:
        r.set(key, json.dumps(finishedObject.get_json()).encode("utf-8"))
        r.expire(key, 86400)

    return finishedObject
