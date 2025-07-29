from metapub.urlreverse.urlreverse import *
import os

# Handle path resolution - script can be run from bin/ or project root
test_file_paths = [
    'tests/urlreverse_test_urls.txt',  # From project root
    '../tests/urlreverse_test_urls.txt'  # From bin/ directory
]

urllist = None
for path in test_file_paths:
    if os.path.exists(path):
        urllist = open(path).read().split('\n')
        print(f"Reading URLs from: {path}")
        break

if urllist is None:
    print("Error: Could not find urlreverse_test_urls.txt file")
    print("Tried paths:", test_file_paths)
    exit(1)

for url in [item for item in urllist if item.strip() != '']:
    print(url)
    try:
        urlrev = UrlReverse(url)
        print('doi:', urlrev.doi)
        print('pmid:', urlrev.pmid)

        for step in urlrev.steps:
            print('     * %s' % step)

        print()
        # Handle JSON serialization of info dict containing function objects
        try:
            import json
            
            # Create a copy of info dict and convert functions to their names
            info_copy = {}
            for key, value in urlrev.info.items():
                if callable(value):
                    info_copy[key] = value.__name__
                else:
                    info_copy[key] = value
            
            print(json.dumps(info_copy, indent=2))
        except Exception as json_error:
            # Fallback to regular dict representation without JSON formatting
            print("Info dict (non-JSON):")
            for key, value in urlrev.info.items():
                if callable(value):
                    print(f"  {key}: {value.__name__} (function)")
                else:
                    print(f"  {key}: {value}")
            
    except Exception as error:
        print(error)

    print()

