import glob
import os
from tqdm import *

def rename_json(start_num=0):
    for infile in tqdm(sorted(glob.glob('*.json'))):
        print("Current File Being Processed is: ", infile, " ", str(start_num))
        os.rename(infile, "audio_" + str(start_num) + ".json")
        start_num += 1

rename_json(8000)