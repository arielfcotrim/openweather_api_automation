from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


class WeatherTab:
    # selectors of page objects (temperature, feels like)
    temperature_css = '#qlook>div[class="h2"]'
    feels_like_xpath = '//table[@id="wt-48"]//tbody//tr[2]//td[1]'

    def __init__(self, driver):
        # Initialize the driver and wait
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 5)

    def get_temperature(self):
        temperature_element = self.wait.until(ec.visibility_of_element_located((By.CSS_SELECTOR, self.temperature_css)))
        return temperature_element.text

    def get_feels_like(self):
        feels_like_element = self.wait.until(ec.visibility_of_element_located((By.XPATH, self.feels_like_xpath)))
        return feels_like_element.text

