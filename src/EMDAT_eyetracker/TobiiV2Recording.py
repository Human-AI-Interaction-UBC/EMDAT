"""
UBC Eye Movement Data Analysis Toolkit (EMDAT), Version 3
Created on 2015-08-15

Class to read Tobii data (exported with Tobii Studio version 1x and 2x). See sample data in the "sampledata" folder.

Authors: Mike Wu (creator), Sebastien Lalle.
Institution: The University of British Columbia.
"""

from EMDAT_core.Recording import *
from EMDAT_core.data_structures import Datapoint, Fixation, Saccade, Event
from EMDAT_core.utils import *
import csv
import params


class TobiiV2Recording(Recording):
    def read_all_data(self, all_file):
        """Returns a list of "Datapoint"s read from an "All-Data" file.

        Args:
            all_file:A string containing the name of the 'All-Data.tsv' file output by the Tobii software.

        Returns:
            a list of "Datapoint"s
        """
        all_data = []
        with open(all_file, 'r') as f:
            for _ in xrange(params.ALLDATAHEADERLINES + params.NUMBEROFEXTRAHEADERLINES - 1):
                next(f)
            reader = csv.DictReader(f, delimiter="\t")
            last_pupil_left = -1
            last_pupil_right = -1
            last_time = -1

            for row in reader:
                if not row["Number"]:  # ignore invalid data point
                    continue
                pupil_left = cast_float(row["PupilLeft"], -1)
                pupil_right = cast_float(row["PupilRight"], -1)
                distance_left = cast_float(row["DistanceLeft"], -1)
                distance_right = cast_float(row["DistanceRight"], -1)
                timestamp = cast_int(row["Timestamp"])
                data = {"timestamp": timestamp,
                        "pupilsize": get_pupil_size(pupil_left, pupil_right),
                        "pupilvelocity": get_pupil_velocity(last_pupil_left, last_pupil_right, pupil_left, pupil_right, (timestamp-last_time) ),
                        "distance": get_distance(distance_left, distance_right),
                        "is_valid": cast_int(row["ValidityRight"]) < 2 or cast_int(row["ValidityLeft"]) < 2,
                        "is_valid_blink": cast_int(row["ValidityRight"]) < 2 and cast_int(row["ValidityLeft"]) < 2,
                        "stimuliname": row["StimuliName"],
                        "fixationindex": cast_int(row["FixationIndex"]),
                        "gazepointxleft": cast_float(row["GazePointXLeft"])}
                all_data.append(Datapoint(data))
                last_pupil_left = pupil_left
                last_pupil_right = pupil_right
                last_time = timestamp

        return all_data

    def read_fixation_data(self, fixation_file):
        """Returns a list of "Fixation"s read from an "Fixation-Data" file.

        Args:
            fixation_file: A string containing the name of the 'Fixation-Data.tsv' file output by the Tobii software.

        Returns:
            a list of "Fixation"s
        """

        all_fixation = []
        with open(fixation_file, 'r') as f:
            for _ in xrange(params.FIXATIONHEADERLINES - 1):
                next(f)
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                data = {"fixationindex": cast_int(row["FixationIndex"]),
                        "timestamp": cast_int(row["Timestamp"]),
                        "fixationduration": cast_int(row["FixationDuration"]),
                        "fixationpointx": cast_int(row["MappedFixationPointX"]),
                        "fixationpointy": cast_int(row["MappedFixationPointY"])}
                all_fixation.append(Fixation(data, self.media_offset))

        return all_fixation

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
                data = {"timestamp": cast_int(row["Timestamp"]),
                        "event": row["Event"],
                        "event_key": cast_int(row["EventKey"])}
                if data["event"] == "LeftMouseClick" or data["event"] == "RightMouseClick":
                    data.update({"x_coord": cast_int(row["Data1"]), "y_coord": cast_int(row["Data2"])})
                elif data["event"] == "KeyPress":
                    data.update({"key_code": cast_int(row["Data1"]), "key_name": row["Descriptor"]})
                elif data["event"] == "LogData":
                    data.update({"description": row["Data1"]})
                all_event.append(Event(data, self.media_offset))

        return all_event

    def read_saccade_data(self, saccade_file):
        """ no saccade in data exported from Tobii Studio V1-V2
        """
        pass
