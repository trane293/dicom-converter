import SimpleITK as sitk
import os, glob
import logging
from modules.helpers import kw, match_rule_t1, match_rule_t2
import argparse
# Ignore warnings
import warnings
import sys
warnings.filterwarnings("ignore")

parser = argparse.ArgumentParser()
parser.add_argument('--path', type=str, default="/local-scratch2/VGH_Data/IMediaExport/DICOM/", help='path to folder containing patient folders in DICOM')
parser.add_argument('--save_path', type=str, default="default", help='save path to write processed images to. Default is to write in same directory under --path')
parser.add_argument('--resample', type=int, default=1, help='whether or not to resample individual series')
parser.add_argument('--target_shape', type=str, default="240x240x155", help='specify target shape to resample, requires --resample=1. Format WxHxZ')
parser.add_argument('--target_spacing', type=str, default="1x1x1", help='specify target spacing, required --resample=1. Format SxSxS')
parser.add_argument('--verbose', type=int, default=0, help='specify whether to output logging information (1) or not (0)')
parser.add_argument('--interpolator', type=int, default=0, help='voxel interpolator to use, requires --resample=1. (0) = BSpline, (1) = NearestNeighbour, (2) Linear')
parser.add_argument('--out_format', type=str, default="nii.gz", help='required output format of the files, can be any format that SimpleITK supports.')

opt = parser.parse_args()


if opt.verbose == 0:
    logging.basicConfig(level=logging.INFO)
else:
    logging.basicConfig(level=logging.DEBUG)

try:
    logger = logging.getLogger(__file__.split('/')[-1])
except:
    logger = logging.getLogger(__name__)
logger.info(opt)
path = opt.path
tags = {"Patient Name": "0010|0010",
        "Patient ID": "0010|0020",
        "Series Description": "0008|103e",
        "Modality": "0008|0060",
        "Contrast Agent": "0018|0010"
        }
pat_data = {}
patients = glob.glob(os.path.join(path, "*"))
for pat in patients:
    for curr_std in glob.glob(os.path.join(pat, "*")):
        for curr_series in glob.glob(os.path.join(curr_std, "*")):
            curr_series_obj = glob.glob(os.path.join(curr_series, "*"))[0]
            logger.debug( "Reading Dicom directory: {}".format(curr_series_obj))
            reader = sitk.ImageSeriesReader()

            dicom_names = reader.GetGDCMSeriesFileNames(curr_series_obj)
            if dicom_names == ():
                logger.debug("Empty folder {}".format(os.path.basename(curr_series_obj)))
                continue

            reader.SetFileNames(dicom_names)
            reader.MetaDataDictionaryArrayUpdateOn()
            reader.LoadPrivateTagsOn()
            try:
                image = reader.Execute()
            except RuntimeError as e:
                logger.info(e)
                continue

            no_flag = False
            # print only if I find Ax T1 in the study
            ser_desc = reader.GetMetaData(0, "0008|103e")
            pat_id = reader.GetMetaData(0, tags['Patient ID'])
            if not (pat_id in pat_data.keys()):
                pat_data[pat_id] = {
                    'T1': None,
                    'T2': None,
                    'T1CE': None,
                    'T2FLAIR': None
                }

            match_str = match_rule_t1(ser_desc, kw, reader)
            if isinstance(match_str, dict):
                match_str = match_rule_t2(ser_desc, kw)

                if isinstance(match_str, dict):
                    logger.debug('Patient {} Cannot match = {}'.format(reader.GetMetaData(0, tags['Patient Name']),
                                                                ser_desc))
                    continue
                else:
                    logger.debug("Matched Patient {}, SeriesDescription {} to {}".format(
                        reader.GetMetaData(0, tags['Patient Name']),
                        ser_desc, match_str))
            else:
                logger.debug("=" * 50)
                logger.debug(
                    "Matched Patient {}, SeriesDescription {} to {}".format(reader.GetMetaData(0, tags['Patient Name']),
                                                                            ser_desc, match_str))

            for ct, t in tags.items():
                try:
                    logger.info(ct + ": " + reader.GetMetaData(0, t))
                except RuntimeError:
                    logger.info('Key {} not present'.format(t))
            logger.info('Matched To: {}'.format(match_str))

            if opt.resample:
                target_shape = [int(x) for x in opt.target_shape.lower().split("x")]
                target_spacing = [int(x) for x in opt.target_spacing.lower().split("x")]
                if opt.interpolator == 0:
                    use_interpolator = sitk.sitkBSpline
                elif opt.interpolator == 1:
                    use_interpolator = sitk.sitkNearestNeighbor
                elif opt.interpolator == 2:
                    use_interpolator = sitk.sitkLinear
                else:
                    logger.error("Incorrect interpolator chosen, exiting!")
                    sys.exit(0)
                image = sitk.Resample(image, target_shape,
                                      sitk.Transform(),
                                      use_interpolator,
                                      image.GetOrigin(),
                                      target_spacing,
                                      image.GetDirection(),
                                      0.0,
                                      image.GetPixelID())
            size = image.GetSize()
            pat_data[pat_id][match_str] = image

            # sitk.Show(image)
            # input()
            logger.info("Image size: {}x{}x{}".format(size[0], size[1], size[2]))
            logger.info("-" * 50)
            logger.info("")

if opt.save_path == "default":
    save_path = os.path.join(os.path.sep.join(path.split(os.path.sep)[0:-2]), "Cleaned_Data")
else:
    save_path = opt.save_path

for k in pat_data.keys():
    pat_path = os.path.join(save_path, k)
    for s in pat_data[k].keys():
        if pat_data[k][s] is not None:
            # seq_path = os.path.join(pat_path, s)

            if 'FLAIR' in s:
                seq_name = os.path.join(pat_path, "Image_flair.{}".format(opt.out_format))
            else:
                seq_name = os.path.join(pat_path, "Image_{}.{}".format(s.lower(), opt.out_format))
            if not os.path.exists(pat_path):
                os.makedirs(pat_path)

            sitk.WriteImage(pat_data[k][s], seq_name)