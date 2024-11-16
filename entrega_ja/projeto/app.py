from flask import Flask, render_template, request, redirect, url_for
import requests
from dotenv import load_dotenv
import os 

app = Flask(__name__)

load_dotenv()
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

# Função para obter rota otimizada
def get_optimized_route(start_location, stop_locations):
    directions_url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": start_location,
        "destination": start_location,
        "waypoints": "|".join(stop_locations),
        "optimize_waypoint": "true",
        "key": GOOGLE_MAPS_API_KEY
    }
    response = requests.get(directions_url, params=params)
    response_data = response.json()

    if response.status_code != 200 or response_data.get("status") != "OK":
        print("Erro ao obter rota otimizada:", response_data.get("error_message"))
        return None

    route_info = {
        "total_distance": 0,
        "total_duration": 0,
        "optimized_order": [],
        "steps": []
    }
    route = response_data["routes"][0]
    legs = route["legs"]
    for leg in legs:
        route_info["total_distance"] += leg["distance"]["value"]
        route_info["total_duration"] += leg["duration"]["value"]
        route_info["steps"].append({
            "start_address": leg["start_address"],
            "end_address": leg["end_address"],
            "distance": leg["distance"]["text"],
            "duration": leg["duration"]["text"]
        })
    route_info["optimized_order"] = route["waypoint_order"]
    route_info["total_distance"] = f"{route_info['total_distance'] / 1000:.2f} km"
    route_info["total_duration"] = f"{route_info['total_duration'] / 60:.2f} mins"

    return route_info

# Página principal
@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

# Página de resultado da rota
@app.route("/calculate_route", methods=["POST"])
def calculate_route():
    start_location = request.form["start_location"]
    stop_locations = request.form.getlist("stop_locations")
    print(start_location, stop_locations)
    route_data = get_optimized_route(start_location, stop_locations)

    if route_data:
        return render_template("route_result.html", route_data=route_data)
    else:
        return "Erro ao calcular rota", 500

if __name__ == "__main__":
    app.run(debug=True)
9