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

ul = []
for i in range(101, 143):
    ul.append(str(i) + "a")
    ul.append(str(i) + "b")
for i in range(144, 163):
    ul.append(str(i) + "a")
    ul.append(str(i) + "b")
uids = ul
alogoffset = [0]*len(ul)

#aoifile_name = "single_aoi.aoi"
#aoifile_name = "grid2x2.aoi"
aoifile_name = "viz-specific.aoi"

# Read participants
ps = read_participants_Basic(user_list=ul, pids=uids, log_time_offsets=alogoffset, datadir=params.EYELOGDATAFOLDER, aoifile= aoifile_name,
                             prune_length=None, require_valid_segs=False, auto_partition_low_quality_segments=False)

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

# output internal data
# for participant in ps:
#     dir = "C:/git00/EMDAT_testing/Part2_EMDATInternal_EMDATOutput/new_data/"
#     fall = open(dir + "EMDATinternaldata_gazesamples_" + str(participant.pid) + ".csv", "w")
#     fall.write(
#         "scene,timestamp,rawpupilsize,pupilvelocity,headdistance,is_valid_pupil,is_valid_headdistance,stimuliname\n")
#     ffix = open(dir + "EMDATinternaldata_fixations_" + str(participant.pid) + ".csv", "w")
#     ffix.write("scene,fixationindex,timestamp,fixationduration,mappedfixationpointx,mappedfixationpointy\n")
#     fsac = open(dir + "EMDATinternaldata_saccades_" + str(participant.pid) + ".csv", "w")
#     fsac.write(
#         "scene,saccadeindex,timestamp,saccadeduration,saccadedistance,saccadespeed,saccadeacceleration,saccadestartpointx,saccadestartpointy,saccadeendpointx,saccadeendpointy,saccadequality\n")
#     feve = open(dir + "EMDATinternaldata_events_" + str(participant.pid) + ".csv", "w")
#     feve.write("scene,timestamp,event,event_key,x_coord,y_coord,key_code,key_name,description\n")
#
#     for sc in participant.scenes:
#         for sg in sc.segments:
#             if sc.scid.find("allsc") > -1:
#                 continue
#
#             # gaze samples (including pupil and head distance)
#             # for d in sg.all_data:
#             #     pupilval = d.is_valid and d.pupilsize > 0
#             #     headval = d.is_valid and d.distance > 0
#             #     fall.write(str(sc.scid) + "," + str(d.timestamp) + "," + str(d.pupilsize) + "," + str(
#             #         d.pupilvelocity) + "," + str(d.distance) + "," + str(pupilval) + "," + str(headval) + "," + str(
#             #         d.stimuliname) + "\n")
#             # gaze samples (including pupil and head distance)
#             for d in sg.all_data:
#                 pupilval = d.pupilsize > 0
#                 headval = d.distance > 0
#                 fall.write(str(sc.scid) + "," + str(d.timestamp) + "," + str(d.pupilsize) + "," + str(
#                     d.pupilvelocity) + "," + str(d.distance) + "," + str(pupilval) + "," + str(headval) + "," + str(
#                     d.stimuliname) + "\n")
#
#                 # fixations
#             for d in sg.fixation_data:
#                 ffix.write(str(sc.scid) + "," + str(d.fixationindex) + "," + str(d.timestamp) + "," + str(
#                     d.fixationduration) + "," + str(d.mappedfixationpointx) + "," + str(d.mappedfixationpointy) + "\n")
#
#                 # saccades
#             for d in sg.saccade_data:
#                 fsac.write(str(sc.scid) + "," + str(d.saccadeindex) + "," + str(d.timestamp) + "," + str(
#                     d.saccadeduration) + "," + str(d.saccadedistance) + "," + str(d.saccadespeed) + "," + str(
#                     d.saccadeacceleration)
#                            + "," + str(d.saccadestartpointx) + "," + str(d.saccadestartpointy) + "," + str(
#                     d.saccadeendpointx) + "," + str(d.saccadeendpointy) + "," + str(d.saccadequality) + "\n")
#
#                 # events
#             for d in sg.event_data:
#                 feve.write(
#                     str(sc.scid) + "," + str(d.timestamp) + "," + str(d.event) + "," + str(d.eventKey) + "," + str(
#                         d.x_coord) + "," + str(d.y_coord) + "," + str(d.key_code) + "," + str(d.key_name) + "," + str(
#                         d.description) + "\n")
#
#     fall.close()
#     ffix.close()
#     fsac.close()
#     feve.close()