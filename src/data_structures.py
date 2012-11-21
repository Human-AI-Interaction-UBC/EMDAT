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

    def __init__(self, tobii_line, data=None):
        """
        Initializes a Datapoint from either a line of gaze data from "all-Data.tsv"
        or the equivalent data in array form.

        Args:
            tobii_line: a line of gaze data from "all-Data.tsv"
            data: An already parsed line of Tobii data

        Yields:
            a Datapoint object
        """
        if data == None:
            data = parse(tobii_line)
        [self.timestamp, self.datetimestamp, self.datetimestampstartoffset, self.number, self.gazepointxleft, self.gazepointyleft, self.camxleft, self.camyleft, 
         self.distanceleft, self.pupilleft, self.validityleft, self.gazepointxright, self.gazepointyright, self.camxright, self.camyright, self.distanceright, 
         self.pupilright, self.validityright, self.fixationindex, self.gazepointx, self.gazepointy, self.event, self.eventkey, self.data1, self.data2, self.descriptor, 
         self.stimuliname, self.stimuliid, self.mediawidth, self.mediaheight, self.mediaposx, self.mediaposy, self.mappedfixationpointx, self.mappedfixationpointy, 
         self.fixationduration, self.aoiids, self.aoinames, self.webgroupimage, self.mappedgazedatapointx, self.mappedgazedatapointy, self.microsecondtimestamp, 
         self.absolutemicrosecondtimestamp] = data
        self.segid = None
        self.is_valid = (self.validityright < 2 or self.validityleft < 2)

def parse(tobii_line):
    """
    Parses a line of gaze data from "all-Data.tsv" file into array form
    
    Args:
        tobii_line: a string containing one line read from an "All-Data.tsv" file.
        
    Yields:
        an array of converted types
    """
    strings = tobii_line.split('\t')
    try:
        data = [int(strings[0]), # timestamp
                strings[1], # datetimestamp
                strings[2], # datetimestampstartoffset
                cast_int(strings[3]), # number
                cast_float(strings[4]), # gazepointxleft
                cast_float(strings[5]), # gazepointyleft
                cast_float(strings[6]), # camxleft
                cast_float(strings[7]), # camyleft
                cast_float(strings[8]), # distanceleft
                cast_float(strings[9]), # pupilleft
                cast_int(strings[10]), # validityleft
                cast_float(strings[11]), # gazepointxright
                cast_float(strings[12]), # gazepointyright
                cast_float(strings[13]), # camxright
                cast_float(strings[14]), # camyright
                cast_float(strings[15]), # distanceright
                cast_float(strings[16]), # pupilright
                cast_int(strings[17]), # validityright
                cast_int(strings[18]), # fixationindex
                cast_float(strings[19]), # gazepointx
                cast_float(strings[20]), # gazepointy
                strings[21], # event
                strings[22], # eventkey
                strings[23], # data1
                strings[24], # data2
                strings[25], # descriptor
                strings[26], # stimuliname
                cast_int(strings[27]), # stimuliid
                cast_int(strings[28]), # mediawidth
                cast_int(strings[29]), # mediaheight
                cast_int(strings[30]), # mediaposx
                cast_int(strings[31]), # mediaposy
                cast_int(strings[32]), # mappedfixationpointx
                cast_int(strings[33]), # mappedfixationpointy
                cast_int(strings[34]), # fixationduration
                strings[35], # aoiids
                strings[36], # aoinames
                strings[37], # webgroupimage
                cast_int(strings[38]), # mappedgazedatapointx
                cast_int(strings[39]), # mappedgazedatapointy
                cast_int(strings[40]), # microsecondtimestamp
                cast_int(strings[41])] # absolutemicrosecondtimestamp
    except ValueError:
        data = None

    return data

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
    if str!="" and str!=None:
        v = int(str)
    else:
        v = None
    return v
#    try:
#        v = int(str)
#    except ValueError:
#        v = None
#    return v


def cast_float(str):
    """a helper method for converting strings to their float value
    
    Args:
        str: a string containing a number
    
    Returns:
        the float value of the string given or None if not a float
    """
    if str!="" and str!=None:
        v = float(str)
    else:
        v = None
    return v
#    try:
#        v = float(str)
#    except ValueError:
#        v = None
#    return v