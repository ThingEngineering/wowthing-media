import os
import os.path
import pathlib


SIZES = [
    16,
    20,
    24,
    32,
    40,
    48,
    56,
]


def main():
    for size in SIZES:
        recurse(str(size))


def recurse(path):
    print(f'Visiting {path}')
    with os.scandir(path) as scanner:
        for entry in scanner:
            if entry.is_dir():
                recurse(entry.path)
            elif entry.name.endswith('.png') and entry.is_symlink():
                target = os.readlink(entry.path)
                print(f'{entry.name} -> {target}')
                try:
                    os.symlink(os.path.basename(target).replace('.png', '.webp'), entry.path.replace('.png', '.webp'))
                except:
                    pass


if __name__ == '__main__':
    main()
