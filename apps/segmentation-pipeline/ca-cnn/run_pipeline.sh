#!/usr/bin/bash

cd ../../..
/grad/3/asa224/.virtualenvs/vgh/bin/python process_vgh_data.py --path="/local-scratch2/VGH_Data/IMediaExport/DICOM/" --resample=1 --target_shape=240x240x155 --target_spacing=1x1x1 --verbose=0 --interpolator=0

cd apps/segmentation-pipeline/ca-cnn
mkdir data
mv /local-scratch2/VGH_Data/IMediaExport/Cleaned_Data ./data/
mkdir seg_out
cd data
ls -d */* -1 > ../config18/test_names.txt
cd ..
/local-scratch/.virtualenvs/seg/bin/python evaluate_model.py config18/test_all_class.txt