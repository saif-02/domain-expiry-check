import requests
import datetime
from collections import defaultdict

# Configuration
VENAFI_URL = "https://<your-venafi-server>/vedsdk"  # Replace with your Venafi server URL
USERNAME = "<your-username>"  # Replace with your username
PASSWORD = "<your-password>"  # Replace with your password

def authenticate():
    url = f"{VENAFI_URL}/Authorize/"
    payload = {
        "Username": USERNAME,
        "Password": PASSWORD
    }
    response = requests.post(url, json=payload)
    response.raise_for_status()
    return response.json().get("APIKey")

def fetch_certificates(api_key, start_date, end_date):
    url = f"{VENAFI_URL}/Certificates/"
    headers = {"Authorization": f"Bearer {api_key}"}
    params = {
        "CreationDateStart": start_date.isoformat(),
        "CreationDateEnd": end_date.isoformat()
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json().get("Certificates", [])

def generate_report(certificates):
    counts = defaultdict(int)
    for cert in certificates:
        if cert.get("Renewal"):
            counts['renewed'] += 1
        else:
            counts['created'] += 1
    return counts

def main():
    try:
        # Authenticate and get API key
        api_key = authenticate()

        # Define date ranges
        today = datetime.date.today()
        first_of_this_month = today.replace(day=1)
        first_of_last_month = (first_of_this_month - datetime.timedelta(days=1)).replace(day=1)
        end_of_last_month = first_of_this_month - datetime.timedelta(days=1)

        # Fetch data
        last_month_certificates = fetch_certificates(api_key, first_of_last_month, end_of_last_month)
        this_month_certificates = fetch_certificates(api_key, first_of_this_month, today)

        # Generate report
        last_month_report = generate_report(last_month_certificates)
        this_month_report = generate_report(this_month_certificates)

        # Print report
        print("Last Month Report:")
        print(f"Total Created: {last_month_report['created']}, Total Renewed: {last_month_report['renewed']}")

        print("\nThis Month Report:")
        print(f"Total Created: {this_month_report['created']}, Total Renewed: {this_month_report['renewed']}")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
