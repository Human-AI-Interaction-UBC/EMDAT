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

if __name__ == '__main__':
    freeze_support() #for windows
    #ul = ['msnv56']    # list of user recordings (files extracted for one participant from Tobii studio)
    #ul = ["msnv10", "msnv12", "msnv13", "msnv14", "msnv15", "msnv17", "msnv18", "msnv2", "msnv20", "msnv21", "msnv22", "msnv24", "msnv25", "msnv29", "msnv30", "msnv34", "msnv35", "msnv37", "msnv38", "msnv39", "msnv4", "msnv41", "msnv42", "msnv43", "msnv44", "msnv46", "msnv49", "msnv5", "msnv50", "msnv51", "msnv54", "msnv56", "msnv6", "msnv60", "msnv63", "msnv66", "msnv68", "msnv69", "msnv71", "msnv73", "msnv75", "msnv77", "msnv78", "msnv81", "msnv85", "msnv9"]
    
    ul = [1,9,12,16,18,19,21,25,26,30,36,38,40,42,45,46,50,52,55,58,59,60,61,62,63,64,65,66,67,68,69,70,71,73,74,75,76,77,78,80,81,82,84,85,88,89,90,91,92,95,97,31]
    ul = map(str, ul)
    #ul = ['85']

    uids =      ul    # User ID that is used in the external logs (can be different from above but there should be a 1-1 mapping)

    alogoffset = ul    # the time sifference between the eye tracker logs and the external log

    
    ###### Read participants
    nbprocess = cpu_count()
    ps = read_participants_Basic_multiprocessing(nbprocess, user_list = ul,pids = uids, log_time_offsets = alogoffset, datadir=params.EYELOGDATAFOLDER, 
                               prune_length = None, 
    #                           aoifile = "./sampledata/general.aoi",
    #                           aoifile = "./sampledata/Dynamic_1.aoi",
                               require_valid_segs = False, auto_partition_low_quality_segments = False)
#                               rpsfile = "./sampledata/all_rest_pupil_sizes.tsv")
    
    ######

    if params.DEBUG or params.VERBOSE == "VERBOSE":
        #explore_validation_threshold_segments(ps, auto_partition_low_quality_segments = False)
        output_Validity_info_Segments(ps, auto_partition_low_quality_segments_flag = False, validity_method = 3)
        output_percent_discarded(ps,'./outputfolder/disc_multiprocessing.csv')
        output_Validity_info_Segments(ps, auto_partition_low_quality_segments_flag = False, validity_method = 2, threshold_gaps_list = [100, 200, 250, 300],output_file = "./outputfolder/Seg_val_multiprocessing.csv")
        output_Validity_info_Participants(ps, include_restored_samples =True, auto_partition_low_quality_segments_flag = False)


    # WRITE features to file
    '''
    if params.VERBOSE != "QUIET":
        print
        print "Exporting:\n--General:", params.featurelist
    write_features_tsv(ps, '../outputfolder/test_intervention.tsv', featurelist=params.featurelist, id_prefix=False)
    '''
    ##### WRITE AOI sequences and AOI features to file
    write_features_tsv(ps, '../outputfolder/control_txt_viz_features.tsv',featurelist = params.aoisequencefeat, aoifeaturelist=params.aoigeneralfeat, id_prefix = False)
    #write_features_tsv(ps, '../outputfolder/control_txt_viz_features.tsv',featurelist = params.aoisequencefeat, aoifeaturelist=params.aoigeneralfeat, id_prefix = False)


    #### Export pupil dilations for each scene to a separate file
    #print "--pupil dilation trends" 
    #plot_pupil_dilation_all(ps, './outputfolder/pupilsizes/', "problem1")
    #plot_pupil_dilation_all(ps, './outputfolder/pupilsizes/', "problem2")
