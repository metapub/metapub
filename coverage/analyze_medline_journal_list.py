import csv

MEDLINE_JOURNAL_LIST = "/tmp/journals.csv"

def compare_abbreviations(file_path):
    same_count = 0
    different_count = 0
    
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['MedAbbr'] == row['IsoAbbr']:
                same_count += 1
            else:
                different_count += 1

    return same_count, different_count

same_count, different_count = compare_abbreviations(MEDLINE_JOURNAL_LIST)
print(f"Entries with the same abbreviations: {same_count}")
print(f"Entries with different abbreviations: {different_count}")

