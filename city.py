import requests


def get_lat_lon(city_name: str):
    """Consulta latitude e longitude pelo nome da cidade."""
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1"
    response = requests.get(url)
    if response.status_code != 200:
        return None, None, f"Erro ao buscar coordenadas: {response.status_code}"

    data = response.json()
    results = data.get("results")
    if not results:
        return None, None, f"Cidade '{city_name}' não encontrada."

    city_info = results[0]
    return city_info["latitude"], city_info["longitude"], None


def get_weather(lat: float, lon: float) -> str:
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    response = requests.get(url)
    if response.status_code != 200:
        return "Erro ao acessar a API do tempo."
    data = response.json()
    if "current_weather" not in data:
        return "Dados do tempo não disponíveis para esta localização."
    weather = data["current_weather"]
    return (
        f"Tempo atual em ({lat}, {lon}):\n"
        f"  Temperatura: {weather['temperature']}°C\n"
        f"  Vento: {weather['windspeed']} km/h\n"
        f"  Condição: Código {weather['weathercode']}"
    )
