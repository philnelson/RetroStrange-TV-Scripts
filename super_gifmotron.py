import random
import re
from os.path import exists, join
from os import walk
import urllib.parse
import time

import mastodon
from mastodon import Mastodon
from atproto import Client

import rstv_config

# Set to True to actually log into and post to Mastodon. False skips API calls.
mastodon_test_mode = False
verbose_mode = False

'''
# Only need to do this once!
Mastodon.create_app(
    'RSTV Tooter',
    api_base_url = 'https://wrestling.social',
    to_file = 'rstv_config.mastodon_client_secret'
)
'''

good_files = []
weird_files = []
weird_file_detail = {}
GIF_mastodon_post_text = rstv_config.GIF_mastodon_post_text

print("## START SUPER GIFMOTRON RUN")
print("🦇 SOARING MAJESTICALLY OVER DIRECTORY {} 🦇".format(rstv_config.gifs_path))
# Check for all *.mp4" filenames
# r=root, d=directories, f = files
for r, d, f in walk(rstv_config.gifs_path):
    for file in f:
        if not file.startswith('.'):
            if ".gif" in file and not file.endswith('html'):
                good_files.append(join(r, file))

if verbose_mode:
    for filename in good_files:
        print("Found {}".format(filename))
    
print("Found {} total files".format(len(good_files)))

print("Choosing one at random...")

random_number = random.randint(0, len(good_files))
second_match = re.search(r'/([^/]+?)(?:\.\w+)+$', good_files[random_number])

print("Chose {}".format(good_files[random_number]))
    
if second_match:
    name_of_item = second_match.group(1)
else:
    print("Regex sucks")
    Raise()
    
mastodon_update = GIF_mastodon_post_text.format(name_of_item)

print('Sending Mastodon post...'.format(name_of_item, good_files[random_number]))

if not mastodon_test_mode:
    # Instance Masto
    mastodon =  Mastodon(access_token=rstv_config.mastodon_access_token, api_base_url=rstv_config.mastodon_api_base_url)

    # Upload the GIF and obtain the media ID
    media = mastodon.media_post(good_files[random_number], mime_type='image/gif')

    time.sleep(15)

    mastodon.status_post(mastodon_update, media_ids=[media])

print("## END RUN")