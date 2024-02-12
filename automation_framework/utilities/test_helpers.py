

class TestHelpers:
    @staticmethod
    def generate_weather_discrepancy_report_txt(discrepancies, file_path):
        # Generate a report of discrepancies between TimeAndDate.com and OpenWeatherMap.com
        # for simplicity, the report will be a text file
        # but generally, would probably use allure or something similar for generating a html report
        with open(file_path, 'w') as file:
            file.write("Temperature and Feels Like Discrepancies Report\n")
            file.write("------------------------------------------------\n")
            for item in discrepancies:
                file.write(f"City: {item['city']}\n")
                file.write(f"  TimeAndDate.com (Web) Temperature: {item['tnd_temp']} | "
                           f"OpenWeatherMap (API/DB) Temperature: {item['owm_temp']}\n")
                file.write(f"  TimeAndDate.com (Web) Feels Like: {item['tnd_feels_like']} | "
                           f"OpenWeatherMap (API/DB) Feels Like: {item['owm_feels_like']}\n")
                file.write("------------------------------------------------\n")




