from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import NoAlertPresentException, UnexpectedAlertPresentException, StaleElementReferenceException
import time

# Function to load SQL injection payloads from a file
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

# Function to handle alerts
def handle_alert(driver):
    try:
        alert = Alert(driver)
        print(f"Alert detected with text: {alert.text}")
        alert.accept()
        print("Alert dismissed.")
        return True
    except NoAlertPresentException:
        return False
    except UnexpectedAlertPresentException:
        print("Unexpected alert present.")
        return True

# Function to check if SQL error or data leakage is detected
def check_sql_error_or_data_leak(page_source, payload):
    # Check for common SQL error messages in the page source
    sql_errors = ["SQL syntax", "database error", "MySQL error", "error in your SQL syntax", "you have an error in your SQL syntax"]
    for error in sql_errors:
        if error.lower() in page_source.lower():
            return True
    
    # Check for data leakage (e.g., "First name" or "ID")
    if "First name:" in page_source or "ID:" in page_source:
        return True
    
    # If no SQL error or data leakage found, return False
    return False

# Function to test SQL injection and detect success
def test_sql_injection():
    requires_login = input("Does this test require login? (yes/no): ").strip().lower()
    login_url, username, password = None, None, None

    if requires_login == 'yes':
        login_url = input("Enter the login URL (e.g., http://localhost/login.php): ")
        username = input("Enter the username: ")
        password = input("Enter the password: ")

    sql_injection_url = input("Enter the SQL injection testing URL: ")
    sql_payloads = load_payloads('sql-payloads.txt')
    if not sql_payloads:
        print("No payloads found. Exiting.")
        return

    driver = webdriver.Chrome()  # Use webdriver.Firefox() if needed
    detected_payloads = []

    try:
        # Perform login if required
        if requires_login == 'yes':
            driver.get(login_url)
            print("Opened login page.")
            driver.find_element(By.NAME, "username").send_keys(username)
            driver.find_element(By.NAME, "password").send_keys(password)
            driver.find_element(By.NAME, "Login").click()
            time.sleep(2)
            if "Login failed" in driver.page_source:
                print("Login failed. Exiting.")
                return
            print("Logged in successfully.")
        
        # Navigate to SQL injection testing page
        driver.get(sql_injection_url)
        print("Navigated to SQL injection testing page.")

        # Test all forms on the page
        forms = driver.find_elements(By.TAG_NAME, "form")
        if not forms:
            print("No forms found. Testing aborted.")
            return
        print(f"Found {len(forms)} forms.")

        for form_index, form in enumerate(forms):
            for payload in sql_payloads:
                try:
                    forms = driver.find_elements(By.TAG_NAME, "form")
                    form = forms[form_index]

                    # Locate text inputs in the form
                    inputs = form.find_elements(By.TAG_NAME, "input")
                    for input_field in inputs:
                        if input_field.get_attribute("type") in ["text", "search"]:
                            input_field.clear()
                            input_field.send_keys(payload)
                            print(f"Injected payload: {payload}")
                    
                    # Capture original page source
                    original_page_source = driver.page_source

                    # Submit the form
                    form.submit()
                    time.sleep(2)

                    # Check for alerts
                    if handle_alert(driver):
                        if payload not in detected_payloads:
                            detected_payloads.append(payload)
                            print(f"Potential SQL injection detected! Payload: {payload}")

                    # Capture new page source after form submission
                    new_page_source = driver.page_source

                    # Only flag as a vulnerability if there's a significant change that indicates an issue
                    if original_page_source != new_page_source and check_sql_error_or_data_leak(new_page_source, payload):
                        if payload not in detected_payloads:
                            detected_payloads.append(payload)
                            print(f"SQL Injection vulnerability detected! Payload: {payload}")

                except StaleElementReferenceException:
                    print("StaleElementReferenceException encountered. Retrying...")
                    continue

        # Print results
        if detected_payloads:
            print("\nSQL Injection vulnerabilities detected for the following payloads:")
            for payload in detected_payloads:
                print(payload)
        else:
            print("No SQL Injection vulnerabilities detected.")

    finally:
        time.sleep(1)
        driver.quit()

# Main function
if __name__ == "__main__":
    test_sql_injection()
