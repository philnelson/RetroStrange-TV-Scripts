import mastodon
from mastodon import Mastodon
import urllib.request
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

print('Downloading nowplaying file...')
try:
    req = urllib.request.urlopen(nowplaying_file_url)
    nowplaying_text = req.readline().rstrip().decode("utf-8")
    nowplaying_duration_and_progress = req.readline().rstrip().decode("utf-8")
    print('Now Playing: {}...'.format(nowplaying_text))
except:
    nowplaying = False

try:
    with open('{}rstv1-wasplaying.txt'.format(nowplaying_status_path)) as f:
        wasplaying_text = f.readline().rstrip()
        print('Was Playing: {}...'.format(wasplaying_text))
except:
    wasplaying_text = False
    print('Error')
    
if(wasplaying_text != nowplaying_text):

    if(len(nowplaying_text) >= 229):
        nowplaying_formatted = "{}... ".format(nowplaying_text[0:229])
    else:
        nowplaying_formatted = nowplaying_text
        
    print(nowplaying_formatted)
    
    nowplaying_duration = nowplaying_duration_and_progress.split('/')[1]

    print('Sending Mastodon post with {}...'.format(nowplaying_formatted))
    update = nowplaying_mastodon_post_text.format(nowplaying_formatted, nowplaying_duration)
    
    mastodon =  Mastodon(access_token=rstv_config.mastodon_access_token, api_base_url=rstv_config.mastodon_api_base_url)
    mastodon.toot(update)

    print("Sent: {}".format(update))
    
    with open('{}rstv1-wasplaying.txt'.format(nowplaying_status_path), 'w') as f:
        f.write(nowplaying_text)
else:
    print('Same thing as last time is playing, exiting...')