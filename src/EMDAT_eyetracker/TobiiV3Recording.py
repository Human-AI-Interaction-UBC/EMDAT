"""
UBC Eye Movement Data Analysis Toolkit (EMDAT), Version 3
Created on 2015-08-15

Class to read Tobii data (exported with Tobii Studio V3 and higher). See sample data in the "sampledata" folder.

Authors: Mike Wu (creator), Sebastien Lalle. 
Institution: The University of British Columbia.
"""

from EMDAT_core.Recording import Recording
from EMDAT_core.data_structures import Datapoint, Fixation, Saccade, Event
import EMDAT_core.utils
import csv
import params


class TobiiV3Recording(Recording):
    def read_all_data(self, all_file):
        """Returns a list of "Datapoint"s read from an data file.

        Args:
            all_file:A string containing the name of the data file output by the Tobii software.

        Returns:
            a list of "Datapoint"s
        """
        all_data = []
        with open(all_file, 'r') as f:
            reader = csv.DictReader(f, delimiter="\t")
            last_pupil_left = -1
            last_pupil_right = -1
            last_time = -1
			
            for row in reader:
                if row["MediaName"] != 'ScreenRec':  # ignore non-recording data point
                    continue
                if not row["ValidityLeft"] or not row["ValidityRight"]: #ignore data point with no validity information
                    continue
                pupil_left = EMDAT_core.utils.cast_float(row["PupilLeft"], -1)
                pupil_right = EMDAT_core.utils.cast_float(row["PupilRight"], -1)
                distance_left = EMDAT_core.utils.cast_float(row["DistanceLeft"], -1)
                distance_right = EMDAT_core.utils.cast_float(row["DistanceRight"], -1)
                timestamp = EMDAT_core.utils.cast_int(row["RecordingTimestamp"])
                data = {"timestamp": timestamp,
                        "pupilsize": EMDAT_core.Recording.get_pupil_size(pupil_left, pupil_right),
                        "pupilvelocity": EMDAT_core.Recording.get_pupil_velocity(last_pupil_left, last_pupil_right, pupil_left, pupil_right, (timestamp-last_time) ),
                        "distance": EMDAT_core.Recording.get_distance(distance_left, distance_right),
                        "is_valid": EMDAT_core.utils.cast_int(row["ValidityRight"]) < 2 or EMDAT_core.utils.cast_int(row["ValidityLeft"]) < 2,
                        "stimuliname": row["MediaName"],
                        "fixationindex": EMDAT_core.utils.cast_int(row["FixationIndex"]),
                        "gazepointxleft": EMDAT_core.utils.cast_float(row["GazePointLeftX (ADCSpx)"])}
                all_data.append(Datapoint(data))
                last_pupil_left = pupil_left
                last_pupil_right = pupil_right
                last_time = timestamp

        return all_data

    def read_fixation_data(self, fixation_file):
        """Returns a list of "Fixation"s read from the data file file.

        Args:
            fixation_file: A string containing the name of the data file output by the Tobii software.

        Returns:
            a list of "Fixation"s
        """

        all_fixation = []
        with open(fixation_file, 'r') as f:
            currentfix = 0
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                if row["MediaName"] != 'ScreenRec':  # ignore non-recording data point
                    continue
                if not row["ValidityLeft"] or not row["ValidityRight"] or not row["FixationPointX (MCSpx)"] or not row["FixationPointY (MCSpx)"]: #ignore data point with no information
                    continue
                if row["GazeEventType"] != "Fixation" or currentfix == row["FixationIndex"]: #if not a fixation or the current fixation
                    continue
                data = {"fixationindex": EMDAT_core.utils.cast_int(row["FixationIndex"]),
                        "timestamp": EMDAT_core.utils.cast_int(row["RecordingTimestamp"]),
                        "fixationduration": EMDAT_core.utils.cast_int(row["GazeEventDuration"]),
                        "fixationpointx": EMDAT_core.utils.cast_int(row["FixationPointX (MCSpx)"]),
                        "fixationpointy": EMDAT_core.utils.cast_int(row["FixationPointY (MCSpx)"])}
                all_fixation.append(Fixation(data, self.media_offset))
                currentfix = row["FixationIndex"]

        return all_fixation
        
    def read_saccade_data(self, saccade_file):
        """Returns a list of "Saccade"s read from the data file file.

        Args:
            fixation_file: A string containing the name of the data file output by the Tobii software.

        Returns:
            a list of "Saccade"s
        """

        all_saccade = []
        with open(saccade_file, 'r') as f:
            reader = csv.DictReader(f, delimiter='\t')
            in_saccade = False
            in_fixation = False
            last_gaze_coord = (0, 0, 0) #timestamp X Y
            saccade_vect = []
            saccade_duration = 0
            current_index = 0
            
            nb_invalid_temp = 0
            nb_valid_sample = 0
            nb_sample = 0
            
            for row in reader:
                if row["MediaName"] != 'ScreenRec' or not row["RecordingTimestamp"]:  # ignore non-recording data point
                    continue
                    
                if in_fixation:
                    if row["GazeEventType"] == "Fixation":
                        nb_invalid_temp = 0
                    elif row["GazeEventType"] == "Saccade": #new saccade
                        in_fixation = False
                        in_saccade = True
                        current_index = row["SaccadeIndex"]
                        saccade_vect = [last_gaze_coord]
                        nb_valid_sample = 0
						
                        #add current sample
                        if (EMDAT_core.utils.cast_int(row["ValidityLeft"])<2 or EMDAT_core.utils.cast_int(row["ValidityRight"])<2) and row["GazePointX (ADCSpx)"] and row["GazePointY (ADCSpx)"]: #ignore data point with no valid data
                            saccade_vect.append( [EMDAT_core.utils.cast_int(row["RecordingTimestamp"]), EMDAT_core.utils.cast_int(row["GazePointX (ADCSpx)"]), EMDAT_core.utils.cast_int(row["GazePointY (ADCSpx)"])] )
                            nb_valid_sample += 1
                        
                        if last_valid:
                            nb_valid_sample += 1
                            
                        nb_sample = 2 + nb_invalid_temp #current gaze sample + last gaze sample of the previous fixation + eventually all unclasified gaze samples in between
                        nb_invalid_temp = 0
                    else: #unclassified gaze samples
                        nb_invalid_temp += 1
                        
                elif in_saccade:
                    if row["GazeEventType"] == "Fixation":
                        in_fixation = True
                        in_saccade = False

                        #end of last saccade
                        if (EMDAT_core.utils.cast_int(row["ValidityLeft"])<2 or EMDAT_core.utils.cast_int(row["ValidityRight"])<2) and row["GazePointX (ADCSpx)"] and row["GazePointY (ADCSpx)"]: #valid last datapoint
                            saccade_vect.append( [EMDAT_core.utils.cast_int(row["RecordingTimestamp"]), EMDAT_core.utils.cast_int(row["GazePointX (ADCSpx)"]), EMDAT_core.utils.cast_int(row["GazePointY (ADCSpx)"])] )
                            nb_valid_sample += 1
                        elif (row["FixationPointX (MCSpx)"] and row["FixationPointY (MCSpx)"]): #if gaze sample not valid, try to use fixation data instead
                            saccade_vect.append( [EMDAT_core.utils.cast_int(row["RecordingTimestamp"]), EMDAT_core.utils.cast_int(row["FixationPointX (MCSpx)"]), EMDAT_core.utils.cast_int(row["FixationPointY (MCSpx)"])] )
                            nb_valid_sample += 1
                        nb_sample += 1
                        
                        rate_valid_sample = float(nb_valid_sample) / nb_sample
                        if rate_valid_sample >= params.VALID_SAMPLES_PROP_SACCADE: #if saccade quality is above the threshold
                            saccade_duration = EMDAT_core.utils.cast_int(row["RecordingTimestamp"]) - saccade_vect[0][0]
                            dist = EMDAT_core.Recording.get_saccade_distance(saccade_vect)
                            accel = -1#Recording.get_saccade_acceleration(saccade_vect)
                            speed = float(dist) / EMDAT_core.utils.cast_int(saccade_duration)
                            data = {"saccadeindex": EMDAT_core.utils.cast_int(current_index),
                                    "timestamp": saccade_vect[0][0],
                                    "saccadeduration": EMDAT_core.utils.cast_int(saccade_duration),
                                    "saccadestartpointx": saccade_vect[0][1],
                                    "saccadestartpointy": saccade_vect[0][2], 
                                    "saccadeendpointx": saccade_vect[-1][1],
                                    "saccadeendpointy": saccade_vect[-1][2], 
                                    "saccadedistance": dist,
                                    "saccadespeed": speed,
                                    "saccadeacceleration": accel,
									"saccadequality": rate_valid_sample
                                    }
                            all_saccade.append(Saccade(data, self.media_offset))
                            nb_valid_sample = 0
                            nb_sample = 0
                        
                    elif row["GazeEventType"] == "Saccade":
                        if (EMDAT_core.utils.cast_int(row["ValidityLeft"])<2 or EMDAT_core.utils.cast_int(row["ValidityRight"])<2) and row["GazePointX (ADCSpx)"] and row["GazePointY (ADCSpx)"]: #ignore data point with no valid data
                            saccade_vect.append( [EMDAT_core.utils.cast_int(row["RecordingTimestamp"]), EMDAT_core.utils.cast_int(row["GazePointX (ADCSpx)"]), EMDAT_core.utils.cast_int(row["GazePointY (ADCSpx)"])] )
                            nb_valid_sample += 1
                        nb_sample += 1
                    else: #unclassified gaze samples
                        nb_sample += 1
                    nb_invalid_temp = 0
                    
                else: #wait for the first fixation
                    if row["GazeEventType"] == "Fixation":
						in_fixation = True
						
                if row["GazePointX (ADCSpx)"] and row["GazePointY (ADCSpx)"]: 
                    last_gaze_coord = (EMDAT_core.utils.cast_int(row["RecordingTimestamp"]), EMDAT_core.utils.cast_int(row["GazePointX (ADCSpx)"]), EMDAT_core.utils.cast_int(row["GazePointY (ADCSpx)"]))
                    last_valid = (EMDAT_core.utils.cast_int(row["ValidityLeft"])<2 or EMDAT_core.utils.cast_int(row["ValidityRight"])<2)
                elif row["GazeEventType"] == "Fixation" and row["FixationPointX (MCSpx)"] and row["FixationPointY (MCSpx)"]: #if last sample not valid, at least check if valid data about the fixation
                    last_gaze_coord = (EMDAT_core.utils.cast_int(row["RecordingTimestamp"]), EMDAT_core.utils.cast_int(row["FixationPointX (MCSpx)"]), EMDAT_core.utils.cast_int(row["FixationPointY (MCSpx)"]))
                    last_valid = True
                        
        return all_saccade

        
    def read_event_data(self, event_file):
        """Returns a list of "Event"s read from an data file.

        Args:
            event_file: A string containing the name of the data file output by the Tobii software.

        Returns:
            a list of "Event"s
        """

        all_event = []
        with open(event_file, 'r') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                if row["MediaName"] != 'ScreenRec':  # ignore non-recording data point
                    continue
                if row["MouseEventIndex"] : #mouse event
                    data = {"timestamp": EMDAT_core.utils.cast_int(row["RecordingTimestamp"]),
                        "event": row["MouseEvent"]+"MouseClick",
                        "x_coord": EMDAT_core.utils.cast_int(row["MouseEventX (MCSpx)"]),
                        "y_coord": EMDAT_core.utils.cast_int(row["MouseEventY (MCSpx)"])
                        }
                    all_event.append(Event(data, self.media_offset))
                elif row["KeyPressEventIndex"] : #keyboard event
                    data = {"timestamp": EMDAT_core.utils.cast_int(row["RecordingTimestamp"]),
                        "event": "KeyPress",
                        "key_name": row["KeyPressEvent"]
                        }
                    all_event.append(Event(data, self.media_offset))

        return all_event
