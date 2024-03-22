from flask import Flask
from flask import render_template, request
from datetime import datetime
from flask_caching import Cache
import requests

app = Flask(__name__)
cache = Cache(config={'CACHE_TYPE': 'simple', 'CACHE_DEFAULT_TIMEOUT': 300})  # 5 minutes in seconds
cache.init_app(app)


cache = Cache(app)

def get_user_city(ip):
    url = f"http://ip-api.com/json/{ip}"
    response = requests.get(url)
    data = response.json()
    city = data.get("city")
    return city

def get_current_weather(city):
    API_KEY = "315cd33146bce681cec0e1f411a44391"
    api_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&lang=fr&units=metric"
    data = requests.get(api_url).json()
    return data


def get_weekly_forecast(city):
    API_KEY = "315cd33146bce681cec0e1f411a44391"
    api_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&lang=fr&units=metric"
    data = requests.get(api_url).json()

    weekly_forecast = {}
    for forecast in data['list']:
        forecast_date = datetime.fromtimestamp(forecast['dt'])
        forecast_day = forecast_date.strftime('%A')
        if forecast_day not in weekly_forecast:
            weekly_forecast[forecast_day] = []
        forecast_data = {
            'time': forecast_date.strftime('%H:%M'),
            'temp': round(forecast['main']['temp']),
            'icon': forecast['weather'][0]['icon'],
            'description': forecast['weather'][0]['description']
        }
        weekly_forecast[forecast_day].append(forecast_data)

    return weekly_forecast


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        city = request.form.get("city")
        # Check cache for current weather data
        data = cache.get(f"weather_{city}")
        if data is None:
            data = get_current_weather(city)
            cache.set(f"weather_{city}", data)
            
        # Check cache for weekly forecast data
        data_forcast = cache.get(f"forecast_{city}")
        if data_forcast is None:
            data_forcast = get_weekly_forecast(city)
            cache.set(f"forecast_{city}", data_forcast)
        return render_template('index.html', data=data, data_forcast=data_forcast)
    else:
        user_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        default_city = get_user_city(user_ip)
        print(default_city)
        # Check cache for current weather data for default city
        data = cache.get(f"weather_{default_city}")
        if data is None:
            data = get_current_weather(default_city)
            cache.set(f"weather_{default_city}", data)
        # Check cache for weekly forecast data for default city
        data_forcast = cache.get(f"forecast_{default_city}")
        if data_forcast is None:
            data_forcast = get_weekly_forecast(default_city)
            cache.set(f"forecast_{default_city}", data_forcast)
        return render_template('index.html', data=data, data_forcast=data_forcast)


if __name__ == '__main__':
    app.run(debug=True)

