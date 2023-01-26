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
    56,
]
SUBDIRS = [
    'achievement',
    'class',
    'currency',
    'enchantment',
    'garrison-talent',
    'item',
    'mount',
    'npc',
    'spec',
    'spell',
]


ITEM_OVERRIDE = {
    178708: 838551, # Unbound Changeling -> inv_pet_spectralporcupinered
}
CLASS_OVERRIDE = {
    12: 1260827, # Demon Hunter -> classicon_demonhunter
}


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
        img.save(outpath)

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

    im = im.crop((3, 3, im.width - 3, im.height - 3))

    print('Processing', filepath, im.size)

    for size in SIZES:
        sizePath = os.path.join(str(size), filename)
        if not os.path.exists(sizePath):
            resized = im.copy()
            resized.thumbnail((size, size), Image.ANTIALIAS)
            resized.save(sizePath)


print('----')
os.exit(0)


existing = {}
for size in SIZES:
    s = str(size)
    existing[size] = set(os.listdir(s))

    for subdir in SUBDIRS:
        p = os.path.join(s, subdir)
        existing[size] = existing[size] | set(os.path.join(subdir, sigh) for sigh in os.listdir(p))


filedata_ids = set()

# Load achievement
achievements = {}
with open('achievement.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        achievements.setdefault(int(row['IconFileID']), []).append(int(row['ID']))

print('Loaded achievement')

# Load battlepetspecies
pets = {}
with open('battlepetspecies.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        pets.setdefault(int(row['IconFileDataID']), []).append(int(row['CreatureID']))

print('Loaded battlepetspecies')

# Load chrclasses
classes = {}
with open('chrclasses.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        id = int(row['ID'])
        classes.setdefault(CLASS_OVERRIDE.get(id, int(row['IconFileDataID'])), []).append(id)
print(classes)

# Load chrspecialization
specs = {}
with open('chrspecialization.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        specs.setdefault(int(row['SpellIconFileID']), []).append(int(row['ID']))

# load spellmisc
spells = {}
with open('spellmisc.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        spell_id = int(row['SpellID'])
        if spell_id == 0:
            continue
        
        filedata_id = int(row['SpellIconFileDataID'])
        if filedata_id == 0:
            continue

        spells.setdefault(filedata_id, []).append(spell_id)

print('Loaded spellmisc')

# load currencytypes
currencies = {}
with open('currencytypes.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        currencies.setdefault(int(row['InventoryIconFileID']), []).append(int(row['ID']))

print('Loaded currencytypes')

# load garrtalent
garrtalents = {}
with open('garrtalent.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        garrtalents.setdefault(int(row['IconFileDataID']), []).append(int(row['ID']))

# load item
items = {}
item_to_filedata = {}
with open('item.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        id = int(row['ID'])
        filedata_id = ITEM_OVERRIDE.get(id, int(row['IconFileDataID']))

        items.setdefault(filedata_id, []).append(id)
        item_to_filedata[id] = filedata_id

print('Loaded item')

# load itemappearance
appearance_to_filedata = {}
with open('itemappearance.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        id = int(row['ID'])
        # Warglaives of Azzinoth are very weird
        if id in (8460, 8461, 34777):
            print('hackerman')
            appearance_to_filedata[id] = 135561
        else:
            appearance_to_filedata[id] = int(row['DefaultIconFileDataID'])

print('Loaded itemappearance')

# load itemmodifiedappearance
item_modified_appearances = {}

with open('itemmodifiedappearance.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        item_id = int(row['ItemID'])
        order = int(row['OrderIndex'])
        modifier_id = int(row['ItemAppearanceModifierID'])
        appearance_id = int(row['ItemAppearanceID'])

        # hack Warglaives of Azzinoth to point to the newer appearance ID
        if item_id in (32837, 32838):
            print('hackerman2')
            appearance_id = 34777

        item_modified_appearances.setdefault(item_id, []).append([
            order,
            modifier_id,
            appearance_id,
        ])

for item_id, imas in item_modified_appearances.items():
    first = True
    for order, modifier_id, appearance_id in sorted(imas):
        #print(order, modifier_id, appearance_id)
        if appearance_id in appearance_to_filedata:
            ima_filedata = appearance_to_filedata[appearance_id]

            if first:
                items.setdefault(ima_filedata, []).append(item_id)
                item_to_filedata[item_id] = ima_filedata
                first = False
            
            if modifier_id > 0:
                #print('eyyy', order, modifier_id, appearance_id)
                items.setdefault(ima_filedata, []).append(f'{item_id}_{modifier_id}')

print('Loaded itemmodifiedappearance')

# load spellitemenchantment
enchantments = {}
with open('spellitemenchantment.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        enchantments.setdefault(int(row['IconFileDataID']), []).append(int(row['ID']))

print('Loaded spellitemenchantment')

# load toy
toys = {}
with open('toy.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        item_id = int(row['ItemID'])
        if item_id in item_to_filedata:
            toys.setdefault(item_to_filedata[item_id], []).append(item_id)

print('Loaded toy')

# load filedata
filedata = {}
with open('manifestinterfacedata.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        id = int(row['ID'])
        if id in achievements or \
            id in currencies or \
            id in enchantments or \
            id in garrtalents or \
            id in pets or \
            id in specs or \
            id in spells or \
            id in toys or \
            id in items:
            filedata[id] = row['FileName'].lower()

print('Found %d valid filedatas' % len(filedata))

# load listfile
with open('listfile.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=';')
    for id, filepath in reader:
        id = int(id)
        if id in achievements or id in currencies or id in pets or id in spells or id in toys or id in items:
            if id not in filedata and filepath.startswith('interface/icons/') and filepath.endswith('.blp'):
                filedata[id] = filepath.replace('interface/icons/', '')
                print(f'listfile: {id} => {filedata[id]}')


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

    im = None
    try:
        im = Image.open(filepath)
        if im.size != (64, 64):
            im.resize((64, 64), Image.ANTIALIAS)

        # source icons have a dumb border
        im = im.crop((4, 4, 60, 60))
    except Exception as e:
        print('!! UH OH !!', filepath, e)
        continue

    for size in SIZES:
        resized = im.copy()
        resized.thumbnail((size, size), Image.ANTIALIAS)

        size_str = str(size)

        if filedata_id in achievements:
            maybe_save(achievements[filedata_id], resized, size_str, 'achievement')

        if filedata_id in classes:
            maybe_save(classes[filedata_id], resized, size_str, 'class')

        if filedata_id in currencies:
            maybe_save(currencies[filedata_id], resized, size_str, 'currency')

        if filedata_id in enchantments:
            maybe_save(enchantments[filedata_id], resized, size_str, 'enchantment')

        if filedata_id in garrtalents:
            maybe_save(garrtalents[filedata_id], resized, size_str, 'garrison-talent')

        if filedata_id in items:
            maybe_save(items[filedata_id], resized, size_str, 'item')

        if filedata_id in pets:
            maybe_save(pets[filedata_id], resized, size_str, 'npc')

        if filedata_id in specs:
            maybe_save(specs[filedata_id], resized, size_str, 'spec')

        if filedata_id in spells:
            maybe_save(spells[filedata_id], resized, size_str, 'spell')
