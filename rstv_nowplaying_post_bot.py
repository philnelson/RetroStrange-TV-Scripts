from datetime import datetime
import urllib.request
import re
from typing import List, Dict

import mastodon
from mastodon import Mastodon
from atproto import Client

import rstv_config

'''
# Only need to do this once!
Mastodon.create_app(
    'RSTV Tooter',
    api_base_url = 'https://wrestling.social',
    to_file = 'rstv_config.mastodon_client_secret'
)
'''

nowplaying_mastodon_post_text = rstv_config.nowplaying_mastodon_post_text
nowplaying_file_url = rstv_config.nowplaying_file_url
nowplaying_status_path = rstv_config.nowplaying_status_path
nowplaying_bsky_post_text = rstv_config.nowplaying_bsky_post_text

now = datetime.now()
formatted_datetime = now.strftime("%Y-%m-%d %H:%M:%S")

# From atproto docs https://docs.bsky.app/docs/advanced-guides/post-richtext

def parse_mentions(text: str) -> List[Dict]:
    spans = []
    # regex based on: https://atproto.com/specs/handle#handle-identifier-syntax
    mention_regex = rb"[$|\W](@([a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)"
    text_bytes = text.encode("UTF-8")
    for m in re.finditer(mention_regex, text_bytes):
        spans.append({
            "start": m.start(1),
            "end": m.end(1),
            "handle": m.group(1)[1:].decode("UTF-8")
        })
    return spans

def parse_urls(text: str) -> List[Dict]:
    spans = []
    # partial/naive URL regex based on: https://stackoverflow.com/a/3809435
    # tweaked to disallow some training punctuation
    url_regex = rb"[$|\W](https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*[-a-zA-Z0-9@%_\+~#//=])?)"
    text_bytes = text.encode("UTF-8")
    for m in re.finditer(url_regex, text_bytes):
        spans.append({
            "start": m.start(1),
            "end": m.end(1),
            "url": m.group(1).decode("UTF-8"),
        })
    return spans
    
# Parse facets from text and resolve the handles to DIDs
def parse_facets(text: str) -> List[Dict]:
    facets = []
    for m in parse_mentions(text):
        resp = requests.get(
            "https://bsky.social/xrpc/com.atproto.identity.resolveHandle",
            params={"handle": m["handle"]},
        )
        # If the handle can't be resolved, just skip it!
        # It will be rendered as text in the post instead of a link
        if resp.status_code == 400:
            continue
        did = resp.json()["did"]
        facets.append({
            "index": {
                "byteStart": m["start"],
                "byteEnd": m["end"],
            },
            "features": [{"$type": "app.bsky.richtext.facet#mention", "did": did}],
        })
    for u in parse_urls(text):
        facets.append({
            "index": {
                "byteStart": u["start"],
                "byteEnd": u["end"],
            },
            "features": [
                {
                    "$type": "app.bsky.richtext.facet#link",
                    # NOTE: URI ("I") not URL ("L")
                    "uri": u["url"],
                }
            ],
        })
    return facets

# Let's go
print("RSTV Nowplaying Poster RUN {}".format(formatted_datetime))

try:
    print('Fetching nowplaying files...')
    with open('{}rstv1-nowplaying.txt'.format(nowplaying_status_path)) as f:
        nowplaying_text = f.readline().rstrip()
        nowplaying_duration_and_progress = f.readline().rstrip()
        f.close()
    
    print('TV1 Now Playing: {}...'.format(nowplaying_text))
    
except Exception as err:
    nowplaying = False
    raise Exception('Error fetching nowplaying files', err)

try:
    print('Fetching wasplaying files...')
    with open('{}rstv1-wasplaying.txt'.format(nowplaying_status_path)) as f:
        wasplaying_text = f.readline().rstrip()
        print('TV1 was Playing: {}...'.format(wasplaying_text))
        f.close()
        
except Exception as err:
    wasplaying_text = False
    print('Error fetching wasplaying files')
    
# Instance Masto & Bsky
mastodon =  Mastodon(access_token=rstv_config.mastodon_access_token, api_base_url=rstv_config.mastodon_api_base_url)

bsky_client = Client()
bsky_client.login(rstv_config.bsky_username, rstv_config.bsky_password)

if(wasplaying_text != nowplaying_text):
    try:
        if(len(nowplaying_text) >= 229):
            nowplaying_formatted = "{}... ".format(nowplaying_text[0:229])
        else:
            nowplaying_formatted = nowplaying_text
        
        nowplaying_duration = nowplaying_duration_and_progress.split('/')[1]
    
        print('Sending RSTV1 Mastodon post.')
        update = nowplaying_mastodon_post_text.format(nowplaying_formatted, nowplaying_duration)
        mastodon.toot(update)
        print("Sent: {}".format(update))
        
        bsky_facets = parse_facets(nowplaying_bsky_post_text.format(nowplaying_formatted, nowplaying_duration))
        bsky_client.send_post(text=nowplaying_bsky_post_text.format(nowplaying_formatted, nowplaying_duration), facets=bsky_facets)
        print("RSTV1 Bsky posted.")
        
        with open('{}rstv1-wasplaying.txt'.format(nowplaying_status_path), 'w') as f:
            f.write(nowplaying_text)
            f.close()
    except Exception as err:
        print(err)
    
else:
    print('Not posting RSTV1 update. Same item still playing.')

