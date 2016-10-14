import Recording
from data_structures import Datapoint, Fixation, Event
import csv
import utils
import params


class TobiiV3Recording(Recording.Recording):
    def read_all_data(self, all_file):
        """Returns a list of "Datapoint"s read from an "All-Data" file.

        Args:
            all_file:A string containing the name of the 'All-Data.tsv' file output by the Tobii software.

        Returns:
            a list of "Datapoint"s
        """
        all_data = []
        with open(all_file, 'r') as f:
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                if row["MediaName"] != 'ScreenRec':  # ignore non-recording data point
                    continue
                if not row["ValidityLeft"] or not row["ValidityRight"]: #ignore data point with no validity information
                    continue
                pupil_left = utils.cast_float(row["PupilLeft"], -1)
                pupil_right = utils.cast_float(row["PupilRight"], -1)
                distance_left = utils.cast_float(row["DistanceLeft"], -1)
                distance_right = utils.cast_float(row["DistanceRight"], -1)
                data = {"timestamp": utils.cast_int(row["RecordingTimestamp"]),
                        "pupilsize": Recording.get_pupil_size(pupil_left, pupil_right),
                        "distance": Recording.get_distance(distance_left, distance_right),
                        "is_valid": utils.cast_int(row["ValidityRight"]) < 2 or utils.cast_int(row["ValidityLeft"]) < 2,
                        "stimuliname": row["MediaName"],
                        "fixationindex": utils.cast_int(row["FixationIndex"]),
                        "gazepointxleft": utils.cast_float(row["GazePointLeftX (ADCSpx)"])}
                all_data.append(Datapoint(data))

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
            currentfix = 0
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                if row["MediaName"] != 'ScreenRec':  # ignore non-recording data point
                    continue
                if not row["ValidityLeft"] or not row["ValidityRight"]: #ignore data point with no validity information
                    continue
                if row["GazeEventType"] != "Fixation" or currentfix == row["FixationIndex"]: #if not a fixation or the current fixation
                    continue
                data = {"fixationindex": utils.cast_int(row["FixationIndex"]),
                        "timestamp": utils.cast_int(row["RecordingTimestamp"]),
                        "fixationduration": utils.cast_int(row["GazeEventDuration"]),
                        "fixationpointx": utils.cast_int(row["FixationPointX (MCSpx)"]),
                        "fixationpointy": utils.cast_int(row["FixationPointY (MCSpx)"])}
                all_fixation.append(Fixation(data, self.media_offset))
                currentfix = row["FixationIndex"]

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
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                if row["MediaName"] != 'ScreenRec':  # ignore non-recording data point
                    continue
                if row["MouseEventIndex"] : #mouse event
                    data = {"timestamp": utils.cast_int(row["RecordingTimestamp"]),
                        "event": row["MouseEvent"]+"MouseClick",
                        "x_coord": utils.cast_int(row["MouseEventX (MCSpx)"]),
                        "y_coord": utils.cast_int(row["MouseEventY (MCSpx)"])
                        }
                    all_event.append(Event(data, self.media_offset))
                elif row["KeyPressEventIndex"] : #keyboard event
                    data = {"timestamp": utils.cast_int(row["RecordingTimestamp"]),
                        "event": "KeyPress",
                        "key_name": row["KeyPressEvent"]
                        }
                    all_event.append(Event(data, self.media_offset))

        return all_event
