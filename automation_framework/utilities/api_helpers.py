import requests
from automation_framework.utilities.configs_helpers import ConfigsHelper


class ApiHelper:
    # Load API_KEY and BASE_URL from config.ini
    configs = ConfigsHelper("config", "config.ini")
    API_KEY = configs.get_configs("api", "API_KEY")
    BASE_URL = configs.get_configs("api", "BASE_URL")

    def get_current_weather(self, identifier: str, city_name_or_id: str):
        url = f"{self.BASE_URL}?{identifier}={city_name_or_id}&appid={self.API_KEY}"
        params = {
            identifier: city_name_or_id,
            "appid": self.API_KEY,
            "units": "metric"
        }
        # Send GET request to OpenWeatherMap API
        response = requests.get(url, params=params)
        print("\nURL: " + url)
        print("Status Code: " + str(response.status_code))
        return response

    def get_status_code(self, response):
        return response.status_code

    def get_city_id(self, response):
        return response.json()["id"]

    def get_weather_keys(self, response, weather: str):
        """
        :param response:
        :param weather: choose JSON key to retrieve value for 'temperature' or 'feels_like'
        :return:
        """
        return round((response.json()["main"][weather]), 2)

