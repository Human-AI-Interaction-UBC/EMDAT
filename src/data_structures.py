"""
UBC Eye Movement Data Analysis Toolkit

Author: Nicholas FitzGerald - nicholas.fitzgerald@gmail.com
Modified by: Samad Kardan
             Oliver Schmid - oliver.schmd@gmail.com

Basic data structures used in EMDAT
"""
from warnings import warn

class Datapoint():
    """
    A class that holds the information for one eye gaze data sample (one line of data logs) 
    
    Attributes:
        segid: a string indicating the Segment that this Datapoint belongs to
        is_valid: a boolean indicating whether this sample is valid
    
        Please refer to the Tobii manual for the description of the rest of the attributes
    """

    def fromString(text):
        """
        Inits Datapoint class with a line of gaze data from "all-Data.tsv" file
        
        Args:
            data_point: a string containing one line read from an "All-Data.tsv" file.
            
        Yields:
            a Datapoint object
        """
        datapoint = Datapoint(text.split('\t'))

        # convert strings to number formats
        datapoint.timestamp = cast_int(datapoint.timestamp)
        # datapoint.datetimestamp already string
        # datapoint.datetimestampstartoffset already string
        datapoint.number = cast_int(datapoint.number)
        datapoint.gazepointxleft = cast_float(datapoint.gazepointxleft)
        datapoint.gazepointyleft = cast_float(datapoint.gazepointyleft)
        datapoint.camxleft = cast_float(datapoint.camxleft)
        datapoint.camyleft = cast_float(datapoint.camyleft)
        datapoint.distanceleft = cast_float(datapoint.distanceleft)
        datapoint.pupilleft = cast_float(datapoint.pupilleft)
        
        datapoint.validityleft = cast_int(datapoint.validityleft)
        datapoint.gazepointxright = cast_float(datapoint.gazepointxright)
        datapoint.gazepointyright = cast_float(datapoint.gazepointyright)
        datapoint.camxright = cast_float(datapoint.camxright)
        datapoint.camyright = cast_float(datapoint.camyright)
        datapoint.distanceright = cast_float(datapoint.distanceright)
        datapoint.pupilright = cast_float(datapoint.pupilright)
        datapoint.validityright = cast_int(datapoint.validityright)
        datapoint.fixationindex = cast_int(datapoint.fixationindex)
        datapoint.gazepointx = cast_int(datapoint.gazepointx)
        
        datapoint.gazepointy = cast_int(datapoint.gazepointy)
        # datapoint.event already string
        # datapoint.eventkey already string
        # datapoint.data1 already string
        # datapoint.data2 already string
        # datapoint.descriptor already string
        # datapoint.stimuliname already string
        datapoint.stimuliid = cast_int(datapoint.stimuliid)
        datapoint.mediawidth = cast_int(datapoint.mediawidth)
        datapoint.mediaheight = cast_int(datapoint.mediaheight)
        
        datapoint.mediaposx = cast_int(datapoint.mediaposx)
        datapoint.mediaposy = cast_int(datapoint.mediaposy)
        datapoint.mappedfixationpointx = cast_int(datapoint.mappedfixationpointx)
        datapoint.mappedfixationpointy = cast_int(datapoint.mappedfixationpointy)
        datapoint.fixationduration = cast_int(datapoint.fixationduration)
        # datapoint.aoiids already comma seperated string of AOIs
        # datapoint.aoinames already string
        # datapoint.webgroupimage already string
        datapoint.mappedgazedatapointx = cast_int(datapoint.mappedgazedatapointx)
        datapoint.mappedgazedatapointy = cast_int(datapoint.mappedgazedatapointy)
        
        datapoint.microsecondtimestamp = cast_int(datapoint.microsecondtimestamp)
        datapoint.absolutemicrosecondtimestamp = cast_int(datapoint.absolutemicrosecondtimestamp)
        return datapoint

    def __init__(self, data):
        [self.timestamp, self.datetimestamp, self.datetimestampstartoffset, self.number, self.gazepointxleft, self.gazepointyleft, self.camxleft, self.camyleft, 
         self.distanceleft, self.pupilleft, self.validityleft, self.gazepointxright, self.gazepointyright, self.camxright, self.camyright, self.distanceright, 
         self.pupilright, self.validityright, self.fixationindex, self.gazepointx, self.gazepointy, self.event, self.eventkey, self.data1, self.data2, self.descriptor, 
         self.stimuliname, self.stimuliid, self.mediawidth, self.mediaheight, self.mediaposx, self.mediaposy, self.mappedfixationpointx, self.mappedfixationpointy, 
         self.fixationduration, self.aoiids, self.aoinames, self.webgroupimage, self.mappedgazedatapointx, self.mappedgazedatapointy, self.microsecondtimestamp, 
         self.absolutemicrosecondtimestamp,_] = data
        self.segid = None
        self.is_valid = (self.validityright < 2 or self.validityleft < 2)

    def set_segid(self,segid):
        """Sets the "Segment" id for this Datapoint
        
        Args:
            segid: a string containing the "Segment" id
        """
        self.segid = segid

    def get_segid(self):
        """Returns the "Segment" id for this Datapoint
            
        Returns:
            a string containing the "Segment" id
            
        Raises:
            Exception: if the segid is not set before reading it an Exception will be thrown
        """
        if self.segid != None:
            return self.segid
        raise Exception('The segid is accessed before setting the initial value in a datapoint!')
            

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
    def __init__(self, eventstr):
        """Inits Event class with a line of gaze data from an "Event-Data.tsv" file
        
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


def cast_int(str):
    """a helper method for converting strings to their integer value
    
    Args:
        str: a string containing a number
    
    Returns:
        the integer value of the string given or None if not an integer
    """
    try:
        v = int(str)
    except ValueError:
        v = None
    return v


def cast_float(str):
    """a helper method for converting strings to their float value
    
    Args:
        str: a string containing a number
    
    Returns:
        the float value of the string given or None if not a float
    """
    try:
        v = float(str)
    except ValueError:
        v = None
    return v
