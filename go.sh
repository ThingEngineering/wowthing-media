#!/bin/sh

echo "Deleting existing icons..."
rm -rf [1-5]*
echo "Resizing..."
python3 resize.py
echo "Generating WebP icons..."
find [1-5]* -name '*.png' \! -type l -print0 | parallel -q0 cwebp -q 85 -quiet "{}" -o "{.}.webp"
echo "Fixing links..."
python3 links.py
echo "Creating tar..."
tar cf icons.tar [1-5]*
