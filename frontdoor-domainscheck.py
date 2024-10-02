import csv
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import SubscriptionClient
from azure.mgmt.frontdoor import FrontDoorManagementClient

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
    for subscription in subscription_client.subscriptions.list():
        subscription_id = subscription.subscription_id
        subscription_name = subscription.display_name
        print(f"Fetching data for Subscription: {subscription_name} ({subscription_id})")

        # Initialize the Front Door management client for the specific subscription
        frontdoor_client = FrontDoorManagementClient(credential, subscription_id)

        # Fetch all Front Doors in the current subscription
        frontdoors = frontdoor_client.front_doors.list()

        for fd in frontdoors:
            front_door_name = fd.name
            resource_group = extract_resource_group(fd.id)  # Extract resource group from resource ID
            location = fd
