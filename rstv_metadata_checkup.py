import os
import random
from pathlib import Path
from os.path import exists
import subprocess
import math
import rstv_config
import csv
import hashlib
import time

generator_config = {
    "types": {
        "episodes": {
            "update": True,
            "path": rstv_config.tv_path,
            "items": {},
        },
        "shorts": {
            "update": True,
            "path": rstv_config.shorts_path,
            "items": {},
        },
        "features": {
            "update": True,
            "path": rstv_config.movies_path,
            "items": {},
        },
        "trailers": {
            "update": True,
            "path": rstv_config.trailers_path,
            "items": {},
        },
        "ads": {
            "update": True,
            "path": rstv_config.stationid_path,
            "items": {},
        },
    },
    "gifs_path": rstv_config.gifs_path,
    "create_gifs": False,
    "overwrite_gifs": False,
}

def get_fancy_duration(duration_in_seconds):
    m, s = divmod(duration_in_seconds, 60)
    h, m = divmod(m, 60)
    return f'{h:d} hours {m:02d} minutes {s:02d} seconds'


def video_length_seconds(filename):
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            "--",
            filename,
        ],
        capture_output=True,
        text=True,
    )
    try:
        return float(result.stdout)
    except ValueError:
        raise ValueError(result.stderr.rstrip("\n"))


def create_gifs_from_video(file, start, duration, seq):
    filename= os.path.basename(file)
    print(f'{generator_config["gifs_path"]}{filename}.{seq}.gif')
    result = subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-ss",
            str(start),
            "-t",
            str(duration),
            "-i",
            file,
            "-filter_complex",
            "[0:v] fps=12,scale=480:-1,split [a][b];[a] palettegen [p];[b][p] paletteuse",
            f'{generator_config["gifs_path"]}{filename}.{seq}.gif',
        ],
        capture_output=True,
        text=True,
    )
    try:
        return str(result.stdout)
    except ValueError:
        raise ValueError(result.stderr.rstrip("\n"))


skipped_types = []
updated_types = {}

for media_type in generator_config['types']:
    tic = time.perf_counter()
    print("------")
    if not generator_config['types'][media_type]['update']:
        print("Skipping {} update due to config".format(media_type))
        skipped_types.append(media_type)
    else:
        path = generator_config['types'][media_type]['path']
        good_files = []
        weird_files = []
        print(" /\                 /\\")
        print("/ \\'._   (\_/)   _.'/ \\")
        print("|.''._'--(o.o)--'_.''.|")
        print(" \_ / `;=/ \" \=;` \ _/")
        print("   `\__| \___/ |__/`")
        print("        \(_|_)/")
        print("         \" ` \"")
        print("🦇 SOARING MAJESTICALLY OVER DIRECTORY {} 🦇".format(path))
        print(" ")
        # r=root, d=directories, f = files
        for r, d, f in os.walk(path):
            for file in f:
                if ".mp4" in file and ".gif" not in file:
                    good_files.append(os.path.join(r, file))
                else:
                    if ".gif" not in file:
                        weird_files.append(os.path.join(r, file))

        # random.shuffle(files)
        total_length_in_seconds = 0

        print("")
        print("🦇 FOUND {} PROPERLY FORMATTED VIDEO FILES 🦇".format(len(good_files)))
        for f in good_files:
            filename= os.path.basename(f)
            video_length_in_seconds = video_length_seconds(f)
            total_length_in_seconds += math.floor(video_length_seconds(f))
            
            with open(f, 'rb') as file_to_check:
                # read contents of the file
                data = file_to_check.read()    
                # pipe contents of the file through
                md5_returned = hashlib.md5(data).hexdigest()
            
            generator_config['types'][media_type]['items'][md5_returned] = {"path": f, "filename": filename, "duration_in_seconds": video_length_in_seconds}
            print(filename, video_length_in_seconds, "sec")

            if generator_config['create_gifs']:
                first_gif_start = 15
                second_gif_start = math.floor(video_length_in_seconds / 4)
                third_gif_start = math.floor(video_length_in_seconds / 4) * 2
                fourth_gif_start = math.floor(video_length_in_seconds / 4) * 3
                fifth_gif_start = (math.floor(video_length_in_seconds / 4) * 4) - 30

                if not exists("{}{}.{}.gif".format(generator_config["gifs_path"],filename, 1)):
                    print("GENERATING GIF1 at {}".format(first_gif_start))
                    create_gifs_from_video(f, first_gif_start, 2.5, 1)
                else:
                    if generator_config['overwrite_gifs']:
                        print("OVERWRITING GIF1 at {}".format(first_gif_start))
                        create_gifs_from_video(
                            f, first_gif_start, 2.5, 1)
                    else:
                        print("GIF1 at {} exists, skipping".format(
                            first_gif_start))

                if not exists("{}{}.{}.gif".format(generator_config["gifs_path"],filename, 2)):
                    print("GENERATING GIF2 at {}".format(second_gif_start))
                    create_gifs_from_video(f, second_gif_start, 2.5, 2)
                else:
                    if generator_config['overwrite_gifs']:
                        print("OVERWRITING GIF2 at {}".format(second_gif_start))
                        create_gifs_from_video(
                            f, second_gif_start, 2.5, 2)
                    else:
                        print("GIF2 at {} exists, skipping".format(
                            second_gif_start))

                if not exists("{}{}.{}.gif".format(generator_config["gifs_path"],filename, 3)):
                    print("GENERATING GIF3 at {}".format(third_gif_start))
                    create_gifs_from_video(f, third_gif_start, 2.5, 3)
                else:
                    if generator_config['overwrite_gifs']:
                        print("OVERWRITING GIF3 at {}".format(third_gif_start))
                        create_gifs_from_video(
                            f, third_gif_start, 2.5, 1)
                    else:
                        print("GIF3 at {} exists, skipping".format(
                            third_gif_start))

                if not exists("{}{}.{}.gif".format(generator_config["gifs_path"],filename, 4)):
                    print("GENERATING GIF4 at {}".format(fourth_gif_start))
                    create_gifs_from_video(f, fourth_gif_start, 2.5, 4)
                else:
                    if generator_config['overwrite_gifs']:
                        print("OVERWRITING GIF4 at {}".format(fourth_gif_start))
                        create_gifs_from_video(
                            f, fourth_gif_start, 2.5, 1)
                    else:
                        print("GIF4 at {} exists, skipping".format(
                            fourth_gif_start))
                            
                if not exists("{}{}.{}.gif".format(generator_config["gifs_path"],filename, 5)):
                    print("GENERATING GIF5 at {}".format(fifth_gif_start))
                    create_gifs_from_video(f, (fifth_gif_start), 2.5, 4)
                else:
                    if generator_config['overwrite_gifs']:
                        print("OVERWRITING GIF5 at {}".format((fifth_gif_start)))
                        create_gifs_from_video(
                            f, (fifth_gif_start), 2.5, 1)
                    else:
                        print("GIF5 at {} exists, skipping".format(
                            (fifth_gif_start)))

        print(" ")
        print("🦇 FOUND {} WEIRD FILES IN THE DIRECTORY 🦇".format(len(weird_files)))
        for f in weird_files:
            print(f, video_length_in_seconds)

        print(" ")
        print("🦇 STATS FOR THE {} PROPERLY FORMATTED FILES 🦇".format(len(good_files)))
        print("Total duration {}".format(get_fancy_duration(total_length_in_seconds)))
        print("------")

        updated_types[media_type] = {
            "good_files": good_files,
            "weird_files": weird_files,
            "total_length_in_seconds": total_length_in_seconds
        }

print("Skipped {} media types: {}".format(
    len(skipped_types), '%s' % ', '.join(map(str, skipped_types))))
print("Updated {} media types: {}".format(
    len(updated_types), '%s' % ', '.join(map(str, updated_types))))

all_media_total_length_in_seconds = 0
for media_type in updated_types:
    all_media_total_length_in_seconds += updated_types[media_type]['total_length_in_seconds']
    print(" {}: {} good files, {} weird files".format(media_type, len(
        updated_types[media_type]['good_files']), len(updated_types[media_type]['weird_files'])))

    print("    Total duration: {}".format(get_fancy_duration(updated_types[media_type]['total_length_in_seconds'])))

with open('rstv media list.csv', 'w', newline='') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',',
                            quoting=csv.QUOTE_MINIMAL)
    spamwriter.writerow(['Media Type','Filename', 'Duration In Seconds','Full Path','md5'])
    for media_type in updated_types:
        for item in generator_config['types'][media_type]['items']:
            spamwriter.writerow([media_type, generator_config['types'][media_type]['items'][item]['filename'], generator_config['types'][media_type]['items'][item]['duration_in_seconds'],generator_config['types'][media_type]['items'][item]['path'], item])

toc = time.perf_counter()
print("Duration of all media: {}".format(get_fancy_duration(all_media_total_length_in_seconds)))
print(f"Took {toc - tic:0.4f} All done.")
