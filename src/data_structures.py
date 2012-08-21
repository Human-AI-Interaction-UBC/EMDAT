"""
UBC Eye Movement Data Analysys Toolkit

Author: Nicholas FitzGerald - nicholas.fitzgerald@gmail.com
Modified by: Samad Kardan

Basic data structures used in EMDAT
"""
class Datapoint():
    """
    A class that holds the infromation 
    """
    def __init__(self, data_point):
        """Inits Datapoint class with a line of gaze data from "all-Data.tsv" file
        
        Args:
            data_point: a string containing one line read from an "All-Data.tsv" file.
            
        Yields:
            a Datapoint object
        """
        #data_point = data_point.replace('\t\r\n','')#??
        #print data_point.split('\t')
        #print len(data_point.split('\t'))
        [self.timestamp, self.datetimestamp, self.datetimestampstartoffset, self.number, self.gazepointxleft, self.gazepointyleft, self.camxleft, self.camyleft, self.distanceleft, self.pupilleft, self.validityleft, self.gazepointxright, self.gazepointyright, self.camxright, self.camyright, self.distanceright, self.pupilright, self.validityright, self.fixationindex, self.gazepointx, self.gazepointy, self.event, self.eventkey, self.data1, self.data2, self.descriptor, self.stimuliname, self.stimuliid, self.mediawidth, self.mediaheight, self.mediaposx, self.mediaposy, self.mappedfixationpointx, self.mappedfixationpointy, self.fixationduration, self.aoiids, self.aoinames, self.webgroupimage, self.mappedgazedatapointx, self.mappedgazedatapointy, self.microsecondtimestamp, self.absolutemicrosecondtimestamp,_] = data_point.split('\t')

        self.timestamp = cast_int(self.timestamp)
        self.number = cast_int(self.number)
        self.validityleft = cast_int(self.validityleft)
        self.validityright = cast_int(self.validityright)
        self.fixationindex = cast_int(self.fixationindex)
        self.gazepointx = cast_int(self.gazepointx)
        self.gazepointy = cast_int(self.gazepointy)
        self.stimuliid = cast_int(self.stimuliid)
        self.mediawidth = cast_int(self.mediawidth)
        self.mediaheight = cast_int(self.mediaheight)
        self.mediaposx = cast_int(self.mediaposx)
        self.mediaposy = cast_int(self.mediaposy)
        self.mappedfixationpointx = cast_int(self.mappedfixationpointx)
        self.mappedfixationpointy = cast_int(self.mappedfixationpointy)
        self.fixationduration = cast_int(self.fixationduration)
        #self.aoiids = cast_int(self.aoiids)#not int : it's comma seperated string of AOIs
        self.mappedgazedatapointx = cast_int(self.mappedgazedatapointx)
        self.mappedgazedatapointy = cast_int(self.mappedgazedatapointy)
        self.microsecondtimestamp = cast_int(self.microsecondtimestamp)
        self.absolutemicrosecondtimestamp = cast_int(self.absolutemicrosecondtimestamp)
        
        self.gazepointxleft = cast_float(self.gazepointxleft)
        self.gazepointyleft = cast_float(self.gazepointyleft)
        self.camxleft = cast_float(self.camxleft)
        self.camyleft = cast_float(self.camyleft)
        self.distanceleft = cast_float(self.distanceleft)
        self.pupilleft = cast_float(self.pupilleft)
        self.gazepointyright = cast_float(self.gazepointyright)
        self.camxright = cast_float(self.camxright)
        self.camyright = cast_float(self.camyright)
        self.distanceright = cast_float(self.distanceright)
        self.pupilright = cast_float(self.pupilright)
        self.segid = None
        #self.is_valid = (not self.camxleft == -1)
        self.is_valid = (self.validityright < 2 or self.validityleft < 2)
    def set_segid(self,segid):
        """Sets the "Segment" id for this Datapoint
        
        Args:
            segid: a string containing the "Segment" id
        """
        self.segid = segid
    def get_segid(self):
        """Returns the "Segment" id for this Datapoint
        
        Args:
            data_point: a string containing one line read from an "All-Data.tsv" file.
            
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
    """
    def __init__(self, fix_point, media_offset = (0, 0)):
        """
        Args:
            fix_point: string. A line read from a "Fixation-Data.tsv" file.
        """
        #fix_point = fix_point.replace('\t\r\n','')
        [self.fixationindex, self.timestamp, self.fixationduration, self.mappedfixationpointx, self.mappedfixationpointy,_] = fix_point.split('\t')
        self.fixationindex = cast_int(self.fixationindex)
        self.timestamp = cast_int(self.timestamp)
        self.fixationduration = cast_int(self.fixationduration)
        (media_offset_x, media_offset_y) = media_offset
        self.mappedfixationpointx = cast_int(self.mappedfixationpointx) - media_offset_x
        self.mappedfixationpointy = cast_int(self.mappedfixationpointy) - media_offset_y
        self.segid = None
        
    def set_segid(self,segid):
        self.segid = segid
    def get_segid(self):
        if self.segid != None:
            return self.segid
        raise Exception('The segid is accessed before setting the initial value in a fixation point!')

class Event():
    """
    """
    def __init__(self, eventstr):
        """
        """
        #Timestamp    Event    EventKey    Data1    Data2    Descriptor
        #print eventstr.split('\t')
        [self.timestamp, self.event, self.eventKey, self.data1, self.data2,self.descriptor,_] = eventstr.split('\t')
        self.timestamp = cast_int(self.timestamp)
        self.eventKey = cast_int(self.eventKey)

class Action():
    """
    """
    def __init__(self, actstr):
        """
        """
        #Action TimeStartoffset
        #print eventstr.split('\t')
        [self.action, self.timestamp] = actstr.split('\t')
        self.timestamp = cast_int(self.timestamp)
        self.action = cast_int(self.action) #action is a nubmeric code!
            
class Action2():
    """
    """
    def __init__(self, actstr):
        """
        """
        #Action TimeStartoffset
        #print eventstr.split('\t')
        [self.timeSincePre, self.timestamp, self.action] = actstr.split('\t')
        self.timeSincePre = cast_int(self.timeSincePre)
        self.timestamp = cast_int(self.timestamp)
        self.action = cast_int(self.action) #action is a nubmeric code!

def cast_int(str):
    try:
        v = int(str)
    except ValueError:
        v = None
    return v

def cast_float(str):
    try:
        v = float(str)
    except ValueError:
        v = None
    return v
