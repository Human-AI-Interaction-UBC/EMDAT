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


class Fixation():
    """
    A class that holds the information for one Fixation representing one line in a "Fixation-Data.tsv" file
    
    Attributes:
        segid: a string indicating the Segment that this Datapoint belongs to
    
        Please refer to the Tobii manual for the description of the rest of the attributes
    """

    def __init__(self, fix_point, media_offset = (0, 0)):
        """Inits Fixation class with a line of gaze data from a "Fixation-Data.tsv" file
        
        Args:
            fix_point: a string containing one line read from a "Fixation-Data.tsv" file        
            media_offset: the coordinates of the top left corner of the window
                showing the interface under study. (0,0) if the interface was
                in full screen (default value)
            
        Yields:
            a Fixation object
        """

        #fix_point = fix_point.replace('\t\r\n','')
        [self.fixationindex, self.timestamp, self.fixationduration, self.mappedfixationpointx, self.mappedfixationpointy,_] = fix_point.split('\t')
        self.fixationindex = cast_int(self.fixationindex)
        self.timestamp = cast_int(self.timestamp)
        self.fixationduration = cast_int(self.fixationduration)
        if self.fixationduration == 0:
            warn("A zero duration Fixation!")
        (media_offset_x, media_offset_y) = media_offset
        self.mappedfixationpointx = cast_int(self.mappedfixationpointx) - media_offset_x
        self.mappedfixationpointy = cast_int(self.mappedfixationpointy) - media_offset_y
        self.segid = None

    def set_segid(self,segid):
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
        if self.segid != None:
            return self.segid
        raise Exception('The segid is accessed before setting the initial value in a fixation point!')


class Event():
    """
    A class that holds the information for one Event representing one line in the an "Event-Data.tsv" file
    
    Please refer to the Tobii manual for the description of the attributes
    """
    def __init__(self, eventstr, media_offset = (0, 0)):
        """Inits Event class with a line of gaze data from an "Event-Data.tsv" file
			Format:
			ScreenRecStarted|8192
			ScreenRecStopped|16384 
			URLStart|512|||URL/website name 
			URLEnd|024|||URL/website name
			KeyPress|4|ASCII code for key pressed||Key name
			LeftMouseClick|1|X mouse coordinate|Y mouse coordinate
			RightMouseClick|2|X mouse coordinate|Y mouse coordinate
			LogData|0|Log name|Logging comment 
        Args:
            eventstr: a string containing one line read from an "Event-Data.tsv" file
            
        Yields:
            an Event object
        """
        #Timestamp    Event    EventKey    Data1    Data2    Descriptor
        #print eventstr.split('\t')
        [self.timestamp, self.event, self.eventKey, self.data1, self.data2,self.descriptor,_] = eventstr.split('\t')
        self.timestamp = cast_int(self.timestamp)
        self.eventKey = cast_int(self.eventKey)
        if self.event == "LeftMouseClick" or self.event == "RightMouseClick":
            (media_offset_x, media_offset_y) = media_offset
            self.data1 = cast_int(self.data1) - media_offset_x
            self.data2 = cast_int(self.data2) - media_offset_y
        elif self.event == "KeyPress":
            self.data1 = cast_int(self.data1)
        self.segid = None

    def set_segid(self,segid):
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
        if self.segid != None:
            return self.segid
        raise Exception('The segid is accessed before setting the initial value in a fixation point!')


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
