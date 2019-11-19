"""
UBC Eye Movement Data Analysis Toolkit (EMDAT), Version 3
Created on 2019

Class to read Tobii data (exported with Tobii 4C and higher). See sample data in the Tobii 4C folder

Authors: Tiffany , Martijn Millecamp
Institution: The University of British Columbia.
"""

from EMDAT_core.Recording import Recording
from EMDAT_core.data_structures import Datapoint, Fixation, Saccade, Event
import EMDAT_core.utils
import csv
import params
import numpy as np


class Tobii4CRecording(Recording):
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
            currentfix = 0
            for row in reader:
                if not row["left_gaze_origin_validity"] or not row["right_gaze_origin_validity"]: #ignore data point with no validity information
                    continue
                right_gaze = list(map(lambda point: EMDAT_core.utils.cast_float(point, -1),
                                      row["right_gaze_point_on_display_area"].strip("()").split(",")))
                left_gaze = list(map(lambda point: EMDAT_core.utils.cast_float(point, -1),
                                     row["left_gaze_point_on_display_area"].strip("()").split(",")))
                gaze_point_x = EMDAT_core.utils.cast_float((left_gaze[0] + right_gaze[0])/2, -1)
                gaze_point_y = EMDAT_core.utils.cast_float((left_gaze[1] + right_gaze[1])/2, -1)
                pupil_left = EMDAT_core.utils.cast_float(row["left_pupil_diameter"], -1)
                pupil_right = EMDAT_core.utils.cast_float(row["right_pupil_diameter"], -1)
                timestamp = EMDAT_core.utils.cast_int(EMDAT_core.utils.cast_float(row["system_time_stamp"]))
                data = {"timestamp": timestamp,
                        "pupilsize": EMDAT_core.Recording.get_pupil_size(pupil_left, pupil_right),
                        "pupilvelocity": EMDAT_core.Recording.get_pupil_velocity(last_pupil_left, last_pupil_right, pupil_left, pupil_right, (timestamp-last_time) ),
                        "distance": -1,
                        "is_valid": EMDAT_core.utils.cast_int(row["right_gaze_origin_validity"]) == 1 or EMDAT_core.utils.cast_int(row["left_gaze_origin_validity"]) == 1,
                        "is_valid_blink": EMDAT_core.utils.cast_int(row["right_gaze_origin_validity"]) == 1 and EMDAT_core.utils.cast_int(row["left_gaze_origin_validity"]) == 1,
                        "fixationindex": currentfix,
                        "gazepointx": gaze_point_x,
                        "gazepointy": gaze_point_y}
                all_data.append(Datapoint(data))
                last_pupil_left = pupil_left
                last_pupil_right = pupil_right
                last_time = timestamp
                currentfix += 1

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
                if row['label'] != "fixation": #if not a fixation or the current fixation
                    continue
                data = {"fixationindex": currentfix,
                        "timestamp": EMDAT_core.utils.cast_int(EMDAT_core.utils.cast_float(row["start"])),
                        "fixationduration": EMDAT_core.utils.cast_int(EMDAT_core.utils.cast_float(row["duration"])),
                        "fixationpointx": EMDAT_core.utils.cast_float(row["x"]),
                        "fixationpointy": EMDAT_core.utils.cast_float(row["y"])}
                all_fixation.append(Fixation(data, self.media_offset))
                currentfix += 1

        return all_fixation

    def read_saccade_data(self, saccade_file):
        """Returns a list of "Saccade"s read from the data file file.

        Args:
            saccade_file: A string containing the name of the data file output by the Tobii software.

        Returns:
            a list of "Saccade"s
        """

        all_saccades = []
        with open(saccade_file, 'r') as f:
            currentfix = 0
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                if row["label"] != "saccade":  # if not a fixation or the current fixation
                    continue
                data = {"fixationindex": currentfix,
                        "timestamp": EMDAT_core.utils.cast_int(EMDAT_core.utils.cast_float(row["start"])),
                        "fixationduration": EMDAT_core.utils.cast_int(EMDAT_core.utils.cast_float(row["duration"])),
                        "fixationpointx": EMDAT_core.utils.cast_float(row["x"]),
                        "fixationpointy": EMDAT_core.utils.cast_float(row["y"])}
                all_saccades.append(Fixation(data, self.media_offset))
                currentfix += 1

        return all_saccades

    def read_event_data(self, event_file):
        """Returns a list of "Event"s read from an "Event-Data" file.

        Args:
            event_file: A string containing the name of the 'Event-Data.tsv' file output by the Tobii software.

        Returns:
            a list of "Event"s
        """

        all_event = []
        with open(event_file, 'r') as f:
            for _ in xrange(params.EVENTSHEADERLINES - 1):
                next(f)
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                data = {"timestamp": int(row["Timestamp"]),
                        "event": row["Event"],
                        "event_key": int(row["EventKey"])}
                if data["event"] == "LeftMouseClick" or data["event"] == "RightMouseClick":
                    data.update({"x_coord": int(row["Data1"]), "y_coord": int(row["Data2"])})
                elif data["event"] == "KeyPress":
                    data.update({"key_code": int(row["Data1"]), "key_name": row["Descriptor"]})
                elif data["event"] == "LogData":
                    data.update({"description": row["Data1"]})
                all_event.append(Event(data, self.media_offset))

        return all_event


if __name__ == "__main__":
    tobii = Tobii4CRecording("../sampledata/Tobii4C/P123456_Data_Export.tsv",
                             "../sampledata/Tobii4C/P123456_Data_Fixations.tsv",
                             "../sampledata/Tobii4C/P123456_Data_Fixations.tsv",
                             None)
    tobii.read_all_data("../sampledata/Tobii4C/P123456_Data_Export.tsv")
    tobii.read_fixation_data("../sampledata/Tobii4C/P123456_Data_Fixations.tsv")
    tobii.read_saccade_data("../sampledata/Tobii4C/P123456_Data_Fixations.tsv")

