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
        driver.find_element_by_id("inputUsername").send_keys("user")
        driver.find_element_by_id("inputPassword").send_keys("pass")
        driver.find_element_by_css_selector("button[type=submit]").click()

        driver.find_element_by_link_text("profilo").click()
        assert driver.current_url == f"{base_url}/profile"
        assert "Profilo di user" in driver.page_source

        driver.find_element_by_css_selector("input[name=fullname").clear()
        driver.find_element_by_css_selector("input[name=fullname").send_keys("Renato")
        driver.find_element_by_id("change_fullname_submit").click()
        assert "Cambia il tuo nome (Renato)" in driver.page_source

        driver.find_element_by_id("other_group_details").click()
        driver.find_element_by_id("sub_group_prima_button").click()
        assert "unsub_group_prima" in driver.page_source

        driver.find_element_by_id("unsub_group_prima_button").click()
        assert "sub_group_prima" in driver.page_source



