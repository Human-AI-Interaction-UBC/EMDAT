"""
UBC Eye Movement Data Analysis Toolkit (EMDAT), Version 3
Created on 2012-08-23

Sample code to run EMDAT for a given experiment (multiprocessing version).

@author: Sebastien Lalle (creator), Samad Kardan
Institution: The University of British Columbia.
"""
import sys
sys.path.append('.')
sys.path.append('./EMDAT_core')
from multiprocessing import freeze_support, cpu_count
from BasicParticipant_multiprocessing import *
from EMDAT_core.Participant import export_features_all, write_features_tsv
from EMDAT_core.ValidityProcessing import output_Validity_info_Segments, output_percent_discarded, output_Validity_info_Participants

if __name__ == '__main__':
    freeze_support() #for windows
    ul =        [61, 62]    # list of user recordings (files extracted for one participant from Tobii studio)
    uids =      [61, 62]    # User ID that is used in the external logs (can be different from above but there should be a 1-1 mapping)

    alogoffset = [0, 0]    # the time sifference between the eye tracker logs and the external log

    ####### Testing error handling
    #ul =        [61, 62, 63]    # list of user recordings (files extracted for one participant from Tobii studio)
    #uids =      [61, 62, 63]    # User ID that is used in the external logs (can be different from above but there should be a 1-1 mapping)
    #
    #alogoffset =[ 3,  2, 2]    # the time sifference between the eye tracker logs and the external log

    ###### Read participants
    nbprocess = cpu_count()
    ps = read_participants_Basic_multiprocessing(nbprocess, user_list = ul,pids = uids, log_time_offsets = alogoffset, datadir=params.EYELOGDATAFOLDER, 
                               prune_length = None, 
                               aoifile = "./sampledata/AOIs/general.aoi",
    #                           aoifile = "./sampledata/AOIs/Dynamic_1.aoi",
                               require_valid_segs = False, auto_partition_low_quality_segments = True,
                               rpsfile = "./sampledata/all_rest_pupil_sizes.tsv")
    print
    ######

    if params.DEBUG or params.VERBOSE == "VERBOSE":
        #explore_validation_threshold_segments(ps, auto_partition_low_quality_segments = False)
        output_Validity_info_Segments(ps, auto_partition_low_quality_segments_flag = False, validity_method = 3)
        output_percent_discarded(ps,'./outputfolder/disc_multiprocessing.csv')
        output_Validity_info_Segments(ps, auto_partition_low_quality_segments_flag = False, validity_method = 2, threshold_gaps_list = [100, 200, 250, 300],output_file = "./outputfolder/Seg_val_multiprocessing.csv")
        output_Validity_info_Participants(ps, include_restored_samples =True, auto_partition_low_quality_segments_flag = False)


    ##### WRITE features to file
    print
    aoi_feat_names = (map(lambda x:x, params.aoigeneralfeat))
    print "Exporting features:\n--General:", params.featurelist, "\n--AOI:", aoi_feat_names, "\n--Sequences:", params.aoisequencefeat
    write_features_tsv(ps, './outputfolder/sample_features_multiprocessing.tsv',featurelist = params.featurelist, aoifeaturelist=aoi_feat_names, id_prefix = False)

    ##### WRITE AOI sequences to file
    write_features_tsv(ps, './outputfolder/sample_sequences_multiprocessing.tsv',featurelist = params.aoisequencefeat, aoifeaturelist=aoi_feat_names, id_prefix = False)

    #### Export pupil dilations for each scene to a separate file
    #print "--pupil dilation trends" 
    #plot_pupil_dilation_all(ps, './outputfolder/pupilsizes/', "problem1")
    #plot_pupil_dilation_all(ps, './outputfolder/pupilsizes/', "problem2")
