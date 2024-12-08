from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException, UnexpectedAlertPresentException, NoAlertPresentException
from selenium.webdriver.support.ui import Select
import time

# Function to load XSS payloads from a file
def load_payloads(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            payloads = file.read().splitlines()
        return payloads
    except FileNotFoundError:
        print(f"Error: {filename} not found.")
        return []
    except UnicodeDecodeError as e:
        print(f"UnicodeDecodeError: {e}. Please ensure the file is encoded in UTF-8.")
        return []

# Function to handle potential alerts
def handle_alert(driver):
    try:
        alert = driver.switch_to.alert
        print(f"Alert detected with text: {alert.text}")
        alert.accept()  # Accept the alert to dismiss it
        print("Alert dismissed.")
    except NoAlertPresentException:
        print("No alert present.")
    except UnexpectedAlertPresentException:
        print("Unexpected alert present.")

# Function to test XSS payloads using Selenium
def test_xss_with_browser():
    # Ask if login is required
    requires_login = input("Does the application require login? (yes/no): ").strip().lower()

    if requires_login == 'yes':
        login_url = input("Enter the login URL (e.g., http://localhost/DVWA/login.php): ")
        username = input("Enter the username: ")
        password = input("Enter the password: ")

    # Ask for XSS page URL
    xss_url = input("Enter the XSS URL (e.g., http://localhost/DVWA/vulnerabilities/xss_r/): ")

    # Load XSS payloads from file
    xss_payloads = load_payloads('S-payloads.txt')
    if not xss_payloads:
        print("No payloads found. Exiting.")
        return

    # Set up Selenium WebDriver
    driver = webdriver.Chrome()  # Update to match your browser
    detected_payloads = []

    try:
        # If login is required, handle the login process
        if requires_login == 'yes':
            driver.get(login_url)
            print("Opened login page.")

            # Find and fill login form
            driver.find_element(By.NAME, "username").send_keys(username)
            driver.find_element(By.NAME, "password").send_keys(password)
            driver.find_element(By.NAME, "Login").click()
            time.sleep(2)

            # Check if login was successful
            if "Login failed" in driver.page_source:
                print("Login failed. Exiting.")
                return
            print("Logged in successfully.")

            # Handle security settings for DVWA
            if login_url == "http://localhost/DVWA/login.php":
                # Navigate to the security settings page and set level to Low
                security_url = "http://localhost/DVWA/security.php"  # Update for your app
                driver.get(security_url)
                print("Navigated to security settings page.")

                security_dropdown = Select(driver.find_element(By.NAME, "security"))
                security_dropdown.select_by_visible_text("Low")
                driver.find_element(By.NAME, "seclev_submit").click()
                print("Set security level to 'Low'.")

        # Navigate to the XSS page
        driver.get(xss_url)
        print("Navigated to XSS vulnerability page.")

        # Find forms on the page
        forms = driver.find_elements(By.TAG_NAME, "form")
        if not forms:
            print("No forms found on the page. XSS testing aborted.")
            return

        print(f"Found {len(forms)} forms on the page. Testing for XSS vulnerabilities...\n")

        # Test each form with payloads
        for form_index, form in enumerate(forms):
            for payload in xss_payloads:
                try:
                    forms = driver.find_elements(By.TAG_NAME, "form")
                    form = forms[form_index]

                    inputs = form.find_elements(By.TAG_NAME, "input")

                    for input_field in inputs:
                        if input_field.get_attribute("type") == "text":
                            input_field.clear()
                            input_field.send_keys(payload)
                            print(f"Injected payload: {payload}")

                    form.submit()
                    time.sleep(2)

                    # Handle alert if present
                    try:
                        alert = driver.switch_to.alert
                        alert_text = alert.text
                        print(f"Alert detected with text: {alert_text}")
                        alert.accept()
                        if payload not in detected_payloads:
                            detected_payloads.append(payload)
                            print(f"Potential XSS vulnerability detected!\nPayload: {payload}")
                    except NoAlertPresentException:
                        print("No alert present.")

                    # Check if payload is reflected in the page source
                    if payload in driver.page_source and payload not in detected_payloads:
                        detected_payloads.append(payload)
                        print(f"Potential XSS vulnerability detected in page source!\nPayload: {payload}")

                except UnexpectedAlertPresentException as e:
                    print("Unexpected alert present. Handling it...")
                    handle_alert(driver)

                except StaleElementReferenceException:
                    print("Encountered StaleElementReferenceException. Re-locating elements...")
                    continue

        if detected_payloads:
            print("\nXSS vulnerabilities detected for the following payloads:")
            for detected in detected_payloads:
                print(detected)
        else:
            print("No XSS vulnerabilities detected.")
        print("XSS testing completed.")

    finally:
        time.sleep(2)
        driver.quit()
        print("Browser closed.")

# Main function
if __name__ == "__main__":
    test_xss_with_browser()
