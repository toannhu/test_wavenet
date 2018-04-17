python3 train.py --data_dir=data-amajor --logdir=log-amajor --lc_channels=192

python3 train.py --data_dir=data-amajor --logdir=log-amajor --lc_channels=285

python3 train.py --data_dir=data-amajor --logdir=log-amajor --lc_channels=603
*Stop at 50

python3 ./generate.py --samples 58000 --lc_label_file ./amajor.json --wav_out_path amajor-1450steps-1.wav ./log-amajor/model.ckpt-1450

