import pytest
from automation_framework.utilities.api_helpers import ApiHelper
from automation_framework.utilities.db_helpers import DatabaseHelper
from automation_framework.utilities.configs_helpers import ConfigsHelper
from automation_framework.utilities.excel_helpers import ExcelHelpers as Excel
from automation_framework.page_objects.weather_tab import WeatherTab
from automation_framework.utilities.test_helpers import TestHelpers
from automation_framework.utilities.path_manager import PathManager as Path


# This test suite is designed to test the OpenWeatherMap API and compare the results with the TimeAndDate.com website
# initializing the ConfigsHelper class to read the base url from the config.ini file
read_configs = ConfigsHelper("config", "config.ini")
base_url = read_configs.get_configs("web", "BASE_URL")

# initializing the Path class to get the path of the reports folder
# in order to later store the temperature discrepancy report
temperature_discrepancies = []
reports_path = Path.get_relative_path("reports")


# The following fixtures are used to initialize the API and DB helpers
@pytest.fixture(scope="module")
def api():
    return ApiHelper()


@pytest.fixture(scope="module")
def db():
    return DatabaseHelper()


# not using the full list of cities for the first tests because it would take too long
# for the purpose of this exam, I used the basic parameterize fixture in order to create the db
@pytest.mark.test_id_001
@pytest.mark.parametrize("city", ["London", "New York", "Paris", "Tel Aviv", "Sao Paulo"])
def test_validate_status_code(api, city):
    expected_result = 200
    actual_result = api.get_status_code(api.get_current_weather("q", city))

    print(f"Expected result: Status code: {expected_result} \nActual result: Status code:{actual_result}")

    assert expected_result == actual_result


@pytest.mark.test_id_002
@pytest.mark.parametrize("city", ["London", "New York", "Paris", "Tel Aviv", "Sao Paulo"])
def test_validate_city_weather(api, city, db):
    # get the json response from the API
    api_weather = api.get_current_weather("q", city)
    # get temp and feels like from the API
    api_temp = api.get_weather_keys(api_weather, "temp")
    api_feels_like = api.get_weather_keys(api_weather, "feels_like")

    print(f"(OpenWeather API) Temperature in {city} is {api_temp} °C")
    print(f"(OpenWeather API) Feels Like in {city} is {api_feels_like} °C")

    # create a new table in the database if it does not exist yet
    db.create_tables()
    # record the weather data received from the API response into the database
    db.insert_weather_data(city, api_temp, api_feels_like)

    # get the weather data from the database and assign to vars
    db_temp = db.get_weather_data(city, "temperature")
    db_feels_like = db.get_weather_data(city, "feels_like")

    print(f"(DB) Temperature in {city} is {db_temp} °C")
    print(f"(DB) Feels Like in {city} is {db_feels_like} °C")

    # validate the weather data received from the API was successfully recorded into the database
    assert api_temp == db_temp
    assert api_feels_like == db_feels_like


@pytest.mark.test_id_003
@pytest.mark.parametrize("city", ["London", "New York", "Paris", "Tel Aviv", "Sao Paulo"])
def test_validate_city_id_weather(api, city, db):
    # first get the json response from the API with the full info in order to retrieve the city id
    city_id = api.get_city_id(api.get_current_weather("q", city))
    # now we can retrieve the weather data from the database using the city id
    api_weather = api.get_current_weather("id", city_id)
    api_temp = api.get_weather_keys(api_weather, "temp")
    api_feels_like = api.get_weather_keys(api_weather, "feels_like")

    print(f"(OpenWeather API) The ID of {city} is {city_id}")
    print(f"(OpenWeather API) Temperature in {city} is {api_temp} °C")
    print(f"(OpenWeather API) Feels Like in {city} is {api_feels_like} °C")

    db.create_tables()
    db.insert_weather_data(city, api_temp, api_feels_like)

    db_temp = db.get_weather_data(city, "temperature")
    db_feels_like = db.get_weather_data(city, "feels_like")

    print(f"(DB) Temperature in {city} is {db_temp} °C")
    print(f"(DB) Feels Like in {city} is {db_feels_like} °C")

    assert api_temp == db_temp
    assert api_feels_like == db_feels_like


# I separated this into part of the question into a separate test because it made the other tests too long
# It's more readable like this... it's merely to demonstrate that:
# a) I understood the task and (b) that I am able to execute it
@pytest.mark.test_id_004
@pytest.mark.parametrize("city", ["London", "New York", "Paris", "Tel Aviv", "Sao Paulo"])
def test_highest_avg_temp(api, db, city):
    # retrieve the json response from the API with the full info
    api_weather = api.get_current_weather("q", city)
    api_temp_min = api.get_weather_keys(api_weather, "temp_min")
    api_temp_max = api.get_weather_keys(api_weather, "temp_max")
    # calculate the average temperature based on the min and max temperatures
    api_avg_temp = round(((api_temp_min + api_temp_max) / 2), 2)

    print(f"(OpenWeather API) The Lowest Temperature in {city} is {api_temp_min} °C")
    print(f"(OpenWeather API) The Highest Temperature in {city} is {api_temp_max} °C")
    print(f"(OpenWeather API) The Average Temperature in {city} is {api_avg_temp} °C")

    # add new columns to the existing table if they don't exist yet
    # one column for each parameter received from the API
    db.add_column_to_table("weather_data", "min_temp", "FLOAT")
    db.add_column_to_table("weather_data", "max_temp", "FLOAT")
    db.add_column_to_table("weather_data", "average_temp", "FLOAT")

    # record the weather data received from the API into the database in the new columns
    db.insert_data(city, "min_temp", api_temp_min)
    db.insert_data(city, "max_temp", api_temp_max)
    db.insert_data(city, "average_temp", api_avg_temp)

    # get the data from the database and assign to vars
    db_highest_avg_temp = db.get_param_boundary_value("MAX", "average_temp")
    city_w_highest_avg_temp = db.get_city_by_param("MAX", "average_temp")

    print(f"(DB) {city_w_highest_avg_temp} is the city with the highest average temperature, {db_highest_avg_temp}°C")


@pytest.mark.test_id_005
@pytest.mark.cities_list
def test_weather_discrepancy(driver_setup, db, city, country):
    # set up the driver
    driver = driver_setup
    # access the page objects (temperature, feels like)
    weather = WeatherTab(driver)
    # build tester object to generate the discrepancies report at the end of the test
    tester = TestHelpers()

    # in the cities_list.xlsx file, the city name is in the first column
    # Country name is in the second column
    # They are capitalized and have spaces, for the url they need to use '-' instead of ' ' and lowercase
    my_city = city.replace(" ", "-").lower()
    my_country = country.replace(" ", "-").lower()

    # concatenate the base url with the city name and country name
    url = f"{base_url}/{my_country}/{my_city}"
    # go to the url in chrome
    driver.get(url)

    # get the temperature values from the web page and from the database
    web_temp = weather.get_temperature()
    db_temp = db.get_weather_data(city, "temperature")

    print(f"(OpenWeather API) Temperature in {city} is {web_temp}")
    print(f"(DB) Temperature in {city} is {db_temp} °C")

    # get the feels like values from the web page and from the database
    web_feels_like = weather.get_feels_like()
    db_feels_like = db.get_weather_data(city, "feels_like")

    print(f"(OpenWeather API) Temperature in {city} is {web_feels_like}")
    print(f"(DB) Temperature in {city} is {db_feels_like} °C")

    # convert the values from the web page to int types in order to compare them
    # using int and not float to deliberately round results
    # I don't think the test should fail on decimal differences
    # the results from the web page come with °C, so I remove it from the string
    converted_web_temp = int(web_temp.split("°C")[0])
    converted_db_temp = int(db_temp)
    converted_web_feels_like = int(web_feels_like.split("°C")[0])
    converted_db_feels_like = int(db_feels_like)

    # compare the values after conversion
    # if they match, do nothing
    # if not, add them to the list of discrepancies
    if converted_web_temp != converted_db_temp or converted_web_feels_like != converted_db_feels_like:
        temperature_discrepancies.append({
            'city': city,
            'tnd_temp': web_temp,
            'owm_temp': str(db_temp) + " °C",
            'tnd_feels_like': web_feels_like,
            'owm_feels_like': str(db_feels_like) + " °C"
        })

    # generate the discrepancy report
    tester.generate_weather_discrepancy_report_txt(
        temperature_discrepancies, reports_path + "/weather_discrepancy_report.txt"
    )


@pytest.mark.test_id_005
@pytest.mark.cities_list
def test_weather_discrepancy(driver_setup, db, city, country):
    # set up the driver
    driver = driver_setup
    excel = Excel()

    cities_list = excel.get_param_list("cities_list.xlsx", "cities_list", "name")
    countries_list = excel.get_param_list("cities_list.xlsx", "cities_list", "country")
    for country_name in countries_list:
        pass

    # add logic to remove empty spaces from country and city names
    # add '-' instead of empty spaces
    # use for loop inside for loop to iterate through all countries and cities in the list
    # this will allow to keep the browser open for the entire duration of the test
    # and once a run is finished, store the results in a dictionary
    # such as {city: [temp, feels], city: [[temp, feels]], city: [[temp, feels]]}
    # use this dictionary to compare the results with the database



