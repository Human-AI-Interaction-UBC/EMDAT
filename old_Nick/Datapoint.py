class Datapoint():
    def __init__(self, data_point):
        """
        @type data_point: str
        @param data_point: A line read from an "All-Data.tsv" file.
        """
        data_point = data_point.replace('\t\r\n','')
        #print data_point.split('\t')
        #print len(data_point.split('\t'))
        [self.timestamp, self.datetimestamp, self.datetimestampstartoffset, self.number, self.gazepointxleft, self.gazepointyleft, self.camxleft, self.camyleft, self.distanceleft, self.pupilleft, self.validityleft, self.gazepointxright, self.gazepointyright, self.camxright, self.camyright, self.distanceright, self.pupilright, self.validityright, self.fixationindex, self.gazepointx, self.gazepointy, self.event, self.eventkey, self.data1, self.data2, self.descriptor, self.stimuliname, self.stimuliid, self.mediawidth, self.mediaheight, self.mediaposx, self.mediaposy, self.mappedfixationpointx, self.mappedfixationpointy, self.fixationduration, self.aoiids, self.aoinames, self.webgroupimage, self.mappedgazedatapointx, self.mappedgazedatapointy, self.microsecondtimestamp, self.absolutemicrosecondtimestamp] = data_point.split('\t')

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
        self.aoiids = cast_int(self.aoiids)
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

        self.is_valid = (not self.camxleft == -1)

class Fixation():
        def __init__(self, fix_point, media_offset = (0, 0)):
            """
            @type fix_point: str
            @param fix_point: A line read from a "Fixation-Data.tsv" file.
            """
            fix_point = fix_point.replace('\t\r\n','')
            [self.fixationindex, self.timestamp, self.fixationduration, self.mappedfixationpointx, self.mappedfixationpointy] = fix_point.split('\t')
            self.fixationindex = cast_int(self.fixationindex)
            self.timestamp = cast_int(self.timestamp)
            self.fixationduration = cast_int(self.fixationduration)
            (media_offset_x, media_offset_y) = media_offset
            self.mappedfixationpointx = cast_int(self.mappedfixationpointx) - media_offset_x
            self.mappedfixationpointy = cast_int(self.mappedfixationpointy) - media_offset_y


def cast_int(string):
    if string == '':
        return None
    else:
        return int(string)

def cast_float(string):
    if string == '':
        return None
    else:
        return float(string)
