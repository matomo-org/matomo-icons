#!/bin/bash
shopt -s globstar

size=16

for i in src/**/*.{png,gif,jpg}; do
    echo "$i"
    absDirname=$(dirname "$i")
    origFilename=$(basename "$i")
    browserCode=${origFilename%.*}
    dirname="dist/${absDirname#src/}"
    distFile="${dirname}/${browserCode}.png"
    echo "$distFile"
    if [ ! -d "$dirname" ]
    then
        mkdir -p "$dirname"
    fi
    convert \
        "$i" \
        -transparent white \
         -background none \
        -trim \
        -resize ${size}x${size} \
        -gravity center \
        -extent ${size}x${size} \
        "$distFile"
        # input file
        # make background transparent
        # keep transparency
        # cut border
        # resize while keeping the aspect ratio
        # center image
        # fit to 16x16
    # optimize png:
    optipng -o 9 -q "$distFile"
done
