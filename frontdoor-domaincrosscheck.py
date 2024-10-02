import csv
from azure.identity import DefaultAzureCredential
from azure.mgmt.frontdoor import FrontDoorManagementClient
from azure.mgmt.resource import SubscriptionClient

# CSV file containing the list of domains to check
CSV_FILE = "domains.csv"

# Output file for the results
OUTPUT_FILE = "domain_frontdoor_check.csv"

# Azure credentials
credential = DefaultAzureCredential()

# Initialize subscription client to list all subscriptions
subscription_client = SubscriptionClient(credential)


def check_domains_in_frontdoor(subscription_id, frontdoor_client, domain_list):
    frontdoor_results = []

    # List all Front Door instances in the subscription
    frontdoors = frontdoor_client.front_doors.list()
    
    for fd in frontdoors:
        # Check for domains in Front Door Designer (Frontend Endpoints)
        for frontend_endpoint in fd.frontend_endpoints:
            frontend_domain = frontend_endpoint.host_name

            if frontend_domain in domain_list:
                frontdoor_results.append({
                    "Domain": frontend_domain,
                    "FrontDoor Name": fd.name,
                    "Subscription ID": subscription_id,
                    "Location": "Frontend (Designer)"
                })

        # Check for domains in Backend Pools
        for backend_pool in fd.backend_pools:
            for backend in backend_pool.backends:
                backend_domain = backend.address
                
                if backend_domain in domain_list:
                    frontdoor_results.append({
                        "Domain": backend_domain,
                        "FrontDoor Name": fd.name,
                        "Subscription ID": subscription_id,
                        "Location": "Backend Pool"
                    })

    return frontdoor_results


def main():
    # Read the domains from the CSV file
    with open(CSV_FILE, mode='r') as file:
        reader = csv.reader(file)
        domain_list = [row[0].strip() for row in reader if row]

    # Create or clear the output file and add headers
    with open(OUTPUT_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Domain", "FrontDoor Name", "Subscription ID", "Location"])

        # Iterate through all subscriptions
        for subscription in subscription_client.subscriptions.list():
            subscription_id = subscription.subscription_id
            print(f"Checking subscription: {subscription_id}")

            # Create a FrontDoorManagementClient for each subscription
            frontdoor_client = FrontDoorManagementClient(credential, subscription_id)

            # Check domains in this subscription's FrontDoor services
            results = check_domains_in_frontdoor(subscription_id, frontdoor_client, domain_list)

            # Write results to the CSV file
            for result in results:
                writer.writerow([result["Domain"], result["FrontDoor Name"], result["Subscription ID"], result["Location"]])

    print(f"Domain check completed. Results saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
