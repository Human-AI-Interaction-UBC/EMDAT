'''
Created on 2012-08-23

@author: skardan
'''
from BasicParticipant import *
from Participant import export_features_all, write_features_tsv
from ValidityProcessing import output_Validity_info_Segments, output_percent_discarded, output_Validity_info_Participants

ul =        [61, 62]    # list of user recordings (files extracted for one participant from Tobii studio)
uids =      [61, 62]    # User ID that is used in the external logs (can be different from above but there should be a 1-1 mapping)

alogoffset =[ 3,  2]    # the time sifference between the eye tracker logs and the external log

###### Read participants
ps = read_participants_Basic(user_list = ul,pids = uids, log_time_offsets = alogoffset, datadir=params.EYELOGDATAFOLDER, 
                           prune_length = None, aoifile = "./sampledata/general.aoi",
                           require_valid_segs = False, auto_partition_low_quality_segments = True)
print
######

#explore_validation_threshold_segments(ps, auto_partition_low_quality_segments = False)
output_Validity_info_Segments(ps, auto_partition_low_quality_segments_flag = False, validity_method = 3)
output_percent_discarded(ps,'disc.csv')
output_Validity_info_Segments(ps, auto_partition_low_quality_segments_flag = False, validity_method = 2, threshold_gaps_list = [100, 200, 300])
output_Validity_info_Participants(ps, include_restored_samples =True, auto_partition_low_quality_segments_flag = False)


##### WRITE features to file
#write_features_tsv(ps, './outputfolder/smaple_features.tsv',featurelist = params.featurelist, aoifeaturelabels=params.aoifeaturelist, id_prefix = False)
