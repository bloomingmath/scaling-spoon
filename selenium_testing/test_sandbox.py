import random
import string
import time

from selenium.webdriver import Firefox

base_url = "http://127.0.0.1:8000"


def random_string(string_length=8):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(string_length))


def test_profile_page():
    with Firefox() as driver:
        driver.get(f"{base_url}/")
        driver.find_element_by_id("inputEmail").send_keys("user@example.com")
        driver.find_element_by_id("inputPassword").send_keys("pass")
        driver.find_element_by_css_selector("button[type=submit]").click()

        driver.find_element_by_link_text("profilo").click()
        assert driver.current_url == f"{base_url}/users/profile"

        driver.find_element_by_id("other_group_details").click()
        driver.find_element_by_id("sub_group_first_button").click()
        # assert "unsub_group_prima" in driver.page_source

        # driver.find_element_by_link_text("Bloomingmath").click()
        # assert driver.current_url == f"{base_url}/"
        # assert "Questi sono gli argomenti a tua disposizione" in driver.page_source
        # assert "second" in driver.page_source
        #
        # driver.find_element_by_link_text("profilo").click()
        # driver.find_element_by_id("other_group_details").click()
        #
        # driver.find_element_by_id("unsub_group_prima_button").click()
        # assert "sub_group_prima" in driver.page_source
        pass


