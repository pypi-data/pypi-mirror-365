import sys
import requests
import keyring

# Constants
BITLY_API_URL = "https://api-ssl.bitly.com/v4/shorten"
SERVICE_ID = "linkmod"

def get_api_key():
    """Retrieves the Bitly API key from the system's keyring."""
    return keyring.get_password(SERVICE_ID, "bitly_api_key")

def set_api_key(api_key):
    """Saves the Bitly API key to the system's keyring."""
    keyring.set_password(SERVICE_ID, "bitly_api_key", api_key)

def shorten_link(api_key, long_url):
    """Shortens a URL using the Bitly API."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "long_url": long_url,
    }
    try:
        response = requests.post(BITLY_API_URL, headers=headers, json=payload, timeout=10)
        if response.status_code in [200, 201]:
            return response.json().get("link")
        else:
            return f"Error: {response.status_code} - {response.text}"
    except requests.exceptions.ConnectionError:
        return "Error: Connection failed - Unable to reach Bitly API"
    except requests.exceptions.Timeout:
        return "Error: Request timed out - Bitly API is not responding"
    except requests.exceptions.RequestException as e:
        return f"Error: Network error - {str(e)}"

def main():
    """Main function for the linkMod tool."""
    # Handle setting the API key
    if len(sys.argv) == 2 and sys.argv[1] == '--set-key':
        new_api_key = input("Please enter your Bitly API key: ")
        if new_api_key:
            set_api_key(new_api_key)
            print("Bitly API key saved successfully.")
        else:
            print("No API key entered.")
        return

    # Handle combined shortening and custom link creation
    if len(sys.argv) == 3:
        long_url = sys.argv[1]
        custom_name = sys.argv[2]
        
        print("Checking for Bitly API key...")
        api_key = get_api_key()
        
        link_to_use = long_url
        
        if api_key:
            print("Bitly API key found. Shortening link...")
            shortened_link = shorten_link(api_key, long_url)
            if shortened_link and not shortened_link.startswith("Error:"):
                link_to_use = shortened_link
                print("Link shortened successfully.")
            else:
                print(f"Could not shorten link: {shortened_link}")
                print("Using original link for custom name.")
        else:
            print("Bitly API key not found. Use 'linkMod --set-key' to add one.")

        # Remove 'https://' if present from the link we are actually using
        if link_to_use.startswith("https://"):
            link_to_use = link_to_use[8:]
        
        # Combine the custom link and original/shortened link
        final_link = custom_name + "@" + link_to_use
        print(final_link)
        return

    # Handle Bitly URL shortening only
    if len(sys.argv) == 2:
        long_url = sys.argv[1]
        api_key = get_api_key()

        # Prompt to add a key if one is not found
        if not api_key:
            choice = input("Bitly API key not found. Would you like to add one? (y/n): ").lower()
            if choice == 'y':
                new_api_key = input("Please enter your Bitly API key: ")
                if new_api_key:
                    set_api_key(new_api_key)
                    api_key = new_api_key  # Use the new key for the current session
                    print("API key saved successfully.")

        if api_key:
            short_link = shorten_link(api_key, long_url)
            if short_link.startswith("Error:"):
                print(f"Could not shorten link: {short_link}")
                print(f"Original link: {long_url}")
            else:
                print(f"Short link: {short_link}")
        else:
            print("No Bitly API key found. Returning original link.")
            print(f"Original link: {long_url}")
        return

    # If argument count is incorrect, show usage
    print("Usage:")
    print("  To shorten a URL: linkMod {long_url}")
    print("  To create a custom link (and shorten if possible): linkMod {link} {custom_name}")
    print("  To set/update your Bitly API key: linkMod --set-key")

if __name__ == "__main__":
    main()
