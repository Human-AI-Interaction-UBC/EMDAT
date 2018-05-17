"""
UBC Eye Movement Data Analysis Toolkit (EMDAT), Version 3
Created on 2015-08-15

Class to read SMI data (exported with BeGaze). See sample data in the "sampledata" folder.

Authors: Sebastien Lalle (creator), Mike Wu.
Institution: The University of British Columbia.
"""

from EMDAT_core.Recording import Recording
from EMDAT_core.data_structures import Datapoint, Fixation, Saccade, Event
import EMDAT_core.utils
import csv
import params


class SMIRecording(Recording):
    def read_all_data(self, all_file):
        all_data = []
        with open(all_file, 'r') as f:
            for i in xrange(params.RAW_HEADER_LINE):
                if i is (params.RAW_HEADER_LINE - 1):  # read the row of the table header for fixations
                    data_header = next(f).strip().split(',')
                else:
                    next(f)

            reader = csv.DictReader(f, fieldnames=data_header)
            last_pupil_left = -1
            last_pupil_right = -1
            last_time = -1

            for row in reader:
                if row["L Event Info"] != "Fixation":  # ignore data points other than fixations (gaze points)
                    continue
                pupil_left = EMDAT_core.utils.cast_float(row["L Pupil Diameter [mm]"])
                pupil_right = EMDAT_core.utils.cast_float(row["R Pupil Diameter [mm]"])
                distance_left = EMDAT_core.utils.cast_float(row["L EPOS Z"], -1)
                distance_right = EMDAT_core.utils.cast_float(row["R EPOS Z"], -1)
                timestamp = EMDAT_core.utils.cast_int(row["Time"])
                data = {"timestamp": timestamp,
                        "pupilsize": EMDAT_core.Recording.get_pupil_size(pupil_left, pupil_right),
                        "pupilvelocity": EMDAT_core.Recording.get_pupil_velocity(last_pupil_left, last_pupil_right, pupil_left, pupil_right, (timestamp-last_time) ),
                        "distance": EMDAT_core.Recording.get_distance(distance_left, distance_right),
                        "is_valid": (EMDAT_core.utils.cast_float(row["L POR X [px]"], -1) > 0 and EMDAT_core.utils.cast_float(row["L POR Y [px]"], -1) > 0 )
                                              or (EMDAT_core.utils.cast_float(row["R POR X [px]"], -1) > 0 and EMDAT_core.utils.cast_float(row["R POR Y [px]"], -1) > 0),
                        "stimuliname": "Screen",  # temporarily set to the same stimuli
                        "is_valid_blink": not ("Blink" in row['L Event Info'] or "Blink" in row['R Event Info']),
                        "fixationindex": EMDAT_core.utils.cast_int(row["Time"]),
                        "gazepointxleft": EMDAT_core.utils.cast_float(row["L POR X [px]"]),
                        "gazepointxlright": EMDAT_core.utils.cast_float(row["R POR X [px]"])}
                all_data.append(Datapoint(data))
                last_pupil_left = pupil_left
                last_pupil_right = pupil_right
                last_time = timestamp

        return all_data

    def read_fixation_data(self, fixation_file):
        all_fixation = []
        with open(fixation_file, 'r') as f:
            for i in xrange(params.EVENTS_FIRST_DATA_LINE - 1):
                if i is (params.FIXATION_HEADER_LINE - 1):  # read the row of the table header for fixations
                    fixation_headers = next(f).strip().split(',')
                else:
                    next(f)
            reader = csv.DictReader(f, fieldnames=fixation_headers)
            for row in reader:
                if not row["Event Type"].startswith("Fixation "+params.MONOCULAR_EYE):
                    continue
                data = {"fixationindex": EMDAT_core.utils.cast_int(row["Number"]),
                        "timestamp": EMDAT_core.utils.cast_int(row["Start"]),
                        "fixationduration": EMDAT_core.utils.cast_int(row["Duration"]),
                        "fixationpointx": EMDAT_core.utils.cast_float(row["Location X"]),
                        "fixationpointy": EMDAT_core.utils.cast_float(row["Location Y"])}
                all_fixation.append(Fixation(data, self.media_offset))

        return all_fixation

    def read_saccade_data(self, saccade_file):
        all_saccades = []
        with open(saccade_file, 'r') as f:
            for i in xrange(params.EVENTS_FIRST_DATA_LINE - 1):
                if i is (params.SACCADE_HEADER_LINE - 1):  # read the row of the table header for saccades
                    saccade_headers = next(f).strip().split(',')
                else:
                    next(f)
            reader = csv.DictReader(f, fieldnames=saccade_headers)
            for row in reader:
                if not row["Event Type"].startswith("Saccade "+params.MONOCULAR_EYE):
                    continue
                data = {"saccadeindex": EMDAT_core.utils.cast_int(row["Number"]),
                        "timestamp": EMDAT_core.utils.cast_int(row["Start"]),
                        "saccadeduration": EMDAT_core.utils.cast_int(row["Duration"]),
                        "saccadestartpointx": EMDAT_core.utils.cast_float(row["Start Loc.X"]),
                        "saccadestartpointy": EMDAT_core.utils.cast_float(row["Start Loc.Y"]),
                        "saccadeendpointx": EMDAT_core.utils.cast_float(row["End Loc.X"]),
                        "saccadeendpointy": EMDAT_core.utils.cast_float(row["End Loc.Y"]),
                        "saccadedistance": EMDAT_core.utils.cast_float(row["Average Speed"])*EMDAT_core.utils.cast_float(row["Duration"]),
                        "saccadespeed": EMDAT_core.utils.cast_float(row["Average Speed"]),
                        "saccadeacceleration": EMDAT_core.utils.cast_float(row["Average Accel."])
                        }
                all_saccades.append(Saccade(data, self.media_offset))

        return all_saccades

    def read_event_data(self, event_file):
        all_event = []
        with open(event_file, 'r') as f:
            for i in xrange(params.EVENTS_FIRST_DATA_LINE - 1):
                if i is (params.USER_EVENT_HEADER_LINE - 1):  # read the row of the table header for user events
                    event_headers = next(f).strip().split(',')
                else:
                    next(f)
            reader = csv.DictReader(f, fieldnames=event_headers)
            for row in reader:
                if row["Event Type"] != "UserEvent":
                    continue
                data = {"timestamp": EMDAT_core.utils.cast_int(row["Start"]),
                        "description": row["Description"]}
                descriptions = row["Description"].split(" ")
                event_type = descriptions[2]
                if event_type == "UE-mouseclick":
                    if descriptions[3] == "left":
                        data.update({"event": "LeftMouseClick"})
                    else:
                        data.update({"event": "RightMouseClick"})
                    data.update({"x_coord": EMDAT_core.utils.cast_int(descriptions[4].split("=")[1]),
                                 "y_coord": EMDAT_core.utils.cast_int(descriptions[5].split("=")[1])})
                elif event_type == "UE-keypress":
                    data.update({"event": "KeyPress", "key_name": descriptions[3]})
                all_event.append(Event(data, self.media_offset))

        return all_event
