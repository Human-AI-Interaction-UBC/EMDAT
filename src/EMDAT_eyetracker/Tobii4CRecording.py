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
            reader = csv.DictReader(f, delimiter=";")
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
            reader = csv.DictReader(f, delimiter=',')
            for row in reader:
                if row["label"] != "fixation": #if not a fixation or the current fixation
                    continue
                data = {"fixationindex": currentfix,
                        "timestamp": EMDAT_core.utils.cast_int(EMDAT_core.utils.cast_float(row["start"])),
                        "fixationduration": EMDAT_core.utils.cast_int(EMDAT_core.utils.cast_float(row["duration"])),
                        "fixationpointx": EMDAT_core.utils.cast_float(row["x"]),
                        "fixationpointy": EMDAT_core.utils.cast_float(row["y"])}
                all_fixation.append(Fixation(data, self.media_offset))
                currentfix += 1

        return all_fixation

    def read_saccade_data(self, saccade_file, all_file):
        """Returns a list of "Saccade"s read from the data file file.

        Args:
            saccade_file: A string containing the name of the data file output by the Tobii software.

        Returns:
            a list of "Saccade"s
        """

        all_saccade = []
        with open(all_file, 'r') as all_data:
            all_reader = list(csv.DictReader(all_data, delimiter=';'))

            with open(saccade_file, 'r') as f:
                reader = list(csv.DictReader(f, delimiter=','))
                current_index = 0

                for row in reader:
                    if row["label"] == "saccade":
                        start = EMDAT_core.utils.cast_float(row["start"])
                        end = EMDAT_core.utils.cast_float(row["end"])
                        # search for start
                        saccade_vect = []
                        is_valid_sample = 0

                        # iterate through all_reader with loop
                        i = np.searchsorted(list(map(lambda all_data_row: EMDAT_core.utils.cast_float(all_data_row["system_time_stamp"]), all_reader)), start)
                        i_start = i
                        while EMDAT_core.utils.cast_float(all_reader[i]["system_time_stamp"]) <= end:
                            right_gaze = list(map(lambda point: EMDAT_core.utils.cast_float(point, -1),
                                                  all_reader[i]["right_gaze_point_on_display_area"].strip("()").split(",")))
                            left_gaze = list(map(lambda point: EMDAT_core.utils.cast_float(point, -1),
                                                 all_reader[i]["left_gaze_point_on_display_area"].strip("()").split(",")))
                            gaze_point_x = EMDAT_core.utils.cast_float((left_gaze[0] + right_gaze[0])/2, -1)
                            gaze_point_y = EMDAT_core.utils.cast_float((left_gaze[1] + right_gaze[1])/2, -1)
                            saccade_vect.append([EMDAT_core.utils.cast_float(all_reader[i]["system_time_stamp"]),
                                                 gaze_point_x, gaze_point_y])

                            if EMDAT_core.utils.cast_int(all_reader[i]["right_gaze_origin_validity"]) == 1 or \
                                    EMDAT_core.utils.cast_int(all_reader[i]["left_gaze_origin_validity"]) == 1:
                                is_valid_sample += 1
                            i += 1

                        rate_valid_sample = is_valid_sample/(i - i_start)
                        saccade_duration = EMDAT_core.utils.cast_int(EMDAT_core.utils.cast_float(row["duration"]))
                        dist = EMDAT_core.Recording.get_saccade_distance(saccade_vect)
                        accel = -1#Recording.get_saccade_acceleration(saccade_vect)
                        speed = float(dist) / EMDAT_core.utils.cast_int(saccade_duration)
                        data = {"saccadeindex": EMDAT_core.utils.cast_int(current_index),
                                "timestamp": start,
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
                        current_index += 1

        return all_saccade


# for testing purposes:
if __name__ == "__main__":

    raw_file = "sampledata/4Ctest.csv"
    fixation_file = "sampledata/4Ctest_fixation.csv"

    tobii = Tobii4CRecording(raw_file, fixation_file)
    alldata = tobii.read_all_data(raw_file)
    print("all_data: ")
    print([data.get_string(",") for data in alldata])
    fixations = tobii.read_fixation_data(fixation_file)
    print("fixation_data: ")
    print([data.get_string(",") for data in fixations])
    saccades = tobii.read_saccade_data(fixation_file, raw_file)
    print("saccade_data: ")
    print([data.get_string(",") for data in saccades])

