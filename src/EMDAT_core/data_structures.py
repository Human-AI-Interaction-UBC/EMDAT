"""
UBC Eye Movement Data Analysis Toolkit (EMDAT), Version 3

Basic data structures used in EMDAT.

Authors: Nicholas FitzGerald (creator), Oliver Schmid, Samad Kardan, Sebastien Lalle.
Institution: The University of British Columbia.
"""
from warnings import warn


class Datapoint:
    """
    A class that holds the information for one eye gaze data sample (one line of data logs)

    Attributes:
        segid: a string indicating the Segment that this Datapoint belongs to
        is_valid: a boolean indicating whether this sample is valid

        Please refer to the Tobii manual for the description of the rest of the attributes
    """

    def __init__(self, data):
        """
        Initializes a Datapoint from either a line of gaze data from "all-Data.tsv"
        or the equivalent data in array form.

        Args:
            tobii_line: a line of gaze data from "all-Data.tsv"
            data: An already parsed line of Tobii data

        Yields:
            a Datapoint object
        """
        self.timestamp = data.get("timestamp", None)
        self.pupilsize = data.get("pupilsize", None)
        self.pupilvelocity = data.get("pupilvelocity", None)
        self.distance = data.get("distance", None)
        self.is_valid = data.get("is_valid", None)
        self.stimuliname = data.get("stimuliname", None)
        self.fixationindex = data.get("fixationindex", None)
        self.gazepointx = data.get("gazepointx", None)
        self.gazepointy = data.get("gazepointy", None)
        self.segid = None

    def get_string(self, sep='\t'):
        return str(self.timestamp)+sep+str(self.pupilsize)+sep+str(self.pupilvelocity)+sep+str(self.distance)+sep+str(self.is_valid)+sep+str(self.stimuliname)+sep+str(self.fixationindex)#+sep+str(self.gazepointxleft)

class Fixation:
    """
    A class that holds the information for one Fixation

    Attributes:
        segid: a string indicating the Segment to which this Fixation belongs
    """

    def __init__(self, data, media_offset = (0, 0)):
        """Initializes a Fixation with attributes

        Args:
            data: a dictionary containing attributes of a fixation
            media_offset: the coordinates of the top left corner of the window
                showing the interface under study. (0,0) if the interface was
                in full screen (default value)

        Yields:
            a Fixation object
        """

        self.fixationindex = data.get("fixationindex", None)
        self.timestamp = data.get("timestamp", None)
        self.fixationduration = data.get("fixationduration", None)
        self.mappedfixationpointx = data.get("fixationpointx", None)
        self.mappedfixationpointy = data.get("fixationpointy", None)
        self.segid = None

        if self.fixationduration == 0:
            warn("A zero duration fixation.")

        if self.mappedfixationpointx is None or self.mappedfixationpointx is None:
            warn("A fixation with invalid coordinates. Fix="+str(self.fixationindex))
        else:
            (media_offset_x, media_offset_y) = media_offset
            self.mappedfixationpointx -= media_offset_x
            self.mappedfixationpointy -= media_offset_y

    def set_segid(self, segid):
        """Sets the "Segment" id for this Fixation

        Args:
            segid: a string containing the "Segment" id
        """
        self.segid = segid

    def get_segid(self):
        """Returns the "Segment" id for this Fixation

        Returns:
            a string containing the "Segment" id

        Raises:
            Exception: if the segid is not set before reading it an Exception will be thrown
        """
        if self.segid is not None:
            return self.segid
        raise Exception('The segid is accessed before setting the initial value in a fixation point.')

    def get_string(self, sep='\t'):
        return str(self.fixationindex)+sep+str(self.timestamp)+sep+str(self.fixationduration)+sep+str(self.mappedfixationpointx)+sep+str(self.mappedfixationpointy)

class Saccade:
    """
    A class that holds the information for one Saccade

    Attributes:
        segid: a string indicating the Segment to which this Saccade belongs
    """

    def __init__(self, data, media_offset = (0, 0)):
        """Initializes a Saccade with attributes

        Args:
            data: a dictionary containing attributes of a Saccade
            media_offset: the coordinates of the top left corner of the window
                showing the interface under study. (0,0) if the interface was
                in full screen (default value)

        Yields:
            a Sacade object
        """

        self.saccadeindex = data.get("saccadeindex", None)
        self.timestamp = data.get("timestamp", None)
        self.saccadeduration = data.get("saccadeduration", None)
        self.saccadedistance = data.get("saccadedistance", None)
        self.saccadespeed = data.get("saccadespeed", None)
        self.saccadeacceleration = data.get("saccadeacceleration", None)
        self.saccadestartpointx = data.get("saccadestartpointx", None)
        self.saccadestartpointy = data.get("saccadestartpointy", None)
        self.saccadeendpointx = data.get("saccadeendpointx", None)
        self.saccadeendpointy = data.get("saccadeendpointy", None)
        self.saccadequality = data.get("saccadequality", None)
        self.segid = None

        if self.saccadeduration == 0:
            warn("A zero duration fixation.")

        if self.saccadestartpointx is None or self.saccadestartpointy is None or self.saccadeendpointx is None or self.saccadeendpointy is None:
            warn("A Saccade with invalid coordinates. Fix="+str(self.saccadeindex))
        else:
            (media_offset_x, media_offset_y) = media_offset
            self.saccadestartpointx -= media_offset_x
            self.saccadestartpointy -= media_offset_x
            self.saccadeendpointx -= media_offset_x
            self.saccadeendpointy -= media_offset_y

    def set_segid(self, segid):
        """Sets the "Segment" id for this Saccade

        Args:
            segid: a string containing the "Segment" id
        """
        self.segid = segid

    def get_segid(self):
        """Returns the "Segment" id for this Saccade

        Returns:
            a string containing the "Segment" id

        Raises:
            Exception: if the segid is not set before reading it an Exception will be thrown
        """
        if self.segid is not None:
            return self.segid
        raise Exception('The segid is accessed before setting the initial value in a fixation point.')

    def get_string(self, sep='\t'):
        return str(self.saccadeindex)+sep+str(self.timestamp)+sep+str(self.saccadeduration)+sep+str(self.saccadedistance)+sep+str(self.saccadespeed)+sep+str(self.saccadeacceleration)+sep+str(
              self.saccadestartpointx)+sep+str(self.saccadestartpointy)+sep+str(self.saccadeendpointx)+sep+str(self.saccadeendpointy)+sep+str(self.saccadequality)

class Event:
    """
    A class that holds the information for one Event
    """
    def __init__(self, data, media_offset=(0, 0)):
        """Initializes an Event with attributes

        Args:
            data: a dictionary containing attributes of an event.

        Yields:
            an Event object
        """

        self.timestamp = data.get("timestamp", None)
        self.event = data.get("event", None)
        self.eventKey = data.get("event_key", None)
        self.x_coord = data.get("x_coord", None)
        self.y_coord = data.get("y_coord", None)
        self.key_code = data.get("key_code", None)
        self.key_name = data.get("key_name", None)
        self.description = data.get("description", None)
        self.segid = None

        if self.event == "LeftMouseClick" or self.event == "RightMouseClick":
            (media_offset_x, media_offset_y) = media_offset
            self.x_coord -= media_offset_x
            self.y_coord -= media_offset_y
            self.data1 = self.x_coord
            self.data2 = self.y_coord
        elif self.event == "KeyPress":
            self.data1 = self.key_code

    def set_segid(self, segid):
        """Sets the "Segment" id for this Event

        Args:
            segid: a string containing the "Segment" id
        """
        self.segid = segid

    def get_segid(self):
        """Returns the "Segment" id for this Event

        Returns:
            a string containing the "Segment" id

        Raises:
            Exception: if the segid is not set before reading it an Exception will be thrown
        """
        if self.segid is not None:
            return self.segid
        raise Exception('The segid is accessed before setting the initial value in an event.')

    def get_string(self, sep='\t'):
        return str(self.timestamp)+sep+str(self.event)+sep+str(self.eventKey)+sep+str(self.x_coord)+sep+str(self.y_coord)+sep+str(self.key_code)+sep+str(self.key_name)+sep+str(self.description)

def cast_int(str):
    """a helper method for converting strings to their integer value

    Args:
        str: a string containing a number

    Returns:
        the integer value of the string given or None if not an integer
    """
    try:
        v = int(str)
    except:
        v = None
    return v
