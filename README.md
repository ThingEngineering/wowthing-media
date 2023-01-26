# WoWthing Media

WoW icons and other images


## Process

1. Download the latest listfile from [wow.tools](https://wow.tools/files/) - Listfile dropdown, "Community CSV (all filenames, incl. guessed ones)".

1. Run `cascview` and extract all of `interface/icons/`.

1. Copy `interface/icons/*.blp` into the `blp/` directory.

1. Download/link updated CSVs into this directory.

1. Remove old files: `rm -rf [1-5]*`.

1. Generate resized icons: `python3 resize.py`.

1. Generate webp files: `find [1-5]* -name '*.png' \! -type l -print0 | parallel -q0 cwebp -q 85 -quiet "{}" -o "{.}.webp"`

1. Generate webp links: `python3 links.py`.

1. Create tar file: `tar cvf icons.tar [1-5]*`.

1. Upload tar file: `scp icons.tar host:`.

1. Extract tar file on host.

1. Flush Cloudflare cache.
