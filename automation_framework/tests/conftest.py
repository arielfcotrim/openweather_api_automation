import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from automation_framework.utilities.path_manager import PathManager as Path
from automation_framework.utilities.excel_helpers import ExcelHelpers as Excel


@pytest.fixture()
def driver_setup():
    # Initialize Chrome options
    options = Options()
    options.headless = True  # Run Chrome in headless mode
    options.add_argument('--disable-gpu')  # Disable GPU (for headless mode)
    options.add_argument('--no-sandbox')  # Bypass OS security model (not recommended for production)
    options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})  # Disable images

    # Initialize Chrome WebDriver with options
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    # generate a new driver instance for each test
    yield driver

    # Cleanup and teardown of the driver instance
    driver.delete_all_cookies()
    driver.quit()


def pytest_generate_tests(metafunc):
    """
    This function is called once for each test function. It is used to parametrize test functions.
    It uses the cities listed in the "cities_list" to parametrize test functions that require "city" and "country".
    :param metafunc:
    :return:
    """
    # Check if the test function is marked with "cities_list" and requires both "city" and "country"
    if ("city" in metafunc.fixturenames and "country" in metafunc.fixturenames
            and metafunc.definition.get_closest_marker("cities_list")):
        excel = Excel()
        file_path = Path.get_relative_path("tests", "cities_list.xlsx")
        city_country_data = excel.get_city_country_list(file_path, "cities_list")

        # List of tuples [(city, country), (city_2, country_2), ...]
        metafunc.parametrize("city, country", city_country_data)
