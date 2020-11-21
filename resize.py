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
    64,
]


for size in SIZES:
    if not os.path.isdir(str(size)):
        os.mkdir(str(size))

for filename in sorted(os.listdir('raw')):
    filepath = os.path.join('raw', filename)

    im = Image.open(filepath)

    if filename.startswith('race_'):
        # left, upper, right, lower
        im = im.crop((3, 3, 117, 117))

    print('Processing', filepath, im.size)

    for size in SIZES:
        resized = im.copy()
        resized.thumbnail((size, size), Image.ANTIALIAS)
        resized.save(os.path.join(str(size), filename))

