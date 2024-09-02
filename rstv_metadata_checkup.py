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
import json
import re

skipped_types = []
updated_types = {}

generator_config = {
    "types": {
        "episodes": {
            "update": True,
            "path": rstv_config.tv_path,
            "items": {},
            "weird_file_detail": {},
        },
        "shorts": {
            "update": True,
            "path": rstv_config.shorts_path,
            "items": {},
            "weird_file_detail": {},
        },
        "features": {
            "update": True,
            "path": rstv_config.movies_path,
            "items": {},
            "weird_file_detail": {},
        },
        "trailers": {
            "update": True,
            "path": rstv_config.trailers_path,
            "items": {},
            "weird_file_detail": {},
        },
        "ephemera": {
            "update": True,
            "path": rstv_config.ephemera_path,
            "items": {},
            "weird_file_detail": {},
        },
        "ads": {
            "update": True,
            "path": rstv_config.stationid_path,
            "items": {},
            "weird_file_detail": {},
        },
        "staging": {
            "update": False,
            "path": rstv_config.staging_path,
            "items": {},
            "weird_file_detail": {},
        },
    },
    "gifs_path": rstv_config.gifs_path,
    "create_gifs": True,
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
        return round(float(result.stdout), 2)
    except ValueError:
        raise ValueError(result.stderr.rstrip("\n"))
    
def get_video_title(file_path):
    # Run ffprobe command to get JSON metadata
    cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_entries', 'format_tags=title', file_path]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        # Parse JSON output and extract title
        metadata = json.loads(result.stdout)

        if 'format' in metadata and 'tags' in metadata['format'] and 'title' in metadata['format']['tags']:
            title = metadata['format']['tags']['title'] 
        else:
            title = None
        return title
    else:
        raise ValueError(result.stderr.rstrip("\n"))


def create_gifs_from_video(file, start, duration, seq):
    filename = os.path.basename(file)
    path = filename[:-4]
    #print(f'{generator_config["gifs_path"]}{path}/{filename}.{seq}.gif')
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
            f'{generator_config["gifs_path"]}{path}/{filename}.{seq}.gif',
        ],
        capture_output=True,
        text=True,
    )
    
    output = result.stdout
    
    result = subprocess.run(
        [
            "gifsicle",
            "-O3",
            "--lossy=30",
            "-o",
            f'{generator_config["gifs_path"]}{path}/{filename}.{seq}.gif',
            f'{generator_config["gifs_path"]}{path}/{filename}.{seq}.gif',
        ],
        capture_output=True,
        text=True,
    )
    
    try:
        return str(output)
    except ValueError:
        raise ValueError(result.stderr.rstrip("\n"))
    
tic = time.perf_counter()

print("""##########################################################################################
################################################     ###     #      #     #####    #######
################################################  ##  ##  ######  ###  ##  ##   ##   #####
####                                       #####      ##     ###  ###      #   #####  ####
####                                       #####  #  ###  ######  ###     ###  ####   ####
################################################  ##  ##     ###  ###  ##  ###      ######
##########################################################################################
####                                                                                  ####
####                                                                                  ####
##########################################################################################
#####     #      #      ####   ####   ####  ###      ###     #############################
####   ######  ###  ##  ####    ###     ##  ##  #### ###  ######                      ####
######    ###  ###     ####  ##  ##   #  #  ##  ##     #     ###                      ####
########  ###  ###  #   ##        #   ##    ##   ###  ##  ################################
#####    ####  ###  ##      ####  #   ####  ####    ####     #############################
##########################################################################################""")
total_files_in_catalog = 0
for media_type in generator_config['types']:
    
    print("------")
    if not generator_config['types'][media_type]['update']:
        print("Skipping {} update due to config".format(media_type))
        skipped_types.append(media_type)
    else:
        path = generator_config['types'][media_type]['path']
        good_files = []
        weird_files = []
        weird_file_detail = {}
        
        print("🦇 SOARING MAJESTICALLY OVER DIRECTORY {} 🦇".format(path))
        print(" ")
        # Check for all *.mp4" filenames
        # r=root, d=directories, f = files
        for r, d, f in os.walk(path):
            for file in f:
                if not file.startswith('.'):
                    if ".mp4" in file or ".m4v" in file:
                        if ".gif" not in file:
                            #print(file)
                            # Check for year in filename
                            if bool(re.search(r'\(\d{4}\)', file)):
                                good_files.append(os.path.join(r, file))
                            else:
                                weird_files.append(os.path.join(r, file))
                    else:
                        if ".gif" not in file:
                            weird_files.append(os.path.join(r, file))

        # random.shuffle(files)
        total_length_in_seconds = 0

        print("")
        print("🦇 FOUND {} PROPERLY FORMATTED VIDEO FILES 🦇".format(len(good_files)))
        total_files_to_scan = len(good_files)
        files_scanned_so_far = 0
        for f in good_files:
            filename= os.path.basename(f)
            video_length_in_seconds = video_length_seconds(f)
            video_title = get_video_title(f)
            total_length_in_seconds += math.floor(video_length_seconds(f))
            
            with open(f, 'rb') as file_to_check:
                # read contents of the file
                data = file_to_check.read()    
                # pipe contents of the file through
                md5_returned = hashlib.md5(data).hexdigest()
                
            file_size = os.path.getsize(f)
            file_size_mb = math.ceil((file_size / 1024)/1024)
            
            generator_config['types'][media_type]['items'][md5_returned] = {"video_title": video_title, "path": f, "filename": filename, "size": file_size, "duration_in_seconds": video_length_in_seconds}
            
            print("{} [{}/{}] {}".format(media_type, files_scanned_so_far+1, total_files_to_scan, md5_returned)) 
            print("\tFile: {} \n\tDuration: {}s, Size: {}mb".format(filename, video_length_in_seconds, file_size_mb))

            number_of_gifs = 7
            if generator_config['create_gifs']:
                first_gif_start = math.floor(video_length_in_seconds / 7)
                second_gif_start = math.floor(video_length_in_seconds / 7) * 2
                third_gif_start = math.floor(video_length_in_seconds / 7) * 3
                fourth_gif_start = math.floor(video_length_in_seconds / 7) * 4
                fifth_gif_start = math.floor(video_length_in_seconds / 7) * 5
                sixth_gif_start = math.floor(video_length_in_seconds / 7) * 6
                seventh_gif_start = math.floor(video_length_in_seconds) - 30
                
                if not os.path.exists("{}{}".format(generator_config["gifs_path"], filename[:-4])): 
                    os.makedirs("{}{}".format(generator_config["gifs_path"], filename[:-4])) 
                
                #print("{}{}/{}.{}.gif".format(generator_config["gifs_path"],filename[:-4], filename, 1))
                      
                if not os.path.exists("{}{}/{}.{}.gif".format(generator_config["gifs_path"],filename[:-4], filename, 1)):
                    print("\tGenerating GIF1 at {}".format(first_gif_start))
                    create_gifs_from_video(f, first_gif_start, 2.5, 1)
                else:
                    if generator_config['overwrite_gifs']:
                        print("\tGenerating GIF1 at {}".format(first_gif_start))
                        create_gifs_from_video(
                            f, first_gif_start, 2.5, 1)
                    #else:
                    #    print("GIF1 at {} exists, skipping".format(
                    #        first_gif_start))

                if not os.path.exists("{}{}/{}.{}.gif".format(generator_config["gifs_path"],filename[:-4],filename, 2)):
                    print("\tGenerating GIF2 at {}".format(second_gif_start))
                    create_gifs_from_video(f, second_gif_start, 2.5, 2)
                else:
                    if generator_config['overwrite_gifs']:
                        print("Overwriting GIF2 at {}".format(second_gif_start))
                        create_gifs_from_video(
                            f, second_gif_start, 2.5, 2)
                    #else:
                    #    print("GIF2 at {} exists, skipping".format(
                    #        second_gif_start))

                if not os.path.exists("{}{}/{}.{}.gif".format(generator_config["gifs_path"],filename[:-4],filename, 3)):
                    print("\tGenerating GIF3 at {}".format(third_gif_start))
                    create_gifs_from_video(f, third_gif_start, 2.5, 3)
                else:
                    if generator_config['overwrite_gifs']:
                        print("\tOverwriting GIF3 at {}".format(third_gif_start))
                        create_gifs_from_video(
                            f, third_gif_start, 2.5, 1)
                    #else:
                    #    print("GIF3 at {} exists, skipping".format(
                    #        third_gif_start))

                if not os.path.exists("{}{}/{}.{}.gif".format(generator_config["gifs_path"],filename[:-4],filename, 4)):
                    print("\tGenerating GIF4 at {}".format(fourth_gif_start))
                    create_gifs_from_video(f, fourth_gif_start, 2.5, 4)
                else:
                    if generator_config['overwrite_gifs']:
                        print("\tOverwriting GIF4 at {}".format(fourth_gif_start))
                        create_gifs_from_video(
                            f, fourth_gif_start, 2.5, 1)
                    #else:
                    #    print("GIF4 at {} exists, skipping".format(
                    #        fourth_gif_start))
                            
                if not os.path.exists("{}{}/{}.{}.gif".format(generator_config["gifs_path"],filename[:-4],filename, 5)):
                    print("\tGenerating GIF5 at {}".format(fifth_gif_start))
                    create_gifs_from_video(f, (fifth_gif_start), 2.5, 5)
                else:
                    if generator_config['overwrite_gifs']:
                        print("\tOverwriting GIF5 at {}".format((fifth_gif_start)))
                        create_gifs_from_video(
                            f, (fifth_gif_start), 2.5, 1)
                    #else:
                        #print("GIF5 at {} exists, skipping".format(
                        #    (fifth_gif_start)))
                
                if not os.path.exists("{}{}/{}.{}.gif".format(generator_config["gifs_path"],filename[:-4],filename, 6)):
                    print("Generating GIF6 at {}".format(sixth_gif_start))
                    create_gifs_from_video(f, (sixth_gif_start), 2.5, 6)
                else:
                    if generator_config['overwrite_gifs']:
                        print("\tOverwriting GIF5 at {}".format((sixth_gif_start)))
                        create_gifs_from_video(
                            f, (sixth_gif_start), 2.5, 1)
                    #else:
                        #print("GIF6 at {} exists, skipping".format(
                        #    (sixth_gif_start)))
                
                if not os.path.exists("{}{}/{}.{}.gif".format(generator_config["gifs_path"],filename[:-4],filename, 7)):
                    print("\tGenerating GIF7 at {}".format(seventh_gif_start))
                    create_gifs_from_video(f, (seventh_gif_start), 2.5, 7)
                else:
                    if generator_config['overwrite_gifs']:
                        print("\tOverwriting GIF7 at frame {}".format((seventh_gif_start)))
                        create_gifs_from_video(
                            f, (seventh_gif_start), 2.5, 1)
                    #else:
                        #print("GIF6 at {} exists, skipping".format(
                        #    (seventh_gif_start)))
            files_scanned_so_far +=1
            total_files_in_catalog +=1
        print(" ")
        print("🦇 FOUND {} WEIRD FILES IN THE DIRECTORY 🦇".format(len(weird_files)))
        for f in weird_files:
            filename= os.path.basename(f)
            print(filename)
            video_length_in_seconds = video_length_seconds(f)
            video_title = get_video_title(f)
            total_length_in_seconds += math.floor(video_length_seconds(f))
            
            with open(f, 'rb') as file_to_check:
                # read contents of the file
                data = file_to_check.read()    
                # pipe contents of the file through
                md5_returned = hashlib.md5(data).hexdigest()
            
            file_size = os.path.getsize(f)
            file_size_mb = math.ceil((file_size / 1024)/1024)

            generator_config['types'][media_type]['weird_file_detail'][md5_returned] = {"video_title": video_title, "path": f, "filename": filename, "size": file_size, "duration_in_seconds": video_length_in_seconds}

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
    print(" {}: {} clean files, {} files with issues".format(media_type, len(
        updated_types[media_type]['good_files']), len(updated_types[media_type]['weird_files'])))

    print("    Total duration: {}".format(get_fancy_duration(updated_types[media_type]['total_length_in_seconds'])))

with open('{}/rstv media list good files.csv'.format(rstv_config.catalog_output_path), 'w', newline='') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',',
                            quoting=csv.QUOTE_MINIMAL)
    spamwriter.writerow(['Title','Media Type','Filename', 'Size (In Bytes)', 'Duration In Seconds','Full Path','md5','Issues'])
    for media_type in updated_types:
        for item in generator_config['types'][media_type]['items']:
            spamwriter.writerow([generator_config['types'][media_type]['items'][item]['video_title'], media_type, generator_config['types'][media_type]['items'][item]['filename'], generator_config['types'][media_type]['items'][item]['size'], generator_config['types'][media_type]['items'][item]['duration_in_seconds'],generator_config['types'][media_type]['items'][item]['path'], item])
            
with open('{}/rstv media weird files only.csv'.format(rstv_config.catalog_output_path), 'w', newline='') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',',
                            quoting=csv.QUOTE_MINIMAL)
    spamwriter.writerow(['Title','Media Type','Filename', 'Size (In Bytes)', 'Duration In Seconds','Full Path','md5','Issues'])
    for media_type in updated_types:
        for item in generator_config['types'][media_type]['weird_file_detail']:
            spamwriter.writerow([generator_config['types'][media_type]['weird_file_detail'][item]['video_title'], media_type, generator_config['types'][media_type]['weird_file_detail'][item]['filename'], generator_config['types'][media_type]['weird_file_detail'][item]['size'], generator_config['types'][media_type]['weird_file_detail'][item]['duration_in_seconds'],generator_config['types'][media_type]['weird_file_detail'][item]['path'], item, "Bad Metadata"])
            
with open('{}/rstv media list combined.csv'.format(rstv_config.catalog_output_path), 'w', newline='') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',',
                            quoting=csv.QUOTE_MINIMAL)
    spamwriter.writerow(['Title','Media Type','Filename', 'Size (In Bytes)', 'Duration In Seconds','Full Path','md5','Issues'])
    for media_type in updated_types:
        for item in generator_config['types'][media_type]['items']:
            spamwriter.writerow([generator_config['types'][media_type]['items'][item]['video_title'], media_type, generator_config['types'][media_type]['items'][item]['filename'],generator_config['types'][media_type]['items'][item]['size'], generator_config['types'][media_type]['items'][item]['duration_in_seconds'],generator_config['types'][media_type]['items'][item]['path'], item])
        for item in generator_config['types'][media_type]['weird_file_detail']:
            spamwriter.writerow([generator_config['types'][media_type]['weird_file_detail'][item]['video_title'], media_type, generator_config['types'][media_type]['weird_file_detail'][item]['filename'], generator_config['types'][media_type]['weird_file_detail'][item]['size'], generator_config['types'][media_type]['weird_file_detail'][item]['duration_in_seconds'],generator_config['types'][media_type]['weird_file_detail'][item]['path'], item, "Bad Metadata"])

toc = time.perf_counter()
print("Total files: {}".format(total_files_in_catalog))
print("Duration of all scanned media: {}".format(get_fancy_duration(all_media_total_length_in_seconds)))
print(f"Took {toc - tic:0.4f} seconds to scan. All done.")
