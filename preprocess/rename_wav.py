import glob
import os
from tqdm import *

def rename_wav(start_num=0):
    for infile in tqdm(sorted(glob.glob('*.wav'))):
        print("Current File Being Processed is: ", infile, " ", str(start_num))
        os.rename(infile, "audio_" + str(start_num) + ".wav")
        start_num += 1

rename_wav(8000)