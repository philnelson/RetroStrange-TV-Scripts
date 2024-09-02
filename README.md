# RetroStrange-TV-Scripts
A collection of junk for RetroStrange.TV.

## rstv_broadcast_golive_notifier.py

This script is meant to be called by a cron job every 1 minute. It checks what is playing and if it's different than what was playing last time it checked it sends a Mastodon and/or Discord post about it.

## rstv_metadata_checkup_py

This thing does too many things. It checks every file in the configured directories for filename and metadata correctness: Does it have a title attribute? Does it have the release year in parentheses (e.g. "(1972)")? It also optionally generates 7 animated GIFs using ffmpeg for each item it detects. It outputs CSV files showing all of the files scanned, with an md5 sum, the  title, duration and likely other metadata by the time you read this.