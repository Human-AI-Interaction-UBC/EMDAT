"""
UBC Eye Movement Data Analysis Toolkit

Author: Nicholas FitzGerald - nicholas.fitzgerald@gmail.com
Modified by: Samad Kardan
             Oliver Schmid - oliver.schmd@gmail.com

Basic data structures used in EMDAT
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
        self.distance = data.get("distance", None)
        self.is_valid = data.get("is_valid", None)
        self.stimuliname = data.get("stimuliname", None)
        self.fixationindex = data.get("fixationindex", None)
        self.gazepointxleft = data.get("gazepointxleft", None)
        self.segid = None


class Fixation:
    """
    A class that holds the information for one Fixation
    
    Attributes:
        segid: a string indicating the Segment to which this Datapoint belongs
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
