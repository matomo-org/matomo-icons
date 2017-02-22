#!/bin/bash
# Copyright (C) 2017 Lukas Winkler
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of  MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.
shopt -s globstar

for i in src/**/*.{png,gif,jpg,ico}; do
    size=48
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
    if echo "$i" | grep "SEO" # if SEO image -> 72px(https://github.com/piwik/piwik/pull/11234)
    then
        size=72
    fi
    # if file (or symlink) -> didn't get deleted
    if [ -e "$i" ]
    then
        width=$(identify -ping -format "%w" "$i")
        height=$(identify -ping -format "%h" "$i")
        if [[ $height -gt $size ]] && [[ $width -gt $size ]]
        then
            convert \
                "$i" \
                -fill transparent \
                -fuzz 1% \
                -floodfill +0+0 white \
                -floodfill +"$((width-1))"+0 white \
                -floodfill +0+"$((height-1))" white \
                -floodfill +"$((width-1))"+"$((height-1))" white \
                -strip \
                -background none \
                -trim \
                -thumbnail ${size}x${size}\> \
                -unsharp 0x1 \
                -gravity center \
                -extent ${size}x${size} \
                "$distFile"
                # input file
                # strip metadata
                # floodfill from every corner
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

convert --version > versions.txt
echo "pngquant version:" >> versions.txt
pngquant --version >> versions.txt
