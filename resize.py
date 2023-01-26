import csv
import os
import os.path

from PIL import Image


SIZES = [
    16,
    20,
    24,
    32,
    40,
    48,
]
SUBDIRS = [
    'item',
    'npc',
    'spell',
]


for size in SIZES:
    s = str(size)
    if not os.path.isdir(s):
        os.mkdir(s)

    for subdir in SUBDIRS:
        p = os.path.join(s, subdir)
        if not os.path.isdir(p):
            os.mkdir(p)


def maybe_save(ids, img, outdir, prefix):
    outfile = '%s.png' % (ids[0])
    outpath = os.path.join(outdir, prefix, outfile)
    if not os.path.exists(outpath):
        resized.save(outpath)

    for id in ids[1:]:
        linkname = '%s.png' % (id)
        if linkname in existing[size]:
            continue

        linkpath = os.path.join(outdir, prefix, linkname)
        if linkpath in existing[size]:
            continue
        
        try:
            os.symlink(outfile, linkpath)
        except:
            pass


# custom images
for filename in sorted(os.listdir('raw')):
    filepath = os.path.join('raw', filename)

    im = Image.open(filepath)

    if filename.startswith('race_'):
        # left, upper, right, lower
        im = im.crop((3, 3, 117, 117))

    elif filename == 'inv_misc_questionmark.png' or filename.startswith('affix_') or filename.startswith('dungeon_') or filename.startswith('spec_'):
        im = im.crop((3, 3, 61, 61))

    print('Processing', filepath, im.size)

    for size in SIZES:
        sizePath = os.path.join(str(size), filename)
        if not os.path.exists(sizePath):
            resized = im.copy()
            resized.thumbnail((size, size), Image.ANTIALIAS)
            resized.save(sizePath)


print('----')


existing = {}
for size in SIZES:
    s = str(size)
    existing[size] = set(os.listdir(s))

    for subdir in SUBDIRS:
        p = os.path.join(s, subdir)
        existing[size] = existing[size] | set(os.path.join(subdir, sigh) for sigh in os.listdir(p))


filedata_ids = set()

# Load battlepetspecies
pets = {}
with open('battlepetspecies.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        pets.setdefault(row['IconFileDataID'], []).append(row['CreatureID'])

print('Loaded battlepetspecies')

# load spellmisc
spells = {}
with open('spellmisc.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        if row['SpellID'] != '0' and row['SpellIconFileDataID'] != '0':
            spells.setdefault(row['SpellIconFileDataID'], []).append(row['SpellID'])

print('Loaded spellmisc')

# load item
items = {}
item_to_filedata = {}
with open('item.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        items.setdefault(row['IconFileDataID'], []).append(row['ID'])
        item_to_filedata[row['ID']] = row['IconFileDataID']

print('Loaded item')

# load itemappearance
appearance_to_filedata = {}
with open('itemappearance.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        appearance_to_filedata[row['ID']] = row['DefaultIconFileDataID']

print('Loaded itemappearance')

# load itemmodifiedappearance
item_to_appearance = {}
with open('itemmodifiedappearance.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        if row['ItemAppearanceID'] in appearance_to_filedata:
            ima_filedata = appearance_to_filedata[row['ItemAppearanceID']]
            items.setdefault(ima_filedata, []).append(row['ItemID'])
            item_to_filedata[row['ItemID']] = ima_filedata

print('Loaded itemmodifiedappearance')

# load toy
toys = {}
with open('toy.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        if row['ItemID'] in item_to_filedata:
            toys.setdefault(item_to_filedata[row['ItemID']], []).append(row['ItemID'])

print('Loaded toy')

# load filedata
filedata = {}
with open('manifestinterfacedata.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        if row['ID'] in pets or row['ID'] in spells or row['ID'] in toys or row['ID'] in items:
            filedata[row['ID']] = row['FileName'].lower()

print('Found %d valid filedatas' % len(filedata))


count = 0
for filedata_id in filedata:
    count += 1
    if count % 100 == 0:
        print(count, '/', len(filedata))

    filename = filedata.get(filedata_id)
    if not filename:
        print('Missing filedata: %s' % (filedata_id))
        continue

    filepath = os.path.join('blp', filename)
    if not os.path.exists(filepath):
        print('Filedata %s missing file: %s' % (filedata_id, filename))
        continue

    im = Image.open(filepath)
    if im.size != (64, 64):
        im.resize((64, 64), Image.ANTIALIAS)

    # source icons have a dumb border
    im = im.crop((4, 4, 60, 60))

    for size in SIZES:
        resized = im.copy()
        resized.thumbnail((size, size), Image.ANTIALIAS)

        if filedata_id in items:
            maybe_save(items[filedata_id], resized, str(size), 'item')

        if filedata_id in pets:
            maybe_save(pets[filedata_id], resized, str(size), 'npc')

        if filedata_id in spells:
            maybe_save(spells[filedata_id], resized, str(size), 'spell')
