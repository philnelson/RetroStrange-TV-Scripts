import csv
import hashlib
import json
import math
import os
from os.path import exists
from pathlib import Path
import random
import re
import subprocess
import time
import threading

import rstv_config

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
        "stationids": {
            "update": True,
            "path": rstv_config.stationid_path,
            "items": {},
            "weird_file_detail": {},
        },
        "staging": {
            "update": True,
            "path": rstv_config.staging_path,
            "items": {},
            "weird_file_detail": {},
        },
    },
    "number_of_gifs_to_generate": 10,
    "gifs_path": rstv_config.gifs_path,
    "create_gifs": True,
    "overwrite_gifs": True,
}


def seconds_to_hms(seconds: float) -> str:
    # Round up to the nearest whole second
    total_seconds = int(math.ceil(seconds))

    # Compute hours, minutes and remaining seconds
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60

    # Helper for pluralisation
    def fmt(value, singular, plural):
        return f"{value} {singular if value == 1 else plural}"

    return (
        f"{fmt(hours, 'hour', 'hours')} "
        f"{fmt(minutes, 'minute', 'minutes')} "
        f"{fmt(secs, 'second', 'seconds')}"
    )


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
    cmd = [
        "ffprobe",
        "-v",
        "quiet",
        "-print_format",
        "json",
        "-show_entries",
        "format_tags=title",
        file_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        # Parse JSON output and extract title
        metadata = json.loads(result.stdout)

        if (
            "format" in metadata
            and "tags" in metadata["format"]
            and "title" in metadata["format"]["tags"]
        ):
            title = metadata["format"]["tags"]["title"]
        else:
            title = None
        return title
    else:
        raise ValueError(result.stderr.rstrip("\n"))


def create_gifs_from_video(file, start, duration, seq):
    filename = os.path.basename(file)
    path = filename[:-4]
    # print(f'{generator_config["gifs_path"]}{path}/{filename}.{seq}.gif')
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
            f"{generator_config['gifs_path']}{path}/{filename}.{seq}.gif",
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
            f"{generator_config['gifs_path']}{path}/{filename}.{seq}.gif",
            f"{generator_config['gifs_path']}{path}/{filename}.{seq}.gif",
        ],
        capture_output=True,
        text=True,
    )

    try:
        return str(output)
    except ValueError:
        raise ValueError(result.stderr.rstrip("\n"))


tic = time.perf_counter()

print("""
##########################################################################################
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
##########################################################################################
""")
total_files_in_catalog = 0
for media_type in generator_config["types"]:
    print("------")
    if not generator_config["types"][media_type]["update"]:
        print("Skipping {} update due to config".format(media_type))
        skipped_types.append(media_type)
    else:
        path = generator_config["types"][media_type]["path"]
        good_files = []
        weird_files = []
        weird_file_detail = {}

        print("🦇 SOARING MAJESTICALLY OVER {} IN {} 🦇".format(media_type, path))
        print(" ")
        # Check for all *.mp4" filenames
        # r=root, d=directories, f = files
        for r, d, f in os.walk(path):
            for file in f:
                if not file.startswith("."):
                    if ".mp4" in file or ".m4v" in file:
                        if ".gif" not in file:
                            # print(file)
                            # Check for year in filename
                            if bool(re.search(r"\(\d{4}\)", file)):
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
            filename = os.path.basename(f)
            video_length_in_seconds = video_length_seconds(f)
            video_title = get_video_title(f)
            total_length_in_seconds += math.floor(video_length_in_seconds)

            with open(f, "rb") as file_to_check:
                # read contents of the file
                data = file_to_check.read()
                # pipe contents of the file through
                md5_returned = hashlib.md5(data).hexdigest()

            file_size = os.path.getsize(f)
            file_size_mb = math.ceil((file_size / 1024) / 1024)

            generator_config["types"][media_type]["items"][md5_returned] = {
                "video_title": video_title,
                "path": f,
                "filename": filename,
                "size": file_size,
                "duration_in_seconds": video_length_in_seconds,
            }

            print(
                "{} [{}/{}] {}".format(
                    media_type,
                    files_scanned_so_far + 1,
                    total_files_to_scan,
                    md5_returned,
                )
            )
            print(
                "\tFile: {} \n\tDuration: {}, Size: {}mb".format(
                    filename, seconds_to_hms(video_length_in_seconds), file_size_mb
                )
            )

            if generator_config["create_gifs"]:
                gif_threads = []

                for gif_iterator in range(
                    1, generator_config["number_of_gifs_to_generate"] + 1
                ):
                    if gif_iterator == 1:
                        # 30s from the start
                        gif_start = (
                            math.floor(
                                video_length_in_seconds
                                / generator_config["number_of_gifs_to_generate"]
                            )
                            + 30
                        )
                    elif (
                        gif_iterator
                        == generator_config["number_of_gifs_to_generate"] + 1
                    ):
                        # 30s from the end
                        gif_start = math.floor(video_length_in_seconds) - 30
                    else:
                        gif_start = (
                            math.floor(
                                video_length_in_seconds
                                / generator_config["number_of_gifs_to_generate"]
                            )
                            * gif_iterator
                        )

                    if not os.path.exists(
                        "{}{}".format(generator_config["gifs_path"], filename[:-4])
                    ):
                        os.makedirs(
                            "{}{}".format(generator_config["gifs_path"], filename[:-4])
                        )

                    if not os.path.exists(
                        "{}{}/{}.{}.gif".format(
                            generator_config["gifs_path"],
                            filename[:-4],
                            filename,
                            gif_iterator,
                        )
                    ):
                        print(
                            "\tGenerating GIF {} at {}s".format(gif_iterator, gif_start)
                        )

                        # create_gifs_from_video(f, gif_start, 2.5, gif_iterator)
                        t = threading.Thread(
                            target=create_gifs_from_video,
                            args=(
                                f,
                                gif_start,
                                2.5,
                                gif_iterator,
                            ),
                        )
                        gif_threads.append(t)
                    else:
                        if generator_config["overwrite_gifs"]:
                            print(
                                "\tOverwriting GIF-{} at {}".format(
                                    gif_iterator, gif_start
                                )
                            )
                            # create_gifs_from_video(f, gif_start, 2.5, gif_iterator)
                            t = threading.Thread(
                                target=create_gifs_from_video,
                                args=(
                                    f,
                                    gif_start,
                                    2.5,
                                    gif_iterator,
                                ),
                            )
                            gif_threads.append(t)

            files_scanned_so_far += 1
            total_files_in_catalog += 1

            # Start each thread
            for t in gif_threads:
                t.start()

            # Wait for all threads to finish
            for t in gif_threads:
                t.join()

        print(" ")
        print("🦇 FOUND {} WEIRD FILES IN THE DIRECTORY 🦇".format(len(weird_files)))
        for f in weird_files:
            filename = os.path.basename(f)
            print(filename)
            video_length_in_seconds = video_length_seconds(f)
            video_title = get_video_title(f)
            total_length_in_seconds += math.floor(video_length_seconds(f))

            with open(f, "rb") as file_to_check:
                # read contents of the file
                data = file_to_check.read()
                # pipe contents of the file through
                md5_returned = hashlib.md5(data).hexdigest()

            file_size = os.path.getsize(f)
            file_size_mb = math.ceil((file_size / 1024) / 1024)

            generator_config["types"][media_type]["weird_file_detail"][md5_returned] = {
                "video_title": video_title,
                "path": f,
                "filename": filename,
                "size": file_size,
                "duration_in_seconds": video_length_in_seconds,
            }

        print(" ")
        print("🦇 STATS FOR THE {} PROPERLY FORMATTED FILES 🦇".format(len(good_files)))
        print("Total duration {}".format(seconds_to_hms(total_length_in_seconds)))
        print("------")

        updated_types[media_type] = {
            "good_files": good_files,
            "weird_files": weird_files,
            "total_length_in_seconds": total_length_in_seconds,
        }

if len(skipped_types) > 0:
    print(
        "Skipped {} media types: {}".format(
            len(skipped_types), "%s" % ", ".join(map(str, skipped_types))
        )
    )
else:
    print("Skipped no media types.")

if len(updated_types) > 0:
    print(
        "Updated {} media types: {}".format(
            len(updated_types), "%s" % ", ".join(map(str, updated_types))
        )
    )
else:
    print("Updated no media types.")

all_media_total_length_in_seconds = 0
for media_type in updated_types:
    all_media_total_length_in_seconds += updated_types[media_type][
        "total_length_in_seconds"
    ]
    print(
        " {}: {} clean files, {} files with issues".format(
            media_type,
            len(updated_types[media_type]["good_files"]),
            len(updated_types[media_type]["weird_files"]),
        )
    )

    print(
        "    Total duration: {}".format(
            seconds_to_hms(updated_types[media_type]["total_length_in_seconds"])
        )
    )
    with open(
        "{}/RetroStrange TV Catalog {}.csv".format(
            rstv_config.catalog_output_path, media_type
        ),
        "w",
        newline="",
    ) as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=",", quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow(
            [
                "Title",
                "Media Type",
                "Filename",
                "Size (In Bytes)",
                "Duration In Seconds",
                "GIFs",
                "checksum",
            ]
        )
        for item in generator_config["types"][media_type]["items"]:
            folder_name = generator_config["types"][media_type]["items"][item][
                "filename"
            ][:-4]

            spamwriter.writerow(
                [
                    generator_config["types"][media_type]["items"][item]["video_title"],
                    media_type,
                    generator_config["types"][media_type]["items"][item]["filename"],
                    generator_config["types"][media_type]["items"][item]["size"],
                    generator_config["types"][media_type]["items"][item][
                        "duration_in_seconds"
                    ],
                    "https://retrostrange.com/gifs/{}/{}.html".format(
                        folder_name, folder_name
                    ),
                    item,
                ]
            )

with open(
    "{}/RetroStrange TV Catalog in-rotation files.csv".format(
        rstv_config.catalog_output_path
    ),
    "w",
    newline="",
) as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=",", quoting=csv.QUOTE_MINIMAL)
    spamwriter.writerow(
        [
            "Title",
            "Media Type",
            "Filename",
            "Size (In Bytes)",
            "Duration In Seconds",
            "Full Path",
            "md5",
        ]
    )
    for media_type in updated_types:
        for item in generator_config["types"][media_type]["items"]:
            spamwriter.writerow(
                [
                    generator_config["types"][media_type]["items"][item]["video_title"],
                    media_type,
                    generator_config["types"][media_type]["items"][item]["filename"],
                    generator_config["types"][media_type]["items"][item]["size"],
                    generator_config["types"][media_type]["items"][item][
                        "duration_in_seconds"
                    ],
                    generator_config["types"][media_type]["items"][item]["path"],
                    item,
                ]
            )

with open(
    "{}/RetroStrange TV Catalog problem files only.csv".format(
        rstv_config.catalog_output_path
    ),
    "w",
    newline="",
) as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=",", quoting=csv.QUOTE_MINIMAL)
    spamwriter.writerow(
        [
            "Title",
            "Media Type",
            "Filename",
            "Size (In Bytes)",
            "Duration In Seconds",
            "Full Path",
            "md5",
            "Issues",
        ]
    )
    for media_type in updated_types:
        for item in generator_config["types"][media_type]["weird_file_detail"]:
            spamwriter.writerow(
                [
                    generator_config["types"][media_type]["weird_file_detail"][item][
                        "video_title"
                    ],
                    media_type,
                    generator_config["types"][media_type]["weird_file_detail"][item][
                        "filename"
                    ],
                    generator_config["types"][media_type]["weird_file_detail"][item][
                        "size"
                    ],
                    generator_config["types"][media_type]["weird_file_detail"][item][
                        "duration_in_seconds"
                    ],
                    generator_config["types"][media_type]["weird_file_detail"][item][
                        "path"
                    ],
                    item,
                    "Bad Metadata",
                ]
            )

with open(
    "{}/RetroStrange TV Catalog all combined.csv".format(
        rstv_config.catalog_output_path
    ),
    "w",
    newline="",
) as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=",", quoting=csv.QUOTE_MINIMAL)
    spamwriter.writerow(
        [
            "Title",
            "Media Type",
            "Filename",
            "Size (In Bytes)",
            "Duration In Seconds",
            "Full Path",
            "md5",
            "Issues",
        ]
    )
    for media_type in updated_types:
        for item in generator_config["types"][media_type]["items"]:
            spamwriter.writerow(
                [
                    generator_config["types"][media_type]["items"][item]["video_title"],
                    media_type,
                    generator_config["types"][media_type]["items"][item]["filename"],
                    generator_config["types"][media_type]["items"][item]["size"],
                    generator_config["types"][media_type]["items"][item][
                        "duration_in_seconds"
                    ],
                    generator_config["types"][media_type]["items"][item]["path"],
                    item,
                ]
            )
        for item in generator_config["types"][media_type]["weird_file_detail"]:
            spamwriter.writerow(
                [
                    generator_config["types"][media_type]["weird_file_detail"][item][
                        "video_title"
                    ],
                    media_type,
                    generator_config["types"][media_type]["weird_file_detail"][item][
                        "filename"
                    ],
                    generator_config["types"][media_type]["weird_file_detail"][item][
                        "size"
                    ],
                    generator_config["types"][media_type]["weird_file_detail"][item][
                        "duration_in_seconds"
                    ],
                    generator_config["types"][media_type]["weird_file_detail"][item][
                        "path"
                    ],
                    item,
                    "Bad Metadata",
                ]
            )

toc = time.perf_counter()
print("Total files: {}".format(total_files_in_catalog))
print(
    "Duration of all scanned media: {}".format(
        seconds_to_hms(all_media_total_length_in_seconds)
    )
)
print(f"Took {toc - tic:0.4f} seconds to scan. All done.")
