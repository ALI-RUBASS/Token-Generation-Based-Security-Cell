from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException
import time

# Function to load XSS payloads from a file
# Function to load XSS payloads from a file
def load_payloads(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:  # Specify the encoding
            payloads = file.read().splitlines()  # Read the file and split it into lines
        return payloads
    except FileNotFoundError:
        print(f"Error: {filename} not found.")
        return []
    except UnicodeDecodeError as e:
        print(f"UnicodeDecodeError: {e}. Please ensure the file is encoded in UTF-8.")
        return []

# Function to test XSS payloads using Selenium
def test_xss_with_browser():
    # Ask for user inputs
    login_url = input("Enter the login URL (e.g., http://localhost/DVWA/login.php): ")
    username = input("Enter the username: ")
    password = input("Enter the password: ")

    # Load the XSS payloads from the payloads.txt file
    xss_payloads = load_payloads('B-payloads.txt')
    if not xss_payloads:
        print("No payloads found. Exiting.")
        return

    # Set up Selenium WebDriver (ensure you have the right driver for your browser)
    driver = webdriver.Chrome()  # Use 'webdriver.Firefox()' for Firefox
    detected_payloads = []  # To store detected payloads
    try:
        # Open the login page
        driver.get(login_url)
        print("Opened login page.")

        # Find the username, password fields and login button
        username_field = driver.find_element(By.NAME, "username")
        password_field = driver.find_element(By.NAME, "password")
        login_button = driver.find_element(By.NAME, "Login")
        
        # Enter credentials and login
        username_field.send_keys(username)
        password_field.send_keys(password)
        login_button.click()
        time.sleep(2)  # Wait for the login to complete
        # if the login is successful
        if "Login failed" in driver.page_source:
            print("Login failed. Exiting.")
            return
        print("Logged in successfully.")
        
        # Get the URL of the XSS vulnerability page
        xss_url = input("Enter the XSS URL (e.g., http://localhost/DVWA/vulnerabilities/xss_r/): ")
        
        # Navigate to the XSS vulnerability page
        driver.get(xss_url)
        print("Navigated to XSS vulnerability page.")
        
        # Find the form on the page
        forms = driver.find_elements(By.TAG_NAME, "form")
        if not forms:
            print("No forms found on the page. XSS testing aborted.")
            return
        
        print(f"Found {len(forms)} forms on the page. Testing for XSS vulnerabilities...\n")
        
        for form_index, form in enumerate(forms):
            for payload in xss_payloads:
                try:
                    # Re-locate the form to avoid stale element reference
                    forms = driver.find_elements(By.TAG_NAME, "form")
                    form = forms[form_index]

                    # Locate the text input fields in the form
                    inputs = form.find_elements(By.TAG_NAME, "input")
                    
                    # Enter the payload into the input fields
                    for input_field in inputs:
                        if input_field.get_attribute("type") == "text":
                            input_field.clear()
                            input_field.send_keys(payload)
                            print(f"Injected payload: {payload}")
                    
                    # Submit the form
                    form.submit()
                    # time.sleep(2)  # Wait for the response to load
                    
                    # Check if the payload is reflected in the page source
                    if payload in driver.page_source and payload not in detected_payloads:
                        detected_payloads.append(payload)  # Add to the list of detected payloads
                        print(f"Potential XSS vulnerability detected!\nPayload: {payload}")
                    
                except StaleElementReferenceException:
                    print("Encountered StaleElementReferenceException. Re-locating elements...")
                    continue
        
        if detected_payloads:
            print(f"\nXSS vulnerabilities detected for the following payloads:")
            for detected in detected_payloads:
                print(detected)
        else:
            print("No XSS vulnerabilities detected.")

        print("XSS testing completed.")
    finally:
        # Keep the browser open for debugging or close it after a delay
        time.sleep(1)  # Adjust as needed for debugging
        driver.quit()

# Main function
if __name__ == "__main__":
    test_xss_with_browser()
