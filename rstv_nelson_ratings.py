import datetime
import json
import urllib.request
import base64
import rstv_config


print('Downloading nowplaying file...')
try:
    req = urllib.request.urlopen(rstv_config.nowplaying_file_url)
    nowplaying_text = req.readline().rstrip().decode("utf-8")
    nowplaying_duration_and_progress = req.readline().rstrip().decode("utf-8")
    nowplaying_duration = nowplaying_duration_and_progress.split('/')[1]
    nowplaying_progress = nowplaying_duration_and_progress.split('/')[0]
    
    print('Now Playing: {}...'.format(nowplaying_text))
except:
    nowplaying = False
    raise()
    
print('Getting broadcast info...')

try:
    current_date = datetime.date.today()
    
    p = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    p.add_password(None, '{}{}'.format(rstv_config.owncast_stream_root_url,rstv_config.owncast_info_api_url), 'admin', rstv_config.owncast_stream_key);
    auth_handler = urllib.request.HTTPBasicAuthHandler(p)
    opener = urllib.request.build_opener(auth_handler)
    
    req = urllib.request.Request('{}{}'.format(rstv_config.owncast_stream_root_url,rstv_config.owncast_info_api_url), headers={'Content-Type': 'application/json', 'Authorization': "Bearer {}".format(rstv_config.owncast_access_token)})
    result = opener.open(req)
    server_status = result.read()
    server_status = json.loads(server_status.decode("UTF-8"))
    
    file_data = {
        'time': str(datetime.datetime.now()),
        'nowplaying': nowplaying_text,
        'total_duration': nowplaying_duration,
        'time_left': nowplaying_progress,
        'viewers': server_status['viewerCount']
    }
    
    print('Current data: {}'.format(file_data))
    
    with open("{}rstv-ratings-{}.txt".format(rstv_config.nowplaying_status_path,current_date), "a") as myfile:
        myfile.write(json.dumps(file_data)+ "\n")
except Exception as error:
    print(error)
    file_data = False
    
