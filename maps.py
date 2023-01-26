import os
import os.path

from PIL import Image


SIZES = [
    [1500, 1000],
    [1200, 800],
    [900, 600],
]


def recurse(path):
    print(f'Visiting {path}')

    out_path = os.path.join('maps', path.replace('raw_maps/', ''))
    if not os.path.isdir(out_path):
        os.mkdir(out_path)

    with os.scandir(path) as scanner:
        for entry in scanner:
            if entry.is_dir():
                recurse(entry.path)
            
            elif entry.name.endswith('.png'):
                im = Image.open(entry.path)
                
                for width, height in SIZES:
                    out_path = entry.path.replace('raw_maps/', 'maps/').replace('.png', '_%d_%d.png' % (width, height))
                    if not os.path.exists(out_path):
                        print('>', out_path)
                        resized = im.resize((width, height), Image.LANCZOS)
                        resized.save(out_path)



recurse('raw_maps/')

# for filename in sorted(os.listdir('raw_maps')):
#     filepath = os.path.join('raw_maps', filename)


#     if not filename.endswith('.png'):
#         print(filename)
#         continue

#     print(filepath)
#     continue
#     im = Image.open(filepath)
    
#     print('Processing', filepath, im.size)

#     for width, height in SIZES:
#         outpath = os.path.join('maps', filename.replace('.png', '_%d_%d.png' % (width, height)))
#         if not os.path.exists(outpath):
#             print('boop', outpath)
#             resized = im.resize((width, height), Image.LANCZOS)
#             resized.save(outpath)
