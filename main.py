import logging
import requests
from fastapi import FastAPI, HTTPException, Request

app = FastAPI()

# Set up logging
logging.basicConfig(level=logging.INFO)

@app.get("/api/hello")
async def hello(visitor_name: str, request: Request):
    try:
        client_ip = request.client.host
        logging.info(f"Client IP: {client_ip}")

        location = get_location(client_ip)
        logging.info(f"Location: {location}")

        city = location.get("city", "New York")
        logging.info(f"City: {city}")

        temperature = get_temperature(city)
        logging.info(f"Temperature: {temperature}")

        greeting = f"Hello, {visitor_name}! The temperature is {temperature} degrees Celsius in {city}"

        return {
            "client_ip": client_ip,
            "location": city,
            "greeting": greeting
        }
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logging.error(f"Unhandled error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

def get_location(ip):
    try:
        response = requests.get(f"https://ipinfo.io/{ip}/json")
        response.raise_for_status()
        location_data = response.json()
        logging.info(f"Location Data: {location_data}")
        return location_data
    except requests.RequestException as e:
        logging.error(f"Error fetching location: {e}")
        raise HTTPException(status_code=500, detail="Error fetching location")

def get_temperature(city):
    api_key = "11937ee579f04b1b851155003240307"
    logging.info(f"Weather API Key: {api_key}")
    if not api_key:
        logging.error("Weather API key not found")
        raise HTTPException(status_code=500, detail="Weather API key not found")
    try:
        response = requests.get(f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}")
        response.raise_for_status()
        weather_data = response.json()
        logging.info(f"Weather Data: {weather_data}")
        return weather_data["current"]["temp_c"]
    except requests.RequestException as e:
        logging.error(f"Error fetching temperature: {e}")
        raise HTTPException(status_code=500, detail="Error fetching temperature")
    except KeyError as e:
        logging.error(f"Unexpected response format from Weather API: {e}")
        raise HTTPException(status_code=500, detail="Unexpected response format from Weather API")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)