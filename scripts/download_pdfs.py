import os
import requests
import operator as op
from dotenv import load_dotenv

load_dotenv(override=True)
LSE_USERNAME = os.environ["LSE_USERNAME"]
LSE_PASSWORD = os.environ["LSE_PASSWORD"]
DATA_FOLDER = os.environ["OFFLINE_PDFS_DIR"]

# Get the list of files that the crawler was unable to download
# with open('data/error_downloads.jsonl', 'r') as file_list:
with open('data/pdf_list.txt', 'r') as file_list:

    for line in file_list:
        # Clean the url
        url = line.strip().strip('\"')
        title = url.split('/')[-1]

        # Do not include any documents that are not in the LSE domain - for this purposes that means anything without "lse.ac.uk" in the address
        if op.contains(url, 'lse.ac.uk'):
            # Exclude anything from the "personal.lse.ac.uk" subdomain - these are personal blog pages etc
            if not (op.contains(url, 'personal.lse.ac.uk')):
                # Exclude anything from the "eprints.lse.ac.uk" subdomain - these are research papers
                if not (op.contains(url, 'eprints.lse.ac.uk')):
                    try:
                        response = requests.get(
                            url, auth=(LSE_USERNAME, LSE_PASSWORD))

                        if response.status_code == 200:
                            filename = os.path.join(DATA_FOLDER, title)

                            try:
                                with open(filename, 'xb') as local_file:
                                    local_file.write(response.content)
                                    print(
                                        f'File downloaded successfully: {url}')
                            except FileExistsError:
                                print(f'File already downloaded: {url}')
                                pass

                        else:
                            print(
                                f'Failed to download file because {response.status_code}: {url}')

                    except Exception as e:
                        print(f'Error {e} prevents access: {url}')
