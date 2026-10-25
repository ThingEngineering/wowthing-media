import csv
import os
import os.path
import requests
import shutil


DOWNLOAD_URL = 'http://localhost:59000/casc/fdid?fileDataID=%s&filename=%s'


def download_blp(filedata_id, existing=None):
    maybe_filename = f'{filedata_id}.blp'
    blp_path = os.path.join('blp', maybe_filename)
    
    if (existing is not None and maybe_filename not in existing) or not os.path.exists(blp_path):
        url = DOWNLOAD_URL % (filedata_id, maybe_filename)
        # print(url)
        with requests.get(url, stream=True) as response:
            if response.status_code != 200:
                print(f'Download failed {maybe_filename} => {response.status_code}')
                return None

            with open(blp_path, 'wb') as out_file:
                shutil.copyfileobj(response.raw, out_file)

            print(f'Downloaded {maybe_filename}')

    return blp_path

def read_csv(filename):
    base_path = os.path.join(os.path.abspath(os.path.expanduser(os.environ['WOWTHING_DUMP_PATH'])), 'enUS')
    with open(os.path.join(base_path, os.path.join(base_path), filename), newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            yield row
