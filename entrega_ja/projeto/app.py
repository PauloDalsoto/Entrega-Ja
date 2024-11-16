from flask import Flask, render_template, request, redirect, url_for, jsonify
import requests
from dotenv import load_dotenv
import os

# Inicializando o app Flask
app = Flask(__name__)

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

# Função para obter rota otimizada
def get_optimized_route(start_location, stop_locations):
    """
    Obtém a rota otimizada usando a API do Google Maps.

    :param start_location: Endereço inicial
    :param stop_locations: Lista de endereços intermediários
    :return: Dicionário com informações da rota otimizada ou None em caso de erro
    """
    directions_url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": start_location,
        "destination": start_location,
        "waypoints": "|".join(stop_locations),
        "optimize_waypoints": True,
        "key": GOOGLE_MAPS_API_KEY
    }

    try:
        response = requests.get(directions_url, params=params)
        response_data = response.json()

        # Verificar status da resposta
        if response.status_code != 200 or response_data.get("status") != "OK":
            print("Erro ao obter rota otimizada:", response_data.get("error_message", "Desconhecido"))
            return None

        # Processar informações da rota
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

        # Conversão de valores para exibição
        route_info["optimized_order"] = route["waypoint_order"]
        route_info["total_distance"] = f"{route_info['total_distance'] / 1000:.2f} km"
        route_info["total_duration"] = f"{route_info['total_duration'] / 60:.2f} mins"

        return route_info

    except Exception as e:
        print(f"Erro durante a chamada da API: {e}")
        return None

# Página principal
@app.route("/", methods=["GET"])
def index():
    """
    Renderiza a página principal.
    """
    return render_template("index.html")

# Página de formulário para endereços
@app.route('/endereco', methods=["GET"])
def endereco():
    """
    Renderiza a página para inserção de endereços.
    """
    return render_template('endereco.html')

# Página de resultado da rota
@app.route("/calculate_route", methods=["POST"])
def calculate_route():
    """
    Calcula a rota otimizada e renderiza os resultados.
    """
    try:
        # Obter dados do formulário
        start_location = request.form.get("start_location", "").strip()
        stop_locations = request.form.getlist("stop_locations")
        
        print(f"Endereço inicial: {start_location}")
        print(f"Endereços intermediários: {stop_locations}")
        print(GOOGLE_MAPS_API_KEY)

        # Validação básica
        if not start_location or not stop_locations:
            return "Por favor, forneça o endereço inicial e pelo menos um endereço de parada.", 400

        # Chamar a função para calcular a rota
        route_data = get_optimized_route(start_location, stop_locations)

        # Renderizar resultados ou exibir erro
        if route_data:
            return render_template("link.html", route_data=route_data)
        else:
            return "Erro ao calcular rota. Verifique os endereços e tente novamente.", 500

    except Exception as e:
        print(f"Erro ao processar a solicitação: {e}")
        return "Erro interno no servidor. Tente novamente mais tarde.", 500

if __name__ == "__main__":
    # Executar o app Flask em modo de desenvolvimento
    app.run(debug=True)
