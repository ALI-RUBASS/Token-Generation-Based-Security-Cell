from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests
import getpass
from webdriver_manager.chrome import ChromeDriverManager


# Authenticate and get a session for restricted areas
def authenticate_and_get_session(url, username, password):
    login_url = f"{url}/rest/user/login"
    payload = {"email": username, "password": password}
    session = requests.Session()

    try:
        response = session.post(login_url, json=payload)
        if response.status_code == 200:
            print("Logged in successfully!")
            return session
        else:
            print(f"Login failed: {response.text}")
    except Exception as e:
        print(f"Error during login: {e}")
    return None


# Add cookies from requests.Session to Selenium WebDriver
def add_cookies_to_selenium(driver, session, domain):
    cookies = session.cookies.get_dict()
    for key, value in cookies.items():
        driver.add_cookie({"name": key, "value": value, "domain": domain})


# Fetch dynamic content using Selenium and session cookies
def fetch_dynamic_content(url, session=None):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(url)

    if session:
        domain = url.split("//")[-1].split("/")[0]
        add_cookies_to_selenium(driver, session, domain)
        driver.refresh()

    page_source = driver.page_source
    driver.quit()
    return BeautifulSoup(page_source, 'html.parser')


# Detect CSRF vulnerabilities in forms
def detect_csrf(url, session=None):
    print(f"Scanning {url} for CSRF vulnerabilities...")
    soup = fetch_dynamic_content(url, session=session)

    forms = soup.find_all('form')
    results = {
        "forms_analyzed": len(forms),
        "csrf_vulnerabilities": []
    }

    if len(forms) == 0:
        print("No forms detected on the page.")
        return results

    for form in forms:
        action = form.get('action')
        method = form.get('method', 'get').lower()
        inputs = form.find_all('input')

        # Convert relative URLs to absolute URLs
        action_url = urljoin(url, action) if action else url

        has_csrf_token = False
        for input_field in inputs:
            if input_field.get('type') == 'hidden' and 'csrf' in input_field.get('name', '').lower():
                has_csrf_token = True
                break

        if not has_csrf_token:
            vulnerability = {
                "action": action_url,
                "method": method,
                "inputs": [inp.get('name') for inp in inputs]
            }
            results["csrf_vulnerabilities"].append(vulnerability)

    return results


# Main function
if __name__ == "__main__":
    # Get URL, username, and password from the user
    target_url = input("Enter the URL to test (e.g., http://example.com): ")
    username = input("Enter the username for login: ")
    password = getpass.getpass("Enter the password for login (input will be hidden): ")

    # Authenticate and retrieve session
    session = authenticate_and_get_session(target_url, username, password)

    # If authentication is successful, scan restricted pages
    if session:
        results = detect_csrf(target_url, session=session)
        print(f"Forms Analyzed: {results['forms_analyzed']}")
        if results["csrf_vulnerabilities"]:
            print("CSRF vulnerabilities detected:")
            for vuln in results["csrf_vulnerabilities"]:
                print(f"- Form action: {vuln['action']}, method: {vuln['method']}, inputs: {vuln['inputs']}")
        else:
            print("No CSRF vulnerabilities detected.")
