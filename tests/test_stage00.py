# Simple assignment
from selenium.webdriver import Chrome

driver = Chrome()

# Or use the context manager
from selenium.webdriver import Chrome

def test_app_is_online():
    with Chrome() as driver:
        driver.get("http://127.0.0.1:8000")
        assert driver.title == "Bloomingmath"
