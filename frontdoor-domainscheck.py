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

    # Write the initial CSV headers (we'll update this later if needed)
    base_headers = ["Subscription ID", "Subscription Name", "Front Door Name", "Resource Group", "Location"]
    writer.writerow(base_headers)

    # Variable to track maximum number of front-ends, backends, and domains across all Front Doors
    max_frontends = 0
    max_backends = 0
    max_domains = 0

    # Store rows temporarily so that we can expand the headers later
    rows = []

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

                    # Fetch the frontend endpoints (domains) associated with this Front Door
                    frontends = [endpoint.host_name for endpoint in fd.frontend_endpoints] if fd.frontend_endpoints else []
                    # Fetch the backend pools associated with this Front Door
                    backends = [backend.name for backend in fd.backend_pools] if fd.backend_pools else []
                    # For designer domains (assuming they're frontend endpoints), it's already handled in frontends

                    # Track the maximum numbers for dynamic CSV columns
                    max_frontends = max(max_frontends, len(frontends))
                    max_backends = max(max_backends, len(backends))

                    # Prepare the row with the basic data
                    row = [subscription_id, subscription_name, front_door_name, resource_group, location]

                    # Append frontend endpoints (domains)
                    row.extend(frontends)

                    # Append backend pools
                    row.extend(backends)

                    # Store the row
                    rows.append(row)

            except HttpResponseError as e:
                print(f"Error fetching Front Door data for subscription {subscription_name}: {e}")

    except HttpResponseError as e:
        print(f"Error fetching subscriptions: {e}")

    # Update the CSV headers to include dynamic columns based on max_frontends and max_backends
    frontend_headers = [f"Frontend Domain {i + 1}" for i in range(max_frontends)]
    backend_headers = [f"Backend Pool {i + 1}" for i in range(max_backends)]
    full_headers = base_headers + frontend_headers + backend_headers
    print(f"Writing headers: {full_headers}")

    # Rewrite the headers with frontend and backend columns
    file.seek(0)
    writer.writerow(full_headers)

    # Write the actual rows
    for row in rows:
        # Ensure each row has enough columns to match the headers (fill with empty strings if needed)
        row.extend([""] * (len(full_headers) - len(row)))
        writer.writerow(row)

print(f"Front Door data exported successfully to {csv_file_path}")
