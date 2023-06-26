import rstv_config
from csv import DictReader
import random
from os.path import splitext
import math

scheduler_config = {
    "types": {
        "episodes": {
            "update": True,
            "path": rstv_config.tv_path,
            "frequency": 1,
            "items": {},
        },
        "shorts": {
            "update": True,
            "path": rstv_config.shorts_path,
            "frequency": 2,
            "items": {},
        },
        "features": {
            "update": True,
            "path": rstv_config.movies_path,
            "frequency": 1,
            "items": {},
        },
        "trailers": {
            "update": True,
            "path": rstv_config.trailers_path,
            "frequency": 1,
            "items": {},
        },
        "ads": {
            "update": True,
            "path": rstv_config.stationid_path,
            "frequency": 3,
            "items": {},
        },
    },
    "how_long": 86400,
}

def get_fancy_duration(duration_in_seconds):
    m, s = divmod(duration_in_seconds, 60)
    h, m = divmod(m, 60)
    return f'{h:d} hours {m:02d} minutes {s:02d} seconds'

# open file in read mode
with open("rstv media list.csv", 'r') as f:
     
    dict_reader = DictReader(f)
     
    list_of_dict = list(dict_reader)
   
for item in list_of_dict:
    scheduler_config["types"][item['Media Type']]['items'][item['md5']] = {"filename": item['Filename'], "path": item['Full Path'], "duration_in_seconds": item['Duration In Seconds'] }
    
print(f"Booking {scheduler_config['how_long']} seconds")

time_remaining = scheduler_config['how_long']
duration_of_playlist = 0
random_type_array = []
generated_schedule_playlist = {}

for media_type in scheduler_config['types']:
    for x in range(0,scheduler_config['types'][media_type]['frequency']):
        random_type_array.append(media_type)
    
while time_remaining > 30:
    print(f'{time_remaining} seconds left.')
    chosen_type = random.choice(random_type_array)
    
    video = random.choice(list(scheduler_config['types'][chosen_type]['items']))
    
    generated_schedule_playlist[video] = scheduler_config['types'][chosen_type]['items'][video]
    
    duration_of_playlist = duration_of_playlist + float(scheduler_config['types'][chosen_type]['items'][video]['duration_in_seconds'])
    
    #while time_remaining < float(scheduler_config['types'][chosen_type]['items'][video]['duration_in_seconds']):
    #    video = random.choice(list(scheduler_config['types'][chosen_type]['items']))
    
    print(f"{scheduler_config['types'][chosen_type]['items'][video]['filename']} : {scheduler_config['types'][chosen_type]['items'][video]['duration_in_seconds']}s")
    
    time_remaining = time_remaining - float(scheduler_config['types'][chosen_type]['items'][video]['duration_in_seconds'])

print(f'Playlist duration: {get_fancy_duration(math.floor(duration_of_playlist))}')
print(f'{time_remaining} seconds leftover.')

seq = 1
with open('24 hour playlist.pls', 'w') as f:
    f.write('[playlist]\n')
    
    for video in generated_schedule_playlist:
        f.write(f"File{seq}={generated_schedule_playlist[video]['path']}\nTitle{seq}={splitext(generated_schedule_playlist[video]['filename'])[0]} \n\n")
        seq = seq + 1