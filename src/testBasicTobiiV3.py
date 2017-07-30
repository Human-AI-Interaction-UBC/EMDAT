"""
UBC Eye Movement Data Analysis Toolkit (EMDAT), Version 3
Created on 2015-08-15

Sample code to run EMDAT for a given experiment.

@author: Sebastien Lalle (creator)
Institution: The University of British Columbia.
"""

from BasicParticipant import *
from EMDAT_core.Participant import export_features_all, write_features_tsv
from EMDAT_core.ValidityProcessing import output_Validity_info_Segments, output_percent_discarded, output_Validity_info_Participants

ul = ['17', '18']
# for i in range(101, 143):
#     ul.append(str(i) + "a")
#     ul.append(str(i) + "b")
# for i in range(144, 163):
#     ul.append(str(i) + "a")
#     ul.append(str(i) + "b")
uids = ul
alogoffset = [0]*len(ul)

#aoifile_name = "single_aoi.aoi"
#aoifile_name = "grid2x2.aoi"
#aoifile_name = "viz-specific.aoi"

#aoifile_name = "single_aoi_dynamic.aoi"
#aoifile_name = "grid2x2_dynamic.aoi"

aoifile_name = None

# Read participants
ps = read_participants_Basic(user_list=ul, pids=uids, log_time_offsets=alogoffset, datadir=params.EYELOGDATAFOLDER,
                             aoifile= aoifile_name,
                             prune_length=None,
                             require_valid_segs=False,
                             auto_partition_low_quality_segments=False)


if params.DEBUG or params.VERBOSE == "VERBOSE":
    # explore_validation_threshold_segments(ps, auto_partition_low_quality_segments = False)
    output_Validity_info_Segments(ps, auto_partition_low_quality_segments_flag=False, validity_method=3)
    output_percent_discarded(ps, './outputfolder/smi_disc.csv')
    output_Validity_info_Segments(ps, auto_partition_low_quality_segments_flag=False, validity_method=2,
                              threshold_gaps_list=[100, 200, 250, 300], output_file="./outputfolder/tobiiv3_Seg_val.csv")
    output_Validity_info_Participants(ps, include_restored_samples=True, auto_partition_low_quality_segments_flag=False)


# WRITE features to file
if params.VERBOSE != "QUIET":
    print
    print "Exporting:\n--General:", params.featurelist
write_features_tsv(ps, './outputfolder/tobiiv3_sample_features.tsv', featurelist=params.featurelist, id_prefix=False)
