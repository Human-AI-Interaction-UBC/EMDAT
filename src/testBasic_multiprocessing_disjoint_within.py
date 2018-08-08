"""
UBC Eye Movement Data Analysis Toolkit (EMDAT), Version 3
Created on 2012-08-23

Sample code to run EMDAT for a given experiment (multiprocessing version).

@author: Sebastien Lalle (creator), Samad Kardan
Institution: The University of British Columbia.
"""


from multiprocessing import freeze_support, cpu_count
from BasicParticipant_multiprocessing import *
from EMDAT_core.Participant import export_features_all, write_features_tsv
from EMDAT_core.ValidityProcessing import output_Validity_info_Segments, output_percent_discarded, output_Validity_info_Participants

import os
time_windows = [1000, 2000, 5000, 10000]


if __name__ == '__main__':
    freeze_support() #for windows

    ul =        [ 1, 9, 12, 16, 18, 19, 21, 25, 26, 30,  31,  36, 38, 40, 42, 45, 46, 50,
                52, 55, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70,
                71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 84, 85, 88, 89,  90,91, 92,
                93, 95, 97 ]    # list of user recordings (files extracted for one participant from Tobii studio)
    uids =      ul    # User ID that is used in the external logs (can be different from above but there should be a 1-1 mapping)

    alogoffset = ul    # the time difference between the eye tracker logs and the external log


            ###### Read participants
    nbprocess = cpu_count()
    ps = read_participants_Basic_multiprocessing(nbprocess, user_list = ul,pids = uids, log_time_offsets = alogoffset, datadir = params.EYELOGDATAFOLDER,
                #                           aoifile = "./sampledata/general.aoi",
                #                           aoifile = "./sampledata/Dynamic_1.aoi",
                                   require_valid_segs = False, auto_partition_low_quality_segments = False, disjoint_window = True, time_windows = time_windows)
            #                               rpsfile = "./sampledata/all_rest_pupil_sizes.tsv")
            ######

    if params.DEBUG or params.VERBOSE == "VERBOSE":
                #explore_validation_threshold_segments(ps, auto_partition_low_quality_segments = False)
                #output_Validity_info_Segments(ps, auto_partition_low_quality_segments_flag = False, validity_method = 3)
                #output_percent_discarded(ps,'./outputfolder/disc_multiprocessing.csv')
                #output_Validity_info_Segments(ps, auto_partition_low_quality_segments_flag = False, validity_method = 2, threshold_gaps_list = [100, 200, 250, 300],output_file = "./outputfolder/Seg_val_multiprocessing.csv")
                #output_Validity_info_Participants(ps, include_restored_samples =True, auto_partition_low_quality_segments_flag = False)
        pass

            # WRITE features to file

            ##### WRITE AOI sequences to file
#    aoi_feat_names = (map(lambda x:x, params.aoigeneralfeat))
#    write_features_tsv(ps, './outputfolder/sequences_multiprocessing_nov15.tsv',featurelist = params.aoisequencefeat, aoifeaturelist=aoi_feat_names, id_prefix = False, require_valid = False)

            #### Export pupil dilations for each scene to a separate file
            #print "--pupil dilation trends"
            #plot_pupil_dilation_all(ps, './outputfolder/pupilsizes/', "problem1")
            #plot_pupil_dilation_all(ps, './outputfolder/pupilsizes/', "problem2")
