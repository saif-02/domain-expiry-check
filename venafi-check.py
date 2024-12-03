import requests
from datetime import datetime, timedelta
import csv

# Replace with your Venafi instance details
BASE_URL = "https://<venafi-instance-url>/vedsdk"
API_KEY = "<your-api-key>"
GROUP_FOLDERS = ["GroupFolder1", "GroupFolder2"]  # Replace with your group folder names

# Function to fetch certificates from a specific folder within a date range
def fetch_certificates(folder, start_date=None, end_date=None):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    query = {
        "Expression": {
            "Operator": "AND",
            "Operands": [
                {"Field": "ParentFolder", "Operator": "EQUALS", "Value": folder}
            ]
        }
    }

    # Add date filters to the query if provided
    if start_date and end_date:
        date_filter = {
            "Field": "ValidationDate",
            "Operator": "BETWEEN",
            "Value": [start_date, end_date]
        }
        query["Expression"]["Operands"].append(date_filter)

    response = requests.post(f"{BASE_URL}/Certificates/Search", json=query, headers=headers)

    if response.status_code == 200:
        return response.json().get("Certificates", [])
    else:
        print(f"Error fetching certificates for {folder}: {response.status_code}, {response.text}")
        return []

# Function to calculate certificate counts for a specific time range
def calculate_cert_counts():
    now = datetime.utcnow()
    first_day_this_month = now.replace(day=1)
    first_day_last_month = (first_day_this_month - timedelta(days=1)).replace(day=1)
    last_day_last_month = first_day_this_month - timedelta(days=1)

    start_last_month = first_day_last_month.strftime("%Y-%m-%dT00:00:00Z")
    end_last_month = last_day_last_month.strftime("%Y-%m-%dT23:59:59Z")
    start_this_month = first_day_this_month.strftime("%Y-%m-%dT00:00:00Z")
    end_this_month = now.strftime("%Y-%m-%dT23:59:59Z")

    last_month_total = 0
    this_month_total = 0

    for folder in GROUP_FOLDERS:
        # Fetch counts for last month
        last_month_certs = fetch_certificates(folder, start_date=start_last_month, end_date=end_last_month)
        last_month_total += len(last_month_certs)

        # Fetch counts for this month
        this_month_certs = fetch_certificates(folder, start_date=start_this_month, end_date=end_this_month)
        this_month_total += len(this_month_certs)

    return last_month_total, this_month_total

# Function to write all certificates to a CSV
def write_to_csv(certificates, output_file):
    with open(output_file, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Certificate ID", "Common Name", "Subject", "Serial Number", "Expiration Date", "Subdomains"])
        for cert in certificates:
            writer.writerow([
                cert.get("CertificateId"),
                cert.get("CommonName"),
                cert.get("Subject"),
                cert.get("SerialNumber"),
                cert.get("ValidTo"),
                cert.get("SubjAltNames", {}).get("DnsNames", [])
            ])

def main():
    print("Calculating certificate counts...")
    last_month_count, this_month_count = calculate_cert_counts()
    difference = this_month_count - last_month_count

    print(f"Last Month Total: {last_month_count}")
    print(f"Current Month Total: {this_month_count}")
    print(f"Difference: {difference}")

    # Optionally, export all certificates to a CSV (if needed)
    # all_certificates = []
    # for folder in GROUP_FOLDERS:
    #     certificates = fetch_certificates(folder)
    #     all_certificates.extend(certificates)
    # write_to_csv(all_certificates, "venafi_certificates.csv")

if __name__ == "__main__":
    main()
