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
set -x
set -e

function resizeLargeIcon () {
    inputfile=$1
    outputfile=$2
    convert \
        "$inputfile" \
        -bordercolor transparent -border 1x1 \
        -fill transparent \
        -fuzz 1% \
        -draw "color 0,0 floodfill" \
        -draw "color $((width+1)),0 floodfill" \
        -draw "color 0,$((height+1)) floodfill" \
        -draw "color $((width+1)),$((height+1)) floodfill" \
        -strip \
        -background none \
		-fuzz 0 \
        -trim \
        -thumbnail "${size}"x"${size}"\> \
        -unsharp 0x1 \
        -gravity center \
        -extent "${size}"x"${size}" \
        "$outputfile"
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
    optimizeIcon "$outputfile"
}
function resizeSmallIcon () {
    inputfile=$1
    outputfile=$2
    convert \
        "$inputfile" \
        -strip \
        -transparent white \
        -background none \
        "$outputfile"
    echo -e "\033[31mWarning: This image is smaller than the default size (${width}x${height})"
    echo -e "$inputfile"
    echo  -e "\033[0m"
    optimizeIcon "$outputfile"
}

function resizeSvg () {
    inputfile=$1
    outputfile=$2
    if echo "$outputfile" | grep "flags"
    then
        inkscape -h "$size" "$inputfile" -o "$outputfile"
    else
        inkscape -h 1024 "$inputfile" -o "$outputfile"
        mogrify \
            -background none \
            -bordercolor transparent -border 1x1 \
            -trim \
            -thumbnail "${size}"x"${size}"\> \
            -unsharp 0x1 \
            -gravity center \
            -extent "${size}"x"${size}" \
            "$outputfile"

    fi
    optimizeIcon "$outputfile"
}

function optimizeIcon () {
    pngquant -f --ext .png -s 1 --skip-if-larger --quality 70-95 "$1" || [ $? -gt 97 ]
}

function handleMultisizeIco () {
    file=$1
    code=$2
    if file "$file" | grep -E "HTML|empty|ASCII text|: data|SVG" # if no valid image
    then
        rm "$file"
    else
        if [ ! -d "tmp" ]
        then
            mkdir "tmp"
        fi
        largestIcon=$(python3 analyseIco.py "$1")
        newIcon="tmp/${code}.ico"
        convert "${i}"\["$largestIcon"\] "$newIcon"
        echo "$newIcon" # "return"
    fi
}

function fixFlags () {
    height="$1"
    targetDir="dist/flags"
    resizeSvg "unk.flag.svg" "dist/flags/xx.png"

    for i in ac cp dg ea eu fx ic su ta uk an bu cs nt sf tp yu zr a1 a2 ap o1 cat
    do
        icon="${targetDir}/${i}.png"
        if [ ! -f "$icon" ]
        then
            echo -e "\033[31mWarning: No flag for $i, using default\033[0m"
            cp "dist/flags/xx.png" "$icon"
        fi
    done

    rm ${targetDir}/gb-*
    rm ${targetDir}/un.png
    rm ${targetDir}/xk.png
    rm ${targetDir}/es-ct.png
    rm ${targetDir}/es-ga.png
}

function loopThrough () {
    for i in src{/**/,/flags/}*.{svg,png,gif,jpg,ico}; do
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
            i=$(handleMultisizeIco "$i" "$code")
        fi
        if echo "$i" | grep "SEO" # if SEO image -> 72px(https://github.com/piwik/piwik/pull/11234)
        then
            size=72
        fi
        if [[ $i == *.svg ]]
        then
            resizeSvg "$i" "$distFile"
            continue
        fi
        # if file (or symlink) -> didn't get deleted
        if [ -e "$i" ]
        then
            width=$(identify -ping -format "%w" "$i")
            height=$(identify -ping -format "%h" "$i")
            if [[ $height -gt $size ]] && [[ $width -gt $size ]]
            then
                resizeLargeIcon "$i" "$distFile"
            else
                resizeSmallIcon "$i" "$distFile"
            fi
        fi
    done
}

function saveVersions () {
    {
        convert --version
        echo "pngquant version:"
        pngquant --version
        inkscape --version
    } > versions.txt
}
function main () {
    loopThrough
    fixFlags 48
    saveVersions
}

main
