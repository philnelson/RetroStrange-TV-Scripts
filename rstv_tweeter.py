import twitter
import rstv_config
api = twitter.Api(consumer_key = rstv_config.consumer_key,
consumer_secret = rstv_config.consumer_secret,
access_token_key = rstv_config.access_token_key,
access_token_secret = rstv_config.access_token_secret)

print(rstv_config.consumer_key)

print('API Connection Test...')
print(api.VerifyCredentials())

print('Checking what is playing...')
with open('/home/leroy/RetroStrangeTV/nowplaying.txt') as f:
    nowplaying_text = f.readline().rstrip()
    nowplaying = nowplaying_text
try:
    with open('/home/leroy/RetroStrangeTV/wasplaying.txt') as f:
        wasplaying_text = f.readline().rstrip()
        wasplaying = wasplaying_text
except:
    wasplaying = ''
    print('Error')

with open('/home/leroy/RetroStrangeTV/wasplaying.txt', 'w') as f:
    f.write(nowplaying)

if(wasplaying != nowplaying):

    if(len(nowplaying) >= 240):
        nowplaying_formatted = nowplaying[0:240]
    else:
        nowplaying_formatted = nowplaying

    print('Sending tweet with currently playing thing which is {}...'.format(nowplaying_formatted))
    update = "{} is now playing on RetroStrange.TV #RSTV".format(nowplaying_formatted)
    status = api.PostUpdate(update)
    print("Sent: {}".format(update))
else:
    print('Same thing as last time is playing, exiting...')