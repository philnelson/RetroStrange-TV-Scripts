import sys
from pathlib import Path

import cv2

import rstv_config

if len(sys.argv) != 1:

    print(sys.argv[1])

    file_prefix = Path(sys.argv[1]).stem

    vidcap = cv2.VideoCapture(sys.argv[1])
    success,image = vidcap.read()
    frame = 0
    count = 0
    while success:
        success,image = vidcap.read()
        if count == 10000: # save a screenshot every X frames
            print("saving {}_{}.jpg".format(file_prefix, frame))
            cv2.imwrite("{}_{}.jpg".format(file_prefix, frame), image)    
            count = 0
        count += 1
        frame += 1
else:
    print("This script takes one argument: The file to screenshot")