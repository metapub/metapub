import os
import pkg_resources

# Function to load journal names from a text file
def load_journals_from_file(publisher):
    resource_package = 'metapub' # Name of the current package
    resource_path = f'publisher_lists/{publisher}.txt'  # Relative path to the resource
    # print(resource_path)

    out = []
    try:
        # Check if the file exists in the package
        if not pkg_resources.resource_exists(resource_package, resource_path):
            print(f"File {publisher}.txt not found in the package.")
            return []

        journal_names = pkg_resources.resource_string(resource_package, resource_path).decode('utf-8')
        for line in journal_names.splitlines():
            journal_name = line.strip()
            if journal_name:
                out.append(journal_name)
    except FileNotFoundError:
        print(f"File {publisher}.txt not found.")
        return []

    return out

