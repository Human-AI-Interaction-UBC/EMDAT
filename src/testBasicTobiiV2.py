"""
UBC Eye Movement Data Analysis Toolkit (EMDAT), Version 3
Created on 2012-08-23

Sample code to run EMDAT for a given experiment.

@author: Samad Kardan (creator), Sebastien Lalle
Institution: The University of British Columbia.
"""

from BasicParticipant import *
from EMDAT_core.Participant import export_features_all, write_features_tsv
from EMDAT_core.ValidityProcessing import output_Validity_info_Segments, output_percent_discarded, output_Validity_info_Participants

ul =        [61, 62]    # list of user recordings (files extracted for one participant from Tobii studio)
uids =      [61, 62]    # User ID that is used in the external logs (can be different from above but there should be a 1-1 mapping)

alogoffset = [0, 0]    # the time sifference between the eye tracker logs and the external log

####### Testing error handling
#ul =        [61, 62, 63]    # list of user recordings (files extracted for one participant from Tobii studio)
#uids =      [61, 62, 63]    # User ID that is used in the external logs (can be different from above but there should be a 1-1 mapping)
#
#alogoffset =[ 3,  2, 2]    # the time sifference between the eye tracker logs and the external log



###### Read participants
ps = read_participants_Basic(user_list = ul,pids = uids, log_time_offsets = alogoffset, datadir=params.EYELOGDATAFOLDER, 
                           prune_length = None, 
                           aoifile = "./sampledata/AOIs/general.aoi",
#                           aoifile = "./sampledata/AOIs/Dynamic_1.aoi",
                           require_valid_segs = False, auto_partition_low_quality_segments = True,
                           rpsfile = "./sampledata/all_rest_pupil_sizes.tsv")
print
######

if params.DEBUG or params.VERBOSE == "VERBOSE":
    output_Validity_info_Segments(ps, auto_partition_low_quality_segments_flag = False, validity_method = 3)
    output_percent_discarded(ps,'./outputfolder/disc.csv')
    output_Validity_info_Segments(ps, auto_partition_low_quality_segments_flag = False, validity_method = 2, threshold_gaps_list = [100, 200, 250, 300],output_file = "./outputfolder/Seg_val.csv")
    output_Validity_info_Participants(ps, include_restored_samples =True, auto_partition_low_quality_segments_flag = False)


##### WRITE features to file
aoi_feat_names = (map(lambda x:x, params.aoigeneralfeat))
if params.VERBOSE != "QUIET":
    print
    print "Exporting features:\n--General:", params.featurelist, "\n--AOI:", aoi_feat_names, "\n--Sequences:", params.aoisequencefeat
write_features_tsv(ps, './outputfolder/sample_features.tsv',featurelist = params.featurelist, aoifeaturelabels=params.aoifeaturelist, id_prefix = True)

##### WRITE AOI sequences to file
write_features_tsv(ps, './outputfolder/sample_sequences.tsv',featurelist = params.aoisequencefeat, aoifeaturelabels=params.aoifeaturelist, id_prefix = False)

#### Export pupil dilations for each scene to a separate file
#print "--pupil dilation trends" 
#plot_pupil_dilation_all(ps, './outputfolder/pupilsizes/', "problem1")
#plot_pupil_dilation_all(ps, './outputfolder/pupilsizes/', "problem2")
