#!/bin/bash
shopt -s globstar
size=48

for i in src/**/*.{png,gif,jpg,ico}; do
    absDirname=$(dirname "$i")
    origFilename=$(basename "$i")
    code=${origFilename%.*}
    dirname="dist/${absDirname#src/}"
    distFile="${dirname}/${code}.png"
    if [ ! -d "$dirname" ]
    then
        mkdir -p "$dirname"
    fi
    if [[ $i == *.ico ]]
    then
        if file "$i" | grep -E "HTML|empty|ASCII text|: data|SVG" # if no valid image
        then
            rm "$i"
        else
            if [ ! -d "tmp" ]
            then
                mkdir "tmp"
            fi
            largestIcon=$(python analyseIco.py "$i")
            newIcon="tmp/${code}.ico"
            convert ${i}\[$largestIcon\] $newIcon
            i=$newIcon
        fi
    fi
    # if file (or symlink) -> didn't get deleted
    if [ -e "$i" ]
    then
        width=$(identify -ping -format "%w" "$i")
        height=$(identify -ping -format "%h" "$i")
        echo "(${width}x${height})"
        if [[ $height -gt $size ]] && [[ $width -gt $size ]]
        then
            convert \
                "$i" \
                -strip \
                -transparent white \
                -background none \
                -trim \
                -thumbnail ${size}x${size}\> \
                -unsharp 0x1 \
                -gravity center \
                -extent ${size}x${size} \
                "$distFile"
                # input file
                # strip metadata
                # make background transparent
                # keep transparency
                # cut border
                # get only one image from .ico
                # resize while keeping the aspect ratio
                # sharpen the image
                # center image
                # fit to 16x16
        else
            convert \
                "$i" \
                -strip \
                -transparent white \
                -background none \
                "$distFile"
            echo -e "\033[31mWarning: This image is smaller than the default size (${width}x${height})"
            echo -e "$i"
            echo  -e "\033[0m"
        fi
        # optimize png:
        pngquant -f --ext .png -s 1 --skip-if-larger --quality 70-95 "$distFile"
    fi
done
