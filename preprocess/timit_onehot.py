import tensorflow as tf
import numpy as np
import re
import math
from pprint import pprint
from collections import OrderedDict

np.set_printoptions(threshold=np.nan)

# Silence
re_silence = [u'H# ']

re_phones = [
             u'B ',
             u'D ',
             u'G ',
             u'P ',
             u'T ',
             u'K ',
             u'DX ',
             u'Q ',

             u'BCL ',
             u'DCL ',
             u'GCL ',
             u'PCL ',
             u'TCL ',
             u'KCL ',

             u'DCL ',
             u'TCL ',

             u'JH ',
             u'CH ',

             u'S ',
             u'SH ',
             u'Z ',
             u'ZH ',
             u'F ',
             u'TH ',
             u'V ',
             u'DH ',

             u'M ',
             u'N ',
             u'NG ',
             u'EM ',
             u'EN ',
             u'ENG ',
             u'NX ',

             u'L ',
             u'R ',
             u'W ',
             u'Y ',
             u'HH ',
             u'HV ',
             u'EL ',

             u'IY ',
             u'IH ',
             u'EH ',
             u'EY ',
             u'AE ',
             u'AA ',
             u'AW ',
             u'AY ',
             u'AH ',
             u'AO ',
             u'OY ',
             u'OW ',
             u'UH ',
             u'UW ',
             u'UX ',
             u'ER ',
             u'AX ',
             u'IX ',
             u'AXR ',
             u'AX-H ',

             u'PAU ',
             u'EPI ',
             u'1 ',
             u'2 '
             ]

keys = re_silence + re_phones
values = np.arange(0, len(keys), 1, dtype=np.uint16)
my_dict = OrderedDict(zip(keys, values))

def APRABet_to_Num(str):
    return list(my_dict.keys()).index(str + ' ')

def OneHotEncoding(input, extra='None'):

    # array = re.split('\W+', input)

    indices = list(map(lambda x: APRABet_to_Num(x), input))
    depth = 64
    if extra == 'None':
        res = tf.one_hot(indices, depth, dtype=tf.uint16)
    else:
        pass

    with tf.Session() as sess:
         return sess.run(res)


def LoadPHN(file):
    phonemes = []
    duration = []
    count = 0
    with open(file, 'r') as infile:
        for line in infile:
            start_time = 0;
            end_time = 0;
            for elem in line.split(' '):
                if (count == 0):
                    start_time = elem
                elif (count == 1):
                    end_time = elem
                    duration.append((start_time, end_time))
                elif (count == 2):
                    phonemes.append(elem.strip('\n').upper())
                    count = 0;
                    continue
                count += 1;

    return phonemes, duration

def ToJSON(string):
    result = []
    result.extend([string[0], string[0], string[0]])
    for count, elem in enumerate(string):
        if (count <= len(string) - 3): 
            result.extend([string[count], string[count+1], string[count+2]])

    result.extend([string[0], string[0], string[0]])
    return result

phonemes, duration = LoadPHN('SA2.PHN')
res = ToJSON(phonemes)
result = OneHotEncoding(res)

count = 0
final = []
temp = [] 
for elem in result:
    if (count < 3):
        for item in elem.tolist():
            temp.append(item)
        count += 1
        if (count == 3):
            final.append(temp)
            temp = []
    elif (count == 3):
        for item in elem.tolist():
            temp.append(item)
        count = 1

print(len(duration))
print(len(phonemes))
print(len(result))
print(len(final))

# for training purpose
training_upsampled_labels = []
for count, elem in enumerate(duration):
    length = int(elem[1]) - int(elem[0])
    duration_size = math.ceil(0.0625 * length / 5)
    training_upsampled_labels += np.repeat([final[count]], duration_size, axis=0).tolist()

with open('amajor-v2.json', 'w') as outfile:
    outfile.write(str(training_upsampled_labels))

# for generating purpose
upsampled_labels = []
for count, elem in enumerate(duration):
    length = int(elem[1]) - int(elem[0])
    upsampled_labels += np.repeat([final[count]], length, axis=0).tolist()

# print(len(upsampled_labels))

with open('amajor-v2-gen-1.json', 'w') as outfile:
    # outfile.write(str(final))
    outfile.write(str(upsampled_labels))


# def upsample_labels(labels, num_samples):
#     label_size = len(labels)
#     label_channel_size = len(labels[0])
#     ratio = num_samples//label_size
#     upsampled_labels = []
#     for label in labels:
#         upsampled_labels += np.repeat([label], ratio, axis=0).tolist()
#     upsampled_len = len(upsampled_labels)
#     if upsampled_len < num_samples:
#         upsampled_labels += np.repeat([labels[-1]], num_samples-upsampled_len, axis=0).tolist()
#     upsampled_labels = np.array(upsampled_labels, dtype=np.float32)
#     upsampled_labels = np.resize(upsampled_labels, [np.shape(upsampled_labels)[0], label_channel_size])
#     return upsampled_labels
