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
with open('{}nowplaying.txt'.format(rstv_config.status_output_path)) as f:
    nowplaying_text = f.readline().rstrip()
    nowplaying_duration = f.readline().rstrip()
    nowplaying = nowplaying_text
try:
    with open('{}wasplaying.txt'.format(rstv_config.status_output_path)) as f:
        wasplaying_text = f.readline().rstrip()
        wasplaying = wasplaying_text
except:
    wasplaying = ''
    print('Error')

with open('{}wasplaying.txt'.format(rstv_config.status_output_path), 'w') as f:
    f.write(nowplaying)

if(wasplaying != nowplaying):

    if(len(nowplaying) >= 229):
        nowplaying_formatted = "{}... ".format(nowplaying[0:229])
    else:
        nowplaying_formatted = nowplaying

    print('Sending tweet with currently playing thing which is {}...'.format(nowplaying_formatted))
    update = rstv_config.nowplaying_tweet_string.format(nowplaying_formatted, nowplaying_duration)
    status = api.PostUpdate(update)
    print("Sent: {}".format(update))
else:
    print('Same thing as last time is playing, exiting...')