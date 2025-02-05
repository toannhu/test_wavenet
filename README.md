# A TensorFlow implementation of DeepMind's WaveNet paper

[![Build Status](https://travis-ci.org/ibab/tensorflow-wavenet.svg?branch=master)](https://travis-ci.org/ibab/tensorflow-wavenet)

This is a TensorFlow implementation of the [WaveNet generative neural
network architecture](https://deepmind.com/blog/wavenet-generative-model-raw-audio/) for audio generation.

<table style="border-collapse: collapse">
<tr>
<td>
<p>
The WaveNet neural network architecture directly generates a raw audio waveform,
showing excellent results in text-to-speech and general audio generation (see the
DeepMind blog post and paper for details).
</p>
<p>
The network models the conditional probability to generate the next
sample in the audio waveform, given all previous samples and possibly
additional parameters.
</p>
<p>
After an audio preprocessing step, the input waveform is quantized to a fixed integer range.
The integer amplitudes are then one-hot encoded to produce a tensor of shape <code>(num_samples, num_channels)</code>.
</p>
<p>
A convolutional layer that only accesses the current and previous inputs then reduces the channel dimension.
</p>
<p>
The core of the network is constructed as a stack of <em>causal dilated layers</em>, each of which is a
dilated convolution (convolution with holes), which only accesses the current and past audio samples.
</p>
<p>
The outputs of all layers are combined and extended back to the original number
of channels by a series of dense postprocessing layers, followed by a softmax
function to transform the outputs into a categorical distribution.
</p>
<p>
The loss function is the cross-entropy between the output for each timestep and the input at the next timestep.
</p>
<p>
In this repository, the network implementation can be found in <a href="./wavenet/model.py">model.py</a>.
</p>
</td>
<td width="300">
<img src="images/network.png" width="300"></img>
</td>
</tr>
</table>

## Requirements

TensorFlow needs to be installed before running the training script.
Code is tested on TensorFlow version 0.12.1 for Python 2.7 and Python 3.5.

In addition, [librosa](https://github.com/librosa/librosa) must be installed for reading and writing audio.

To install the required python packages (except TensorFlow), run
```bash
pip install -r requirements.txt
```

## Training the network

You can use any corpus containing `.wav` files.
We've mainly used the [VCTK corpus](http://homepages.inf.ed.ac.uk/jyamagis/page3/page58/page58.html) (around 10.4GB, [Alternative host](http://www.udialogue.org/download/cstr-vctk-corpus.html)) so far.

In order to train the network, execute
```bash
python train.py --data_dir=corpus
```
to train the network, where `corpus` is a directory containing `.wav` files.
The script will recursively collect all `.wav` files in the directory.

You can see documentation on each of the training settings by running
```bash
python train.py --help
```

You can find the configuration of the model parameters in [`wavenet_params.json`](./wavenet_params.json).
These need to stay the same between training and generation.

### Global Conditioning
Global conditioning refers to modifying the model such that the id of a set of mutually-exclusive categories is specified during training and generation of .wav file.
In the case of the VCTK, this id is the integer id of the speaker, of which there are over a hundred.
This allows (indeed requires) that a speaker id be specified at time of generation to select which of the speakers it should mimic. For more details see the paper or source code.

### Training with Global Conditioning
The instructions above for training refer to training without global conditioning. To train with global conditioning, specify command-line arguments as follows:
```
python train.py --data_dir=corpus --gc_channels=32
```
The --gc_channels argument does two things:
* It tells the train.py script that
it should build a model that includes global conditioning.
* It specifies the
size of the embedding vector that is looked up based on the id of the speaker.

The global conditioning logic in train.py and audio_reader.py is "hard-wired" to the VCTK corpus at the moment in that it expects to be able to determine the speaker id from the pattern of file naming used in VCTK, but can be easily be modified.

### Local Conditioning
Local conditioning refers to summing a convolved and upsampled time series of labels
with the raw audio during training. Each wav file in the data directory must have
a corresponding JSON label file with the same name as the wav file. The JSON label
file should represent an array of feature vectors.

In the example case "data-amajor," the feature vector is 3 concatenated 4-length
one-hot-vectors whose indexes represent the F0 of the sine wav (silence, A, C#,
and E) at that time in the wav file.

To clarify, indexes 0-3 are the F0 of the previous label, indexes 4-7 are F0 of the
current label, and indexes 8-11 are the F0 of the next example.

The label samples are automatically upsampled to match the audio frequency (based
on the sample length of the label vector and the sample length of the audio file).

[Example output](https://soundcloud.com/user-763760918/wavenet-localconditioning-on-f0-of-sin-waves)

### Training with Local Conditioning

To train with local conditioning, specify command-line arguments as follow:
```
python train.py --data_dir=data-amajor --logdir=log-amajor --lc_channels=12
```

The `--lc_channels` argument specifies the size of the local conditioning embedding vector.


## Generating audio

[Example output](https://soundcloud.com/user-731806733/tensorflow-wavenet-500-msec-88k-train-steps)
generated by @jyegerlehner based on speaker 280 from the VCTK corpus.

You can use the `generate.py` script to generate audio using a previously trained model.

### Generating without Global or Local Conditioning
Run
```
python generate.py --samples 16000 logdir/train/2017-02-13T16-45-34/model.ckpt-80000
```
where `logdir/train/2017-02-13T16-45-34/model.ckpt-80000` needs to be a path to previously saved model (without extension).
The `--samples` parameter specifies how many audio samples you would like to generate (16000 corresponds to 1 second by default).

The generated waveform can be played back using TensorBoard, or stored as a
`.wav` file by using the `--wav_out_path` parameter:
```
python generate.py --wav_out_path=generated.wav --samples 16000 logdir/train/2017-02-13T16-45-34/model.ckpt-80000
```

Passing `--save_every` in addition to `--wav_out_path` will save the in-progress wav file every n samples.
```
python generate.py --wav_out_path=generated.wav --save_every 2000 --samples 16000 logdir/train/2017-02-13T16-45-34/model.ckpt-80000
```

Fast generation is enabled by default.
It uses the implementation from the [Fast Wavenet](https://github.com/tomlepaine/fast-wavenet) repository.
You can follow the link for an explanation of how it works.
This reduces the time needed to generate samples to a few minutes.

To disable fast generation:
```
python generate.py --samples 16000 logdir/train/2017-02-13T16-45-34/model.ckpt-80000 --fast_generation=false
```

### Generating with Global Conditioning
Generate from a model incorporating global conditioning as follows:
```
python generate.py --samples 16000  --wav_out_path speaker311.wav --gc_channels=32 --gc_cardinality=377 --gc_id=311 logdir/train/2017-02-13T16-45-34/model.ckpt-80000
```
Where:

`--gc_channels=32` specifies 32 is the size of the embedding vector, and
must match what was specified when training.

`--gc_cardinality=377` is required
as 376 is the largest id of a speaker in the VCTK corpus. If some other corpus
is used, then this number should match what is automatically determined and
printed out by the train.py script at training time.

`--gc_id=311` specifies the id of speaker, speaker 311, for which a sample is
to be generated.

### Generating with Local Conditioning
Generate from a model incorporating local conditioning as follows:
```
python ./generate.py --samples 32000 --lc_label_file ./amajor-gen-3.json --wav_out_path amajor-3-1000steps-1.wav ./log-amajor/model.ckpt-1000
```
Where:

`--lc_label_file` is a JSON file that contains an array of feature vectors with the same length as that which trained
the model originally. The upsampling frequency will automatically be determined by the length of the labels array and
the number of samples parameter.

## Running tests

Install the test requirements
```
pip install -r requirements_test.txt
```

Run the test suite
```
./ci/test.sh
```

## Missing features

Currently there is no local conditioning on extra information which would allow
context stacks or controlling what speech is generated.


## Related projects

- [tex-wavenet](https://github.com/Zeta36/tensorflow-tex-wavenet), a WaveNet for text generation.
- [image-wavenet](https://github.com/Zeta36/tensorflow-image-wavenet), a WaveNet for image generation.
