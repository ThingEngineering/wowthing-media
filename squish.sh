#!/usr/bin/env bash

#find [1-4]* -name '*.png' \! -type l -print0 | xargs -0 -n 10 -P 4 optipng -o7 -quiet
#find [1-4]* -name '*.png' \! -type l -print0 | xargs -0 -P 4 -I {} cwebp -q 85 -quiet "{}" -o "$(echo '{}' | sed 's/\.png/.webp/')"
#find [1-4]* -name '*.png' \! -type l -print0 | xargs -0 -P 4 -I {} avif -e "{}" -o "$(echo '{}' | sed 's/\.png/.avif/')"

find [1-4]*/achievement -name '*.png' \! -type l -print0 | parallel -q0 cwebp -q 85 -quiet "{}" -o "{.}.webp"
#find [1-4]* -name '*.png' \! -type l -print0 | parallel -q0 avif-linux-x64 -e "{}" -o "{.}.avif"

find [1-4]* -name '*.png' -type l -print0 | parallel -q0 ln -fs "{.}.webp"
