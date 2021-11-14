import twitter
import rstv_config
api = twitter.Api(consumer_key = '',
consumer_secret = '',
access_token_key = '',
access_token_secret = '')

print('API Connection Test...')
print(api.VerifyCredentials())

print('Sending tweet with currently playing thing...')
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
    update = "{} is now playing on RetroStrange TV".format(nowplaying)
    print(update)
    status = api.PostUpdate(update)
