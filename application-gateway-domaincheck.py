import csv
from azure.identity import DefaultAzureCredential
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource import SubscriptionClient, ResourceManagementClient

# CSV file containing the list of domains to check
CSV_FILE = "domains.csv"

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
        print(f"Checking resource group: {resource_group.name}")  # Debugging output

        # List all Application Gateway services in the resource group
        app_gateways = network_client.application_gateways.list(resource_group.name)

        for app_gateway in app_gateways:
            print(f"Found Application Gateway: {app_gateway.name}")  # Debugging output

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

    # Create a list to store all results
    all_results = []

    # Iterate through all subscriptions
    for subscription in subscription_client.subscriptions.list():
        subscription_id = subscription.subscription_id
        print(f"Checking subscription: {subscription_id}")

        # Create a NetworkManagementClient for each subscription
        network_client = NetworkManagementClient(credential, subscription_id)

        # Check domains in this subscription's Application Gateway services
        results = check_domains_in_application_gateway(subscription_id, network_client, domain_list)

        # Append results to the all_results list
        all_results.extend(results)

    # Write results to the same CSV file
    with open(CSV_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        # Write a header for results if there are any
        if all_results:
            writer.writerow(["Domain", "Application Gateway Name", "Resource Group", "Subscription ID"])
            for result in all_results:
                writer.writerow([result["Domain"], result["App Gateway Name"], result["Resource Group"], result["Subscription ID"]])

    print(f"Domain check completed. Results appended to {CSV_FILE}")


if __name__ == "__main__":
    main()
