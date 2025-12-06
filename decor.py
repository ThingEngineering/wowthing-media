import csv
import os
import os.path
import requests
import shutil

from PIL import Image


DOWNLOAD_URL = 'http://localhost:59000/casc/fdid?fileDataID=%s&filename=%s'


def main():
    base_path = os.path.join(os.path.abspath(os.path.expanduser(os.environ['WOWTHING_DUMP_PATH'])), 'enUS')

    for p in ['decor', 'decor_raw']:
        if not os.path.isdir(p):
            os.mkdir(p)

    for filename in os.listdir('decor'):
        filepath = os.path.join('decor', filename)
        os.remove(filepath)

    decor = {}
    with open(os.path.join(base_path, os.path.join(base_path), 'housedecor.csv'), newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            filedata_id = int(row['ThumbnailFileDataID'])
            if filedata_id > 0:
                decor.setdefault(filedata_id, []).append(int(row['ID']))

    for filedata_id, decor_ids in sorted(decor.items()):
        print(filedata_id, decor_ids)

        blp_name = f'{filedata_id}.blp'
        blp_path = os.path.join('decor_raw', blp_name)

        if not os.path.exists(blp_path):
            print(f'Downloading {blp_name}')
            url = DOWNLOAD_URL % (filedata_id, blp_name)
            with requests.get(url, stream=True) as response:
                if response.status_code == 200:
                    with open(blp_path, 'wb') as out_file:
                        shutil.copyfileobj(response.raw, out_file)
        
        saved = None
        for decor_id in decor_ids:
            decor_path = os.path.join('decor', f'{decor_id}.png')
            if saved:
                os.symlink(saved, decor_path)
            else:
                img = Image.open(blp_path)
                img.save(decor_path)
                saved = decor_path


if __name__ == '__main__':
    main()
