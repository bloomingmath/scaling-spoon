from selenium.webdriver import Firefox
base_url = "http://127.0.0.1:8000"

def test_app_is_online():
    with Firefox() as driver:
        driver.get(f"{base_url}")
        assert driver.title == "Bloomingmath"

import selenium
