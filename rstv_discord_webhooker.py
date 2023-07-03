from discord_webhook import DiscordWebhook
import urllib.request
import rstv_config

nowplaying_discord_message_text = rstv_config.nowplaying_discord_message_text
nowplaying_file_url = rstv_config.nowplaying_file_url
nowplaying_status_path = rstv_config.nowplaying_status_path

print('Checking what is playing...')
try:
    req = urllib.request.urlopen(nowplaying_file_url)
    nowplaying_text = req.readline().rstrip().decode("utf-8")
    nowplaying_duration_and_progress = req.readline().rstrip().decode("utf-8")
except:
    nowplaying = False

try:
    with open('{}rstv1-wasplaying.txt'.format(nowplaying_status_path)) as f:
        wasplaying_text = f.readline().rstrip()
        wasplaying = wasplaying_text
except:
    wasplaying = False
    print('Error')
    
with open('{}rstv1-wasplaying.txt'.format(nowplaying_status_path), 'w') as f:
    f.write(nowplaying_text)
    
if(wasplaying != nowplaying_text):

    if(len(nowplaying_text) >= 229):
        nowplaying_formatted = "{}... ".format(nowplaying_text[0:229])
    else:
        nowplaying_formatted = nowplaying_text
        
    print(nowplaying_formatted)
    
    nowplaying_duration = nowplaying_duration_and_progress.split('/')[1]

    print('Sending webhook with currently playing thing which is {}...'.format(nowplaying_formatted))
    update = nowplaying_discord_message_text.format(nowplaying_formatted, nowplaying_duration)

    webhook = DiscordWebhook(url=rstv_config.discord_nowplaying_webhook_url, content=update)
    response = webhook.execute()

    print("Sent: {}".format(update))
else:
    print('Same thing as last time is playing, exiting...')
