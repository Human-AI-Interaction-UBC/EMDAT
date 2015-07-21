from BasicParticipant import *
from Participant import write_features_tsv
from ValidityProcessing import output_Validity_info_Segments, output_percent_discarded, \
    output_Validity_info_Participants

ul = [67]
uids = ul
alogoffset = [0]

# Read participants
ps = read_participants_Basic(user_list=ul, pids=uids, log_time_offsets=alogoffset, datadir=params.EYELOGDATAFOLDER,
                             prune_length=None, require_valid_segs=False, auto_partition_low_quality_segments=True)

# explore_validation_threshold_segments(ps, auto_partition_low_quality_segments = False)
output_Validity_info_Segments(ps, auto_partition_low_quality_segments_flag=False, validity_method=3)
output_percent_discarded(ps, './outputfolder/smi_disc.csv')
output_Validity_info_Segments(ps, auto_partition_low_quality_segments_flag=False, validity_method=2,
                              threshold_gaps_list=[100, 200, 250, 300], output_file="./outputfolder/smi_Seg_val.csv")
output_Validity_info_Participants(ps, include_restored_samples=True, auto_partition_low_quality_segments_flag=False)


# WRITE features to file
print "Exporting:\n--General:", params.featurelist
write_features_tsv(ps, './outputfolder/smi_sample_features.tsv', featurelist=params.featurelist, id_prefix=False)
