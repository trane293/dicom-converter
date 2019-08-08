#!/usr/bin/env bash

#python train.py config18/new/train_wt_ax.txt
#python train.py config18/new/train_wt_sg.txt
#python train.py config18/new/train_wt_cr.txt

#python train.py config18/new/train_tc_ax.txt
python train.py config18/new/train_tc_sg.txt
python train.py config18/new/train_tc_cr.txt

python train.py config18/new/train_en_ax.txt
python train.py config18/new/train_en_sg.txt
python train.py config18/new/train_en_cr.txt
