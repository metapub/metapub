import csv
import requests

def download_file(url, local_path):
    response = requests.get(url)
    with open(local_path, 'wb') as file:
        file.write(response.content)

def parse_journal_info(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Split the content by the separator line
    journal_entries = content.strip().split('--------------------------------------------------------\n')
    
    # Prepare to write to a CSV file
    output_file = '/tmp/journals.csv'
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['JrId', 'JournalTitle', 'MedAbbr', 'ISSN (Print)', 'ISSN (Online)', 'IsoAbbr', 'NlmId']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for entry in journal_entries:
            if entry.strip():  # Ensure entry is not empty
                journal_info = {}
                for line in entry.split('\n'):
                    if line.strip():  # Ensure line is not empty
                        key, value = line.split(': ', 1)
                        journal_info[key] = value
                writer.writerow(journal_info)
    
    print(f"CSV file '{output_file}' created successfully.")

# URL of the file to be downloaded
url = 'https://ftp.ncbi.nih.gov/pubmed/J_Medline.txt'
# Path to save the downloaded file
local_file_path = '/tmp/J_Medline.txt'

# Download the file
download_file(url, local_file_path)

# Parse the downloaded file and create CSV
parse_journal_info(local_file_path)

