#!/bin/bash

# Path to the CSV file containing domains
CSV_FILE="domain.csv"

# Output file for the results
OUTPUT_FILE="domain_cert_info.csv"

# Check if the CSV file exists
if [[ ! -f "$CSV_FILE" ]]; then
  echo "CSV file not found!"
  exit 1
fi

# Create or clear the output file and add headers
echo "Domain,Common Name,Issued On,Expiration Date,Organization,Organization Unit" > "$OUTPUT_FILE"

# Function to check certificate information
check_certificate() {
  domain=$1

  # Use openssl to get the certificate information
  cert_info=$(echo | openssl s_client -servername "$domain" -connect "$domain:443" 2>/dev/null | openssl x509 -noout -dates -subject)

  # Check if the certificate info was retrieved
  if [[ -z "$cert_info" ]]; then
    echo "$domain,Failed to retrieve certificate,,,,," >> "$OUTPUT_FILE"
    return
  fi

  # Extract the expiration date, issued on, common name, organization, and organization unit
  expiration_date=$(echo "$cert_info" | grep "notAfter=" | cut -d'=' -f2)
  issued_on=$(echo "$cert_info" | grep "notBefore=" | cut -d'=' -f2)
  common_name=$(echo "$cert_info" | grep "subject=" | sed -n 's/.*CN=\([^,]*\).*/\1/p')
  organization=$(echo "$cert_info" | grep "subject=" | sed -n 's/.*O=\([^,]*\).*/\1/p')
  organization_unit=$(echo "$cert_info" | grep "subject=" | sed -n 's/.*OU=\([^,]*\).*/\1/p')

  # If Organization or Organization Unit is not available, set it as "N/A"
  if [[ -z "$organization" ]]; then
    organization="N/A"
  fi
  if [[ -z "$organization_unit" ]]; then
    organization_unit="N/A"
  fi

  # Output the result to the CSV file
  echo "$domain,$common_name,$issued_on,$expiration_date,$organization,$organization_unit" >> "$OUTPUT_FILE"
}

# Loop through each domain in the CSV file
while IFS= read -r domain; do
  # Skip empty lines
  if [[ -z "$domain" ]]; then
    continue
  fi

  # Call the function to check the certificate
  check_certificate "$domain"

done < "$CSV_FILE"

echo "Certificate check completed. Results saved to $OUTPUT_FILE"
