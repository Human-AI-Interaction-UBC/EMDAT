'''
Created on 2012-08-23

@author: skardan
'''
from BasicParticipant import *
from Participant import export_features_all, write_features_tsv

ul =        [61, 62]    # list of user recordings (files extracted for one participant from Tobii studio)
uids =      [61, 62]    # User ID that is used in the external logs (can be different from above but there should be a 1-1 mapping)

alogoffset =[ 3,  2]    # the time sifference between the eye tracker logs and the external log

###### Read participants
ps = read_participants_Basic(user_list = ul,pids = uids, log_time_offsets = alogoffset, datadir=params.EYELOGDATAFOLDER, 
                           prune_length = None, aoifile = "./sampledata/general.aoi",
                           require_valid_segs = True, auto_partition_low_quality_segments = True)
print
######

##### WRITE features to file
write_features_tsv(ps, './outputfolder/smaple_features.tsv',featurelist = params.featurelist, aoifeaturelabels=params.aoifeaturelist, id_prefix = False)
