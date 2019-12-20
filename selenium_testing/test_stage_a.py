import random
import string
import time

from selenium.webdriver import Firefox

base_url = "http://127.0.0.1:8000"


def random_string(string_length=8):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(string_length))


def test_authorization_cicle():
    """Development stage a is about user authentication. Users can signup, signin and signout. The server
    communicates results via message flashing."""
    with Firefox() as driver:
        # Access homepage
        driver.get(f"{base_url}/")

        # Anchor to signup page
        driver.find_element_by_link_text("registrazione").click()
        assert driver.current_url == f"{base_url}/signup"

        # Filling form with incomplete data will get you nowhere
        driver.find_element_by_id("inputUsername").send_keys("username")
        driver.find_element_by_id("inputPassword").send_keys("pass")
        driver.find_element_by_css_selector("button[type=submit]").click()
        assert driver.current_url == f"{base_url}/signup"

        # If passwords don't match, fails, redirect to signup and flash a warning
        driver.find_element_by_id("inputEmail").send_keys(f"username@example.com")
        driver.find_element_by_id("inputRePassword").send_keys("different pass")
        driver.find_element_by_css_selector("button[type=submit]").click()
        assert driver.current_url == f"{base_url}/signup"
        assert "Le password devono coincidere." in driver.page_source


        # Fill signup form and submit
        username = random_string()
        driver.find_element_by_id("inputUsername").send_keys(username)
        driver.find_element_by_id("inputEmail").send_keys(f"{username}@example.com")
        driver.find_element_by_id("inputPassword").send_keys("pass")
        driver.find_element_by_id("inputRePassword").send_keys("pass")
        driver.find_element_by_css_selector("button[type=submit]").click()

        # Being redirected to mainpage
        assert driver.current_url == f"{base_url}/"

        # Fill signin form and submit
        driver.find_element_by_id("inputUsername").send_keys(username)
        driver.find_element_by_id("inputPassword").send_keys("pass")
        driver.find_element_by_css_selector("button[type=submit]").click()

        # Homepage now display user-related info
        assert driver.current_url == f"{base_url}/"
        assert f"Benvenut@ {username}" in driver.page_source

        # Anchor to signout, homepage back to anonymous format
        driver.find_element_by_link_text("Esci").click()
        assert driver.current_url == f"{base_url}/"
        assert f"Benvenut@ Eternauta" in driver.page_source

