import csv
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import SubscriptionClient
from azure.mgmt.frontdoor import FrontDoorManagementClient
from azure.core.exceptions import HttpResponseError

# Authenticate using default credentials (works with Azure CLI, environment vars, etc.)
credential = DefaultAzureCredential()

# Initialize the subscription client to list all subscriptions
subscription_client = SubscriptionClient(credential)

# Define CSV file path
csv_file_path = "frontdoor_data.csv"

# Function to extract resource group from resource ID
def extract_resource_group(resource_id):
    parts = resource_id.split('/')
    return parts[4] if len(parts) > 4 else "Unknown"

# Open CSV file for writing
with open(csv_file_path, mode='w', newline='') as file:
    writer = csv.writer(file)

    # Write CSV headers
    writer.writerow(["Subscription ID", "Subscription Name", "Front Door Name", "Resource Group", "Location", "Associated Domain"])

    # Iterate over all subscriptions
    try:
        for subscription in subscription_client.subscriptions.list():
            subscription_id = subscription.subscription_id
            subscription_name = subscription.display_name
            print(f"Fetching data for Subscription: {subscription_name} ({subscription_id})")

            try:
                # Initialize the Front Door management client for the specific subscription
                frontdoor_client = FrontDoorManagementClient(credential, subscription_id)

                # Fetch all Front Doors in the current subscription
                frontdoors = frontdoor_client.front_doors.list()

                # Check if there are any Front Doors in this subscription
                frontdoor_list = list(frontdoors)  # Convert to list to check contents
                if not frontdoor_list:
                    print(f"No Front Doors found in Subscription: {subscription_name}")
                    continue

                for fd in frontdoor_list:
                    front_door_name = fd.name
                    resource_group = extract_resource_group(fd.id)  # Extract resource group from resource ID
                    location = fd.location

                    # List the associated domains for the Front Door
                    if fd.frontend_endpoints:
                        for endpoint in fd.frontend_endpoints:
                            # Write the row to the CSV file for each associated domain
                            writer.writerow([subscription_id, subscription_name, front_door_name, resource_group, location, endpoint.host_name])
                    else:
                        # If no associated domain, write a row indicating that
                        writer.writerow([subscription_id, subscription_name, front_door_name, resource_group, location, "No associated domains found"])

            except HttpResponseError as e:
                print(f"Error fetching Front Door data for subscription {subscription_name}: {e}")

    except HttpResponseError as e:
        print(f"Error fetching subscriptions: {e}")

print(f"Front Door data exported successfully to {csv_file_path}")
