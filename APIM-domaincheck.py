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


def check_custom_domains_in_apim(subscription_id, apim_client, domain_list):
    apim_results = []

    # List all API Management services in the subscription
    apim_services = apim_client.api_management_service.list()

    for apim in apim_services:
        # Check custom domains in APIM (hostname configurations)
        for hostname_config in apim.hostname_configurations:
            # Get the custom domain
            custom_domain = hostname_config.host_name

            # Check if the custom domain is in the provided domain list
            if custom_domain in domain_list:
                apim_results.append({
                    "Domain": custom_domain,
                    "APIM Service Name": apim.name,
                    "Subscription ID": subscription_id,
                    "Hostname Type": hostname_config.type
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
        writer.writerow(["Domain", "APIM Service Name", "Subscription ID", "Hostname Type"])

        # Iterate through all subscriptions
        for subscription in subscription_client.subscriptions.list():
            subscription_id = subscription.subscription_id
            print(f"Checking subscription: {subscription_id}")

            # Create an ApiManagementClient for each subscription
            apim_client = ApiManagementClient(credential, subscription_id)

            # Check custom domains in this subscription's APIM services
            results = check_custom_domains_in_apim(subscription_id, apim_client, domain_list)

            # Write results to the CSV file
            for result in results:
                writer.writerow([result["Domain"], result["APIM Service Name"], result["Subscription ID"], result["Hostname Type"]])

    print(f"Domain check completed. Results saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
