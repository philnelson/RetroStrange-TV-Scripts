ffmpeg -i "$1" -qmin 1 -qmax 1 -q:v 1 "$2/%06d.png"
