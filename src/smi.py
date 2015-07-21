from Recording import Recording
from data_structures import Datapoint, Fixation, Event
import utils
import csv
import params


class SMIRecording(Recording):
    @staticmethod
    def read_all_data(all_file):
        all_data = []
        with open(all_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["L Event Info"] != "Fixation":  # ignore data points other than fixations (gaze points)
                    continue
                pupil_left = utils.cast_float(row["L Pupil Diameter [mm]"])
                pupil_right = utils.cast_float(row["R Pupil Diameter [mm]"])
                data = {"timestamp": utils.cast_int(row["Time"]),
                        "pupilsize": Recording.get_pupil_size(pupil_left, pupil_right),
                        "distance": 0,  # temporarily set to 0
                        "is_valid": True,  # temporarily set to true for all
                        "stimuliname": "Screen",  # temporarily set to the same stimuli
                        "fixationindex": utils.cast_int(row["Time"]),
                        "gazepointxleft": utils.cast_float(row["L POR X [px]"])}
                all_data.append(Datapoint(data))

        return all_data

    @staticmethod
    def read_fixation_data(fixation_file, media_offset=(0, 0)):
        all_fixation = []
        with open(fixation_file, 'r') as f:
            for i in xrange(params.EVENTS_FIRST_DATA_LINE - 1):
                if i is (params.FIXATION_HEADER_LINE - 1):  # read the row of the table header for fixations
                    fixation_headers = next(f).strip().split(',')
                else:
                    next(f)
            reader = csv.DictReader(f, fieldnames=fixation_headers)
            for row in reader:
                if not row["Event Type"].startswith("Fixation L"):
                    continue
                data = {"fixationindex": utils.cast_int(row["Number"]),
                        "timestamp": utils.cast_int(row["Start"]),
                        "fixationduration": utils.cast_int(row["Duration"]),
                        "fixationpointx": utils.cast_float(row["Location X"]),
                        "fixationpointy": utils.cast_float(row["Location Y"])}
                all_fixation.append(Fixation(data, media_offset))

        return all_fixation

    @staticmethod
    def read_event_data(event_file, media_offset=(0, 0)):
        all_event = []
        with open(event_file, 'r') as f:
            for i in xrange(params.EVENTS_FIRST_DATA_LINE - 1):
                if i is (params.USER_EVENT_HEADER_LINE - 1):  # read the row of the table header for user events
                    fixation_headers = next(f).strip().split(',')
                else:
                    next(f)
            reader = csv.DictReader(f, fieldnames=fixation_headers)
            for row in reader:
                if row["Event Type"] != "UserEvent":
                    continue
                data = {"timestamp": utils.cast_int(row["Start"]),
                        "description": row["Description"]}
                descriptions = row["Description"].split(" ")
                event_type = descriptions[2]
                if event_type == "UE-mouseclick":
                    if descriptions[3] == "left":
                        data.update({"event": "LeftMouseClick"})
                    else:
                        data.update({"event": "RightMouseClick"})
                    data.update({"x_coord": utils.cast_int(descriptions[4].split("=")[1]),
                                 "y_coord": utils.cast_int(descriptions[5].split("=")[1])})
                elif event_type == "UE-keypress":
                    data.update({"event": "KeyPress", "key_name": descriptions[3]})
                all_event.append(Event(data, media_offset))

        return all_event

