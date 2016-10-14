"""
UBC Eye Movement Data Analysis Toolkit (EMDAT), Version 3
Created on 2015-07-21

Sample code to run EMDAT for a given experiment.

@author: Mike Wu (creator), Sebastien Lalle
Institution: The University of British Columbia.
"""

from BasicParticipant import *
from EMDAT_core.Participant import export_features_all, write_features_tsv
from EMDAT_core.ValidityProcessing import output_Validity_info_Segments, output_percent_discarded, output_Validity_info_Participants

ul = [67]
uids = ul
alogoffset = [0]

# Read participants
ps = read_participants_Basic(user_list=ul, pids=uids, log_time_offsets=alogoffset, datadir=params.EYELOGDATAFOLDER,
                             prune_length=None, require_valid_segs=False, auto_partition_low_quality_segments=True)


if params.DEBUG or params.VERBOSE == "VERBOSE":
    # explore_validation_threshold_segments(ps, auto_partition_low_quality_segments = False)
    output_Validity_info_Segments(ps, auto_partition_low_quality_segments_flag=False, validity_method=3)
    output_percent_discarded(ps, './outputfolder/smi_disc.csv')
    output_Validity_info_Segments(ps, auto_partition_low_quality_segments_flag=False, validity_method=2,
                              threshold_gaps_list=[100, 200, 250, 300], output_file="./outputfolder/smi_Seg_val.csv")
output_Validity_info_Participants(ps, include_restored_samples=True, auto_partition_low_quality_segments_flag=False)


# WRITE features to file
if params.VERBOSE != "QUIET":
    print "Exporting features:\n--General:", params.featurelist
write_features_tsv(ps, './outputfolder/smi_sample_features.tsv', featurelist=params.featurelist, id_prefix=False)
