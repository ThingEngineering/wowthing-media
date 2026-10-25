import csv
import os
import requests

from PIL import Image

from lib import download_blp, read_csv


DOWNLOAD_URL = 'http://localhost:59000/casc/fdid?fileDataID=%s&filename=%s'

PROFESSION_QUALITY_ICONS = [
    ('1', 18335), # Professions-Icon-Quality-Tier1
    ('2', 18330), # Professions-Icon-Quality-Tier2
    ('3', 18334), # Professions-Icon-Quality-Tier3
    ('4', 18348), # Professions-Icon-Quality-Tier4
    ('5', 18349), # Professions-Icon-Quality-Tier5
    ('13', 32403),# Professions-Icon-Quality-12-Tier1
    ('14', 32406),# Professions-Icon-Quality-12-Tier2
]


# Extract relevant icons from WoW atlases (sprite sheets)
# - character races
def main():
    atlas_ids = set()
    element_ids = set()
    filedata_ids = set()
    atlases = {}
    elements = {}

    for _, element_id in PROFESSION_QUALITY_ICONS:
        element_ids.add(element_id)

    # (race_id, sex, ui_texture_atlas_element_id)
    races = []
    for row in read_csv('chrracescreatescreenicon.csv'):
        sex = int(row['Sex'])
        if sex > 1:
            continue

        element_id = int(row['RaceIcon'])
        element_ids.add(element_id)
        races.append((int(row['ChrRacesID']), sex, element_id))

    for row in read_csv('uitextureatlasmember.csv'):
        element_id = int(row['UiTextureAtlasElementID'])
        if element_id not in element_ids:
            continue
        
        elements[element_id] = row
        atlas_ids.add(int(row['UiTextureAtlasID']))
    
    for row in read_csv('uitextureatlas.csv'):
        atlas_id = int(row['ID'])
        if atlas_id not in atlas_ids:
            continue

        filedata_id = int(row['FileDataID'])
        atlases[atlas_id] = filedata_id
        filedata_ids.add(filedata_id)

    # ew but whatever
    images = {}
    def get_cropped_image(element_id):
        element = elements[element_id]
        if element is None:
            print(f'Missing element : {element_id}')
            return None
        
        atlas_id = int(element['UiTextureAtlasID'])
        filedata_id = atlases[atlas_id]
        if filedata_id is None:
            print(f'Missing atlas for element {element_id}: {atlas_id}')
            return None

        filepath = download_blp(filedata_id)
        if filepath is None:
            return None

        if filepath not in images:
            im = open_image(filepath)
            if im is None:
                return None

            images[filepath] = im
        
        # left, upper, right, lower
        box = (
            int(element['CommittedLeft']),
            int(element['CommittedTop']),
            int(element['CommittedRight']),
            int(element['CommittedBottom']),
        )
        cropped = images[filepath].crop((box))
        return cropped

    for quality, element_id in PROFESSION_QUALITY_ICONS:
        cropped = get_cropped_image(element_id)
        if cropped is None:
            continue
            
        out_filepath = os.path.join('raw', f'crafting_quality_{quality}.png')
        cropped.save(out_filepath)

        print(f'Saved {out_filepath}')

    for race_id, sex, element_id in races:
        cropped = get_cropped_image(element_id)
        if cropped is None:
            continue

        out_filepath = os.path.join('raw', f'race_{race_id}_{sex}.png')
        cropped.save(out_filepath)

        print(f'Saved {out_filepath}')


def open_image(filepath):
    try:
        im = Image.open(filepath)
    except Exception as e:
        print('!! UH OH !!', filepath, e)
        return None

    return im


if __name__ == '__main__':
    main()
