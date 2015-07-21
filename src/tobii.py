from Recording import Recording
from data_structures import Datapoint, Fixation, Event
import csv
import utils
import params


class TobiiRecording(Recording):
    @staticmethod
    def read_all_data(all_file):
        """Returns a list of "Datapoint"s read from an "All-Data" file.

        Args:
            all_file:A string containing the name of the 'All-Data.tsv' file output by the
                Tobii software.
        Returns:
            a list of "Datapoint"s
        """
        all_data = []
        with open(all_file, 'r') as f:
            for _ in xrange(params.ALLDATAHEADERLINES + params.NUMBEROFEXTRAHEADERLINES - 1):
                next(f)
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                if not row["Number"]:  # ignore invalid data point
                    continue
                pupil_left = utils.cast_float(row["PupilLeft"], -1)
                pupil_right = utils.cast_float(row["PupilRight"], -1)
                distance_left = utils.cast_float(row["DistanceLeft"], -1)
                distance_right = utils.cast_float(row["DistanceRight"], -1)
                data = {"timestamp": utils.cast_int(row["Timestamp"]),
                        "pupilsize": Recording.get_pupil_size(pupil_left, pupil_right),
                        "distance": Recording.get_distance(distance_left, distance_right),
                        "is_valid": utils.cast_int(row["ValidityRight"]) < 2 or utils.cast_int(row["ValidityLeft"]) < 2,
                        "stimuliname": row["StimuliName"],
                        "fixationindex": utils.cast_int(row["FixationIndex"]),
                        "gazepointxleft": utils.cast_float(row["GazePointXLeft"])}
                all_data.append(Datapoint(data))

        return all_data

    @staticmethod
    def read_fixation_data(fixation_file, media_offset=(0, 0)):
        """Returns a list of "Fixation"s read from an "Fixation-Data" file.

        Args:
            fixation_file: A string containing the name of the 'Fixation-Data.tsv' file output by the
                Tobii software.
            media_offset: the coordinates of the top left corner of the window
                    showing the interface under study. (0,0) if the interface was
                    in full screen (default value)
        Returns:
            a list of "Fixation"s
        """

        all_fixation = []
        with open(fixation_file, 'r') as f:
            for _ in xrange(params.FIXATIONHEADERLINES - 1):
                next(f)
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                data = {"fixationindex": utils.cast_int(row["FixationIndex"]),
                        "timestamp": utils.cast_int(row["Timestamp"]),
                        "fixationduration": utils.cast_int(row["FixationDuration"]),
                        "fixationpointx": utils.cast_int(row["MappedFixationPointX"]),
                        "fixationpointy": utils.cast_int(row["MappedFixationPointY"])}
                all_fixation.append(Fixation(data, media_offset))

        return all_fixation

    @staticmethod
    def read_event_data(event_file, media_offset=(0, 0)):
        """Returns a list of "Event"s read from an "Event-Data" file.

        Args:
            event_file: A string containing the name of the 'Event-Data.tsv' file output by the
                Tobii software.
            media_offset: the coordinates of the top left corner of the window
                    showing the interface under study. (0,0) if the interface was
                    in full screen (default value)
        Returns:
            a list of "Event"s
        """

        all_event = []
        with open(event_file, 'r') as f:
            for _ in xrange(params.EVENTSHEADERLINES - 1):
                next(f)
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                data = {"timestamp": utils.cast_int(row["Timestamp"]),
                        "event": row["Event"],
                        "event_key": utils.cast_int(row["EventKey"])}
                if data["event"] == "LeftMouseClick" or data["event"] == "RightMouseClick":
                    data.update({"x_coord": utils.cast_int(row["Data1"]), "y_coord": utils.cast_int(row["Data2"])})
                elif data["event"] == "KeyPress":
                    data.update({"key_code": utils.cast_int(row["Data1"]), "key_name": row["Descriptor"]})
                elif data["event"] == "LogData":
                    data.update({"description": row["Data1"]})
                all_event.append(Event(data, media_offset))

        return all_event
