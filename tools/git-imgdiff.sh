#!/bin/sh
# by http://varya.me/en/posts/image-diffs-with-git/
compare $2 $1 png:- | montage -geometry +4+4 $2 - $1 png:- | gwenview /dev/stdin 

