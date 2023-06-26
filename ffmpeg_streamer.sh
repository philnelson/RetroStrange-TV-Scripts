ffmpeg -thread_queue_size 64 \
  -r 60 -scale 1280x720 -i "$1" \
  -c:v libx264 -preset veryfast -b:v 1984k -maxrate 1984k -bufsize 3968k \
  -vf "format=yuv420p" -g 60 -c:a aac -b:a 128k -ar 44100 \
  -f flv [YOUR STREAM URL]