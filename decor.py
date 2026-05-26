import csv
import os
import os.path
import requests
import shutil
import subprocess

from PIL import Image


DOWNLOAD_URL = 'http://localhost:59000/casc/fdid?fileDataID=%s&filename=%s'


def main():
    base_path = os.path.join(os.path.abspath(os.path.expanduser(os.environ['WOWTHING_DUMP_PATH'])), 'enUS')

    for p in ['decor', 'decor_raw']:
        if not os.path.isdir(p):
            os.mkdir(p)

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
                else:
                    print(response.status_code)
                    continue
        
        saved_png = None
        saved_webp = None
        for decor_id in decor_ids:
            png_path = os.path.join('decor', f'{decor_id}.png')
            webp_path = os.path.join('decor', f'{decor_id}.webp')
            if saved_png:
                if os.path.exists(png_path) and not os.path.islink(png_path):
                    os.remove(png_path)
                    os.symlink(saved_png, png_path)

                if os.path.exists(webp_path) and not os.path.islink(webp_path):
                    os.remove(webp_path)
                    os.symlink(saved_webp, webp_path)
            else:
                if not os.path.exists(png_path):
                    print(f'- creating {png_path}')
                    try:
                        img = Image.open(blp_path)
                    except Exception as e:
                        print(f'-- KABOOM: {e}')
                        continue
                    img.save(png_path)
                
                if not os.path.exists(webp_path):
                    print(f'- creating {webp_path}')
                    subprocess.run([
                        'cwebp',
                        '-q',
                        '85',
                        '-quiet',
                        png_path,
                        '-o',
                        webp_path,
                    ])

                saved_png = os.path.basename(png_path)
                saved_webp = os.path.basename(webp_path)


if __name__ == '__main__':
    main()
