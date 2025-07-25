import json
import os
import urllib.parse
import urllib.request

def get_smart_jacket(feelslike, wind, condition, is_night, precip_mm, humidity, uv, cloud):
    c = condition.lower()
    context = {
        "feelslike": feelslike,
        "wind": wind,
        "condition": c,
        "is_night": is_night,
        "precip_mm": precip_mm,
        "humidity": humidity,
        "uv": uv,
        "cloud": cloud
    }

    rules = [
        {
            "when": lambda d: d["feelslike"] < -5,
            "jacket": "Arctic parka or expedition coat",
            "layer": "Thermal base layer + heavy insulated outer shell"
        },
        {
            "when": lambda d: "snow" in d["condition"] or "ice" in d["condition"],
            "jacket": "Insulated waterproof snow jacket",
            "layer": "Thermal mid-layer recommended"
        },
        {
            "when": lambda d: d["precip_mm"] > 5 or "storm" in d["condition"],
            "jacket": "Rain shell with light insulation",
            "layer": "Wear waterproof layers"
        },
        {
            "when": lambda d: d["feelslike"] < 5,
            "jacket": "Windproof insulated jacket",
            "layer": "Layer fleece underneath"
        },
        {
            "when": lambda d: "drizzle" in d["condition"] or "light rain" in d["condition"],
            "jacket": "Light waterproof shell",
            "layer": "Shell over a hoodie works well"
        },
        {
            "when": lambda d: 5 <= d["feelslike"] < 15,
            "jacket": "Softshell or fleece jacket",
            "layer": "Optional shell if windy or wet"
        },
        {
            "when": lambda d: 15 <= d["feelslike"] <= 22 and d["humidity"] > 70,
            "jacket": "Breathable shell or light jacket",
            "layer": "No insulation needed"
        },
        {
            "when": lambda d: 15 <= d["feelslike"] <= 22 and d["wind"] > 20 and d["is_night"],
            "jacket": "Light jacket or hoodie for the breeze",
            "layer": "Add thin base layer if outdoors long"
        },
        {
            "when": lambda d: d["feelslike"] > 22,
            "jacket": "No jacket needed",
            "layer": "Bring a shell only if forecast shifts"
        },
    ]

    default_jacket = "No jacket needed"
    default_layer = None

    for rule in rules:
        if rule["when"](context):
            return {
                "jacket": rule["jacket"],
                "layering": rule["layer"],
                "hints": build_hints(wind, uv, cloud, is_night, feelslike)
            }

    return {
        "jacket": default_jacket,
        "layering": default_layer,
        "hints": build_hints(wind, uv, cloud, is_night, feelslike)
    }

def build_hints(wind, uv, cloud, is_night, feelslike):
    hints = []
    if wind > 20:
        hints.append("It may feel colder if you're biking or walking.")
    if uv >= 6 and cloud < 20 and not is_night:
        hints.append("Strong UV — sun exposure might make it feel warmer.")
    if cloud > 80 and feelslike < 15:
        hints.append("Overcast skies can make it feel cooler than it is.")
    return hints

def handler(event, context):
    key = os.environ["WEATHERAPI_KEY"]
    query = event.get("queryStringParameters", {}) or {}

    location = query.get("zip") or (
        query.get("lat") + "," + query.get("lon") if query.get("lat") and query.get("lon") else None
    )

    cors_headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET"
    }

    if not location:
        return {
            "statusCode": 400,
            "headers": cors_headers,
            "body": json.dumps({"error": "Missing location input"})
        }

    try:
        url = f"https://api.weatherapi.com/v1/current.json?key={key}&q={urllib.parse.quote(location)}"
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read())

        weather = data["current"]
        country_raw = data["location"].get("country", "")
        country_clean = country_raw.strip().lower()
        use_fahrenheit = "usa" in country_clean or "united states" in country_clean

        temperature = weather["temp_f"] if use_fahrenheit else weather["temp_c"]
        feelslike = weather["feelslike_f"] if use_fahrenheit else weather["feelslike_c"]
        unit = "F" if use_fahrenheit else "C"

        smart = get_smart_jacket(
            feelslike=feelslike,
            wind=weather["wind_kph"],
            condition=weather["condition"]["text"],
            is_night=(not weather["is_day"]),
            precip_mm=weather["precip_mm"],
            humidity=weather["humidity"],
            uv=weather["uv"],
            cloud=weather["cloud"]
        )

        return {
            "statusCode": 200,
            "headers": cors_headers,
            "body": json.dumps({
                "location": data["location"]["name"],
                "temp": temperature,
                "unit": unit,
                "condition": weather["condition"]["text"],
                "jacket": smart["jacket"],
                "layering": smart["layering"],
                "hints": smart["hints"]
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": cors_headers,
            "body": json.dumps({"error": "Failed to fetch weather data", "details": str(e)})
        }