#!/bin/sh
# improved version of http://varya.me/en/posts/image-diffs-with-git/
# enable with `git config diff.image.command 'tools/git-imgdiff.sh'`
echo $1
compare $2 $1 tmp/diff.png
compare $2 $1 -fuzz 5% tmp/fuzzy.png
compare $2 $1 -fuzz 10% tmp/fuzzier.png

composite $2 $1 -compose difference tmp/comp.png
convert tmp/comp.png -auto-level tmp/comp-auto.png

montage -geometry +4+4 -tile 7x1 $1 tmp/diff.png tmp/fuzzy.png tmp/fuzzier.png tmp/comp.png tmp/comp-auto.png $2 tmp/final.png
mogrify -magnify tmp/final.png
cp tmp/final.png tmp/diffs/$(basename $1)
# display tmp/final.png
