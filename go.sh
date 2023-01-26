#!/bin/sh

rm -rf [1-5]*
python3 resize.py
find [1-5]* -name '*.png' \! -type l -print0 | parallel -q0 cwebp -q 85 -quiet "{}" -o "{.}.webp"
python3 links.py
tar cf icons.tar [1-5]*
