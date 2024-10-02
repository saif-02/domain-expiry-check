# Domain SSL Certificate Information Script

This Bash script is designed to check SSL certificate information for a list of domains specified in a CSV file and output the details into another CSV file. The script retrieves the Common Name, Issued On date, Expiration Date, Organization, and Organization Unit of the SSL certificates for each domain.

## Prerequisites

1. **OpenSSL**: Ensure that OpenSSL is installed on your system. It is used to fetch SSL certificate details.

2. **CSV File**: A CSV file named `domain.csv` should be present in the same directory as the script. This file should contain a list of domain names, each on a new line.

## How the Script Works

1. **Input File**: The script reads domains from the `domain.csv` file.
   - The file should contain one domain per line.
   
2. **Output File**: The script writes the SSL certificate information for each domain to `domain_cert_info.csv`.
   - The output CSV file contains the following columns:
     - Domain
     - Common Name (CN)
     - Issued On (Certificate start date)
     - Expiration Date (Certificate end date)
     - Organization (O)
     - Organization Unit (OU)

3. **Certificate Retrieval**:
   - The script uses OpenSSL to connect to each domain on port 443 (HTTPS) and retrieves the SSL certificate details.
   - If the script cannot retrieve the certificate information, it logs an error for that domain in the output file.

4. **Headers**: The output CSV file includes headers to label the columns.

## Script Workflow

1. **Check CSV File**: The script checks if the `domain.csv` file exists. If not, it terminates with an error message.
   
2. **Clear/Create Output File**: If the output file `domain_cert_info.csv` exists, it clears the content and writes headers to the file.

3. **Loop Through Domains**: 
   - The script reads each domain from `domain.csv`.
   - For each domain, it calls OpenSSL to retrieve the certificate information.
   
4. **Extract Certificate Data**:
   - The script extracts relevant data, including:
     - Common Name (CN)
     - Issued On date
     - Expiration Date
     - Organization (O)
     - Organization Unit (OU)
     
5. **Handle Missing Data**: If an Organization or Organization Unit is not available, the script fills in "N/A" for those fields.

6. **Write Results**: The certificate information for each domain is written to `domain_cert_info.csv`.

7. **Completion**: The script outputs a message indicating the check is complete and the results are saved.

## Usage

1. Create a file named `domain.csv` in the same directory as the script, containing the list of domains to check.
   
2. Run the script:
   ```bash
   ./your_script_name.sh
