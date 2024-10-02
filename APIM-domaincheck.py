import csv
from azure.identity import DefaultAzureCredential
from azure.mgmt.apimanagement import ApiManagementClient
from azure.mgmt.resource import SubscriptionClient

# CSV file containing the list of domains to check
CSV_FILE = "domains.csv"

# Output file for the results
OUTPUT_FILE = "domain_apim_check.csv"

# Azure credentials
credential = DefaultAzureCredential()

# Initialize subscription client to list all subscriptions
subscription_client = SubscriptionClient(credential)


def check_domains_in_apim(subscription_id, apim_client, domain_list):
    apim_results = []

    # List all API Management services in the subscription
    apim_services = apim_client.api_management_service.list()

    for apim in apim_services:
        # Check for custom domains in APIM (for Gateway, Management Portal, Developer Portal, SCM)
        custom_domains = [
            apim.hostname_configurations.gateway,  # Gateway domain
            apim.hostname_configurations.management,  # Management portal domain
            apim.hostname_configurations.developer_portal,  # Developer portal domain
            apim.hostname_configurations.portal  # SCM domain
        ]

        for domain in custom_domains:
            # Check if the domain is in the provided list
            if domain and domain.host_name in domain_list:
                apim_results.append({
                    "Domain": domain.host_name,
                    "APIM Service Name": apim.name,
                    "Subscription ID": subscription_id
                })

    return apim_results


def main():
    # Read the domains from the CSV file
    with open(CSV_FILE, mode='r') as file:
        reader = csv.reader(file)
        domain_list = [row[0].strip() for row in reader if row]

    # Create or clear the output file and add headers
    with open(OUTPUT_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Domain", "APIM Service Name", "Subscription ID"])

        # Iterate through all subscriptions
        for subscription in subscription_client.subscriptions.list():
            subscription_id = subscription.subscription_id
            print(f"Checking subscription: {subscription_id}")

            # Create an ApiManagementClient for each subscription
            apim_client = ApiManagementClient(credential, subscription_id)

            # Check domains in this subscription's APIM services
            results = check_domains_in_apim(subscription_id, apim_client, domain_list)

            # Write results to the CSV file
            for result in results:
                writer.writerow([result["Domain"], result["APIM Service Name"], result["Subscription ID"]])

    print(f"Domain check completed. Results saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
