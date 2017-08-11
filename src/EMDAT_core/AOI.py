"""
UBC Eye Movement Data Analysis Toolkit (EMDAT), Version 3
The Generic Area of Interest Classes
Created on 2011-08-26

In EMDAT, the bounderies of an Area of Interest (AOI) is defined as a polygon on the screen. You can
optionally define a second polygone inside the first polygone to be excluded from an AOI.
An AOI can be always active (a global AOI) or can be active during certain time intervals.
In order to calculate the features for an AOI instance, you need to create an AOI_Stat instance and
map it to a target AOI object by passing it to the AOI_Stat constructor. The resulting AOI_Stat
will calculate all features related to the given AOI and store them for later reference


Authors: Samad Kardan (creator), Sebastien Lalle.
Institution: The University of British Columbia.
"""

from utils import *
from warnings import warn


class AOI():

    def __init__(self, aid, polyin, polyout=[], timeseq=[]):
        """Inits AOI class
        Args:
            aid: AOI id

            polyin: the polygon defining the boundaries of the AOI in form of a list of (x,y) tuples

            polyout: optional polygon inside the boundaries of the AOI that is not part of
                the AOI in form of a list of (x,y) tuples

            timeseq: the time sequence of the format [(start1, end1), (start2, end2), ...] that
                specifies the intervals when this AOI is active

        Yields:
            an AOI object
        """
        self.aid = aid
        self.polyin = polyin
        self.polyout = polyout
        self.timeseq = timeseq
#            self.partial = True

    def set_coordinates(self, polyin, polyout=[]):
        """Sets the coordiantes of the AOI

        Args:
            polyin: the polygon defining the bounderies of the AOI in form of a list of (x,y) tuples
            polyout: optional polygon inside the bounderies of the AOI that is not part of the AOI
                in form of a list of (x,y) tuples
        """

        self.polyin = polyin
        self.polyout = polyout

    def is_active(self,start,end):
        """Determines if an AOI is active during the whole given time interval


        Args:
            start: time interval start
            end: time interval end

        Returns:
            true if the AOI is always active within the given time interval
        """
        if start == -1:
            return False
        if self.timeseq:
            for intr in self.timeseq:
                if (start>=intr[0] and start<intr[1])or(end>intr[0] and end<=intr[1]):
                    return True
                elif (start<intr[0] and start<intr[1])and(end>intr[0] and end>intr[1]):
                    warn("Incorrect definition of Dynamic AOI and Segments, AOI info not calculated for AOI:"+self.aid)
            return False #not active
        else:
            return True #global AOI

    def is_active_partition(self,start,end):
        """Determines if an AOI is partially active during a given time interval

        If the AOI is active at any sub-interval of the given time interval returns true
        if such sub-interval exists it also returns its start and end that AOI is active otherwise returns False, []

        Args:
            start: time interval start
            end: time interval start

        Returns:
            A boolean for whether the AOI is active or not
            ovelap_part: The subset of the time interval [sub_start,sub_end] that AOI is active or
            [] if it is active during the whole interval or not active at all.
        """
        #if (end - start)== 0:
        if start == -1:
            return False, []
        if params.DEBUG or params.VERBOSE == "VERBOSE":
            print "in:",self.aid
        ovelap_part = []
        is_active = False
        if self.timeseq:
            for intr in self.timeseq:
                if (start>=intr[0] and end<=intr[1]):
                    return True, [] #active during the whole interval
                else:
                    if start<=intr[1] and end>=intr[0]:
                        if params.DEBUG or params.VERBOSE == "VERBOSE":
                            print "partial:",start,end,":",intr[0],intr[1]
                        ovstart = max(start,intr[0])
                        ovend  = min(end,intr[1])
                        ovelap_part.append( (ovstart,ovend) )
                        is_active = True

            return is_active, ovelap_part #partially or not active
        else:
            return True, [] #global AOI


class AOI_Stat():
    """Methods of AOI_Stat calculate and store all features related to the given AOI object
    """

    def __init__(self,aoi,seg_fixation_data, starttime, endtime, active_aois, seg_event_data=None):
        """Inits AOI_Stat class

        Args:
            aoi: the aoi object for which the statistics are calculated
            seg_fixation_data:
            starttime:
            endtime:
            active_aois:list of the AOI objects that will be used for calculating the transitions between this AOI and other AOIs

        Yields:
            an AOI_Stat object
        """
        self.aoi = aoi
        self.isActive, partition = self.aoi.is_active_partition(starttime, endtime)

        #init features
        self.features = {}
        self.starttime = -1
        self.features['numfixations'] = 0
        self.features['longestfixation'] = -1
        self.features['meanfixationduration'] = -1
        self.features['stddevfixationduration'] = -1
        self.features['timetofirstfixation'] = -1
        self.features['timetolastfixation'] = -1
        self.features['proportionnum'] = 0
        self.features['proportiontime'] = 0
        self.features['fixationrate'] = 0
        self.features['totaltimespent'] = 0
        self.features['numevents'] = 0
        self.features['numleftclic'] = 0
        self.features['numrightclic'] = 0
        self.features['numdoubleclic'] = 0
        self.features['leftclicrate'] = 0
        self.features['rightclicrate'] = 0
        self.features['doubleclicrate'] = 0
        self.features['timetofirstleftclic'] = -1
        self.features['timetofirstrightclic'] = -1
        self.features['timetofirstdoubleclic'] = -1
        self.features['timetolastleftclic'] = -1
        self.features['timetolastrightclic'] = -1
        self.features['timetolastdoubleclic'] = -1
        self.total_trans_from = 0
        self.variance = 0
        for aoi in active_aois:
            aid = aoi.aid
            self.features['numtransfrom_%s'%(aid)] = 0
            self.features['proptransfrom_%s'%(aid)] = 0

        if not(self.isActive):
            return

        fixation_data = []
        event_data = []

        if partition:
            if params.DEBUG or params.VERBOSE == "VERBOSE":
                print "partition",partition
            for intr in partition:
                if starttime <= intr[1] and endtime >= intr[0]:
                    _,st,en = get_chunk(seg_fixation_data, 0, intr[0],intr[1])
                    fixation_data += seg_fixation_data[st:en]
                    if seg_event_data != None:
                        _,st,en = get_chunk(seg_event_data, 0, intr[0],intr[1])
                        event_data += seg_event_data[st:en]
            if params.DEBUG or params.VERBOSE == "VERBOSE":
                print "len(seg_fixation_data)",seg_fixation_data
                print "len(fixation_data)",fixation_data
        else:  #global AOI (alaways active)
            fixation_data = seg_fixation_data
            if seg_event_data != None:
                event_data = seg_event_data

		fixation_indices = []
        fixation_indices = filter(lambda i: _fixation_inside_aoi(fixation_data[i], self.aoi.polyin, self.aoi.polyout), range(len(fixation_data)))
        fixations = map(lambda i: fixation_data[i], fixation_indices)

        if seg_event_data != None:
            event_indices = filter(lambda i: _event_inside_aoi(event_data[i],self.aoi.polyin, self.aoi.polyout), range(len(event_data)))
            events = map(lambda i: event_data[i], event_indices)
            (leftc, rightc, doublec, _) = generate_event_lists(events)


        numfixations = len(fixations)
        self.features['numfixations'] = numfixations
        self.features['longestfixation'] = -1
        self.features['timetofirstfixation'] = -1
        self.features['timetolastfixation'] = -1
        self.features['proportionnum'] = 0
        self.starttime = starttime
        totaltimespent = sum(map(lambda x: x.fixationduration, fixations))
        self.features['totaltimespent'] = totaltimespent
        length = endtime - starttime

        self.features['proportiontime'] = float(totaltimespent)/length
        if numfixations > 0:
            self.features['longestfixation'] = max(map(lambda x: x.fixationduration, fixations))
            self.features['meanfixationduration'] = mean(map(lambda x: float(x.fixationduration), fixations))
            self.features['stddevfixationduration'] = stddev(map(lambda x: float(x.fixationduration), fixations))
            self.features['timetofirstfixation'] = fixations[0].timestamp - starttime
            self.features['timetolastfixation'] = fixations[-1].timestamp - starttime
            self.features['proportionnum'] = float(numfixations)/len(fixation_data)
            self.features['fixationrate'] = numfixations / float(totaltimespent)
            #self.variance = sum(map(lambda x: float(x.fixationduration) ** 2, fixations))
            sd = self.features['stddevfixationduration']
            self.variance = sd ** 2 if not math.isnan(sd) else 0

        if seg_event_data != None:
            self.features['numevents'] = len(events)
            self.features['numleftclic'] = len(leftc)
            self.features['numrightclic'] = len(rightc)
            self.features['numdoubleclic'] = len(doublec)
            self.features['leftclicrate'] = float(len(leftc))/length if length>0 else 0
            self.features['rightclicrate'] = float(len(rightc))/length if length>0 else 0
            self.features['doubleclicrate'] = float(len(doublec))/length if length>0 else 0
            self.features['timetofirstleftclic'] = leftc[0].timestamp - starttime if len(leftc) > 0 else -1
            self.features['timetofirstrightclic'] = rightc[0].timestamp - starttime if len(rightc) > 0 else -1
            self.features['timetofirstdoubleclic'] = doublec[0].timestamp - starttime if len(doublec) > 0 else -1
            self.features['timetolastleftclic'] = leftc[-1].timestamp - starttime if len(leftc) > 0 else -1
            self.features['timetolastrightclic'] = rightc[-1].timestamp - starttime if len(rightc) > 0 else -1
            self.features['timetolastdoubleclic'] = doublec[-1].timestamp - starttime if len(doublec) > 0 else -1


        #calculating the transitions to and from this AOI and other active AOIs at the moment
        for aoi in active_aois:
            aid = aoi.aid
            self.features['numtransfrom_%s'%(aid)] = 0

        sumtransfrom = 0
        for i in fixation_indices:
            if i > 0:
                for aoi in active_aois:
                    aid = aoi.aid
                    polyin = aoi.polyin
                    polyout = aoi.polyout
                    key = 'numtransfrom_%s'%(aid)

                    if _fixation_inside_aoi(fixation_data[i-1], polyin, polyout):
                        self.features[key] += 1
                        sumtransfrom += 1

        for aoi in active_aois:
            aid = aoi.aid

            if sumtransfrom > 0:
                val = self.features['numtransfrom_%s'%(aid)]
                self.features['proptransfrom_%s'%(aid)] = float(val) / sumtransfrom
            else:
                self.features['proptransfrom_%s'%(aid)] = 0
        self.total_trans_from = sumtransfrom
        ###end of transition calculation


    def get_features(self, featurelist = None):
        """Returns the list of names and values of features for this AOI_Stat object

        Args:
            featurelist: optional list of features. If equal to None the full set of all features will be returned

        Returns:
            featnames: a list of feature names sorted alphabetically
            featvals: a corresponding list of feature values
            e.g.
            featnames = ['fixationrate', 'length', 'meanabspathangles']
            featvals  = [0.00268522882294', '1529851', '1.60354714212']

        """
        if featurelist == []:
            return [], []
        elif not featurelist:   #all features
            featnames = self.features.keys()
        else:                   #a list was given
            featnames = []
            for name in featurelist:
                if name == 'numtransfrom':
                    featnames += filter(lambda x: x[:12] == 'numtransfrom', self.features.keys())
                elif name == 'proptransfrom':
                    featnames += filter(lambda x: x[:13] == 'proptransfrom', self.features.keys())
                elif name in self.features.keys():
                    featnames.append(name)
                else:
                    raise Exception('AOI %s has no such feature: %s'%(self.aoi.aid, name))

        featnames.sort()

        featvals = map(lambda x: self.features[x], featnames)
#        print featnames

        return featnames, featvals

    def print_(self):
        """Prints the list of features and their values for this AOI_Stat object
        """

        print  "AOI ID:",self.aoi.aid
        fn,fv = self.get_features()
        for i in xrange(len(fn)):
            print fn[i],':',fv[i]
        print


def _fixation_inside_aoi(fixation, polyin, polyout):
    """Helper function that checks if a fixation object is inside the AOI described by external polygon polyin and the internal polygon polyout.

    Fixation object is inside AOI if it is inside polyin but outside polyout

    Args:
        fixation: A Fixation object
        polyin: the external polygon in form of a list of (x,y) tuples
        polyout: the internal polygon in form of a list of (x,y) tuples

    Returns:
        A boolean for whether the Fixation is inside the AOI or not
    """
    return point_inside_polygon(fixation.mappedfixationpointx,
    fixation.mappedfixationpointy, polyin) and not point_inside_polygon(fixation.mappedfixationpointx,
    fixation.mappedfixationpointy, polyout)

def _event_inside_aoi(event, polyin, polyout):
    """Helper function that checks if an event (mouse clic) object is inside the AOI described by external polygon polyin and the internal polygon polyout.

    Event object is inside AOI if it is inside polyin but outside polyout

    Args:
        event: An Event object
        polyin: the external polygon in form of a list of (x,y) tuples
        polyout: the internal polygon in form of a list of (x,y) tuples

    Returns:
        A boolean for whether the Fixation is inside the AOI or not
    """
    if event.event == "LeftMouseClick" or event.event == "RightMouseClick": #keep only mouse clics
        return point_inside_polygon(event.data1, event.data2, polyin) and not point_inside_polygon(event.data1, event.data2, polyout)
    else:
        return False
