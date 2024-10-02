import csv
from azure.identity import DefaultAzureCredential
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource import SubscriptionClient, ResourceManagementClient

# CSV file containing the list of domains to check
CSV_FILE = "domains.csv"

# Output file for the results
OUTPUT_FILE = "domain_app_gateway_check.csv"

# Azure credentials
credential = DefaultAzureCredential()

# Initialize subscription client to list all subscriptions
subscription_client = SubscriptionClient(credential)

def check_domains_in_application_gateway(subscription_id, network_client, domain_list):
    results = []

    # List all resource groups in the subscription
    resource_client = ResourceManagementClient(credential, subscription_id)
    resource_groups = resource_client.resource_groups.list()

    for resource_group in resource_groups:
        # List all Application Gateway services in the resource group
        app_gateways = network_client.application_gateways.list(resource_group.name)

        for app_gateway in app_gateways:
            # Check the listeners in each Application Gateway
            for listener in app_gateway.http_listeners:
                # Get the domain name (host_name) from the listener
                domain = listener.host_name

                # Check if the domain is in the provided domain list
                if domain in domain_list:
                    results.append({
                        "Domain": domain,
                        "App Gateway Name": app_gateway.name,
                        "Resource Group": resource_group.name,
                        "Subscription ID": subscription_id
                    })

    return results


def main():
    # Read the domains from the CSV file
    with open(CSV_FILE, mode='r') as file:
        reader = csv.reader(file)
        domain_list = [row[0].strip() for row in reader if row]

    # Create or clear the output file and add headers
    with open(OUTPUT_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Domain", "Application Gateway Name", "Resource Group", "Subscription ID"])

        # Iterate through all subscriptions
        for subscription in subscription_client.subscriptions.list():
            subscription_id = subscription.subscription_id
            print(f"Checking subscription: {subscription_id}")

            # Create a NetworkManagementClient for each subscription
            network_client = NetworkManagementClient(credential, subscription_id)

            # Check domains in this subscription's Application Gateway services
            results = check_domains_in_application_gateway(subscription_id, network_client, domain_list)

            # Write results to the CSV file
            for result in results:
                writer.writerow([result["Domain"], result["App Gateway Name"], result["Resource Group"], result["Subscription ID"]])

    print(f"Domain check completed. Results saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
