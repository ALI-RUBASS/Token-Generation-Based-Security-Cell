import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

new_endpoints = []

# Function to read endpoints from a file
def load_endpoints(file_path):
    try:
        with open(file_path, "r") as file:
            endpoints = [line.strip() for line in file if line.strip()]
        print(f"Loaded {len(endpoints)} endpoints from {file_path}.")
        return endpoints
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return []

# Function to test access control for unauthorized users
def test_broken_access_control(base_url, endpoints, cookies=None):
    headers = {}
    if cookies:
        headers['Cookie'] = cookies

    print(f"Testing access control on base URL: {base_url}")

    for endpoint in endpoints:
        full_url = f"{base_url.rstrip('/')}{endpoint}"

        # Send GET request to the endpoint
        response = requests.get(full_url, headers=headers)

        # Check HTTP status code
        if response.status_code == 200:
            print(f"{full_url} is accessible without proper authorization.")

# Function to automate forced browsing with Selenium
def forced_browsing(base_url, endpoints, session_cookie=None):
    """
    Improved forced browsing function using Selenium and HTTP status validation.

    :param base_url: The base URL of the application.
    :param endpoints: List of endpoints to test.
    :param session_cookie: Optional session cookie string for authenticated requests.
    """
    # Initialize Selenium WebDriver
    driver = webdriver.Chrome()
    print(f"Launching browser to test forced browsing on: {base_url}")
    
    # Setup headers for requests
    headers = {}
    if session_cookie:
        headers['Cookie'] = session_cookie

    try:
        for endpoint in endpoints:
            url = f"{base_url.rstrip('/')}{endpoint}"

            # Step 1: Check HTTP response with requests
            try:
                response = requests.head(url, headers=headers, allow_redirects=True)
                if response.status_code == 403 or response.status_code == 401:
                    print(f"Access blocked for {url} (HTTP {response.status_code}).")
                    continue
            except Exception as e:
                print(f"Error making request to {url}: {e}")
                continue

            # Step 2: Visit the page with Selenium
            driver.get(url)
            current_url = driver.current_url

            # Step 3: Check for unauthorized redirects
            if "login" in current_url.lower() or current_url != url:
                # print(f"Access blocked for {url}. Redirected to login page.")
                new_endpoints.append(endpoint)
                continue

            # Step 4: Analyze page content for unauthorized messages
            page_source = driver.page_source.lower()
            if "access denied" in page_source or "403 forbidden" in page_source or "unauthorized" in page_source:
                print(f"Access blocked for {url} (Access Denied message).")
                continue

            # If none of the conditions matched, the endpoint might be accessible
            # print(f"Potential Broken Access Control! {url} is accessible.")

    finally:
        driver.quit()


# Function to test if the endpoint leads to a valid page
def validate_page(base_url, new_endpoints):
    driver = webdriver.Chrome()
    print(f"Validating new endpoints for valid pages: {base_url}")

    valid_endpoints = []
    try:
        for endpoint in new_endpoints:
            url = f"{base_url.rstrip('/')}{endpoint}"
            driver.get(url)

            # Step 1: Wait for the page to load completely
            try:
                # You can replace this with a specific element you expect to load
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            except Exception as e:
                print(f"Error waiting for page to load: {url}, {e}")
                continue

            # Step 2: Check for HTTP 200 status
            if driver.current_url != url:
                print(f"Redirected or not accessible: {url}")
                valid_endpoints.append(endpoint)
                continue

            # Step 3: Check for a valid title or content on the page
            page_source = driver.page_source.lower()
            if "dashboard" in page_source or "home" in page_source or "welcome" in page_source:
                print(f"Valid page found: {url}")
            elif "<title>" in page_source:
                title = driver.title.lower()
                if title != "404 not found" and "error" not in title and "unauthorized" not in title:
                    print(f"Valid page found: {url} (title: {title})")
                    valid_endpoints.append(endpoint)

    finally:
        driver.quit()

    return valid_endpoints


# Main function
if __name__ == "__main__":
    print("Broken Access Control Testing Script")

    base_url = input("Enter the base URL of the application (e.g., http://localhost/app): ").strip()
    endpoints_file = input("Enter the file path containing endpoints (e.g., endpoints.txt): ").strip()
    endpoints = load_endpoints(endpoints_file)

    if not endpoints:
        print("No endpoints to test. Exiting.")
    else:
        test_type = input("Choose test type (1 = Unauthorized access via requests, 2 = Forced browsing via Selenium): ").strip()

        if test_type == "1":
            cookies = input("Enter any session cookies for the request (or leave blank for none): ").strip()
            test_broken_access_control(base_url, endpoints, cookies)
        elif test_type == "2":
            forced_browsing(base_url, endpoints)
            print("Forced browsing completed.")
            print("Validating new endpoints for correct pages.")
            valid_endpoints = validate_page(base_url, new_endpoints)
            if valid_endpoints:
                print(f"Valid pages found: {valid_endpoints}")
            else:
                print("No valid pages found.")
        else:
            print("Invalid option selected. Exiting.")
