"""
UBC Eye Movement Data Analysis Toolkit
The Generic Area of Interest Classes
Created on 2011-08-26

@author: skardan

In EMDAT, the bounderies of an Area of Interest (AOI) is defined as a polygon on the screen. You can 
optionally define a second polygone inside the first polygone to be excluded from an AOI.
An AOI can be always active (a global AOI) or can be active during certain time intervals.
In order to calculate the features for an AOI instance, you need to create an AOI_Stat instance and
map it to a target AOI object by passing it to the AOI_Stat constructor. The resulting AOI_Stat
will calculate all features related to the given AOI and store them for later reference 
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
        if params.DEBUG:
            print "in:",self.aid
        ovelap_part = []
        if self.timeseq:
            for intr in self.timeseq:
                if (start>=intr[0] and start<intr[1])or(end>intr[0] and end<=intr[1]):
                    if (start>=intr[0] and end<=intr[1]):
                        ovelap_part=[]
                    else:
                        if params.DEBUG:
                            print "partial:",start,end,":",intr[0],intr[1]
                        ovstart = max(start,intr[0])
                        ovend  = min(end,intr[1])
                        ovelap_part = [ovstart,ovend]
                    return True, ovelap_part
                elif (start<intr[0] and start<intr[1])and(end>intr[0] and end>intr[1]):
                    warn("Incorrect definition of Dynamic AOI and Segments, AOI info not calculated for AOI:"+self.aid)

            return False, [] #not active
        else:
            return True, [] #global AOI
    
                   
class AOI_Stat():
    """Methods of AOI_Stat calculate and store all features related to the given AOI object
    """

    def __init__(self,aoi,seg_fixation_data, starttime, endtime, active_aois):
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
        self.aoi
        if not(self.isActive):
            return
        self.isActive = True
        
        if partition:
            if params.DEBUG:
                print "partition",partition
            _,st,en = get_chunk(seg_fixation_data, 0, partition[0],partition[1])
            fixation_data = seg_fixation_data[st:en]
            if params.DEBUG:
                print "len(seg_fixation_data)",seg_fixation_data
                print "len(fixation_data)",fixation_data
        else:  #global AOI (alaways active)
            fixation_data = seg_fixation_data 
        fixation_indices = filter(lambda i: _fixation_inside_aoi(fixation_data[i],self.aoi.polyin, self.aoi.polyout), range(len(fixation_data)))

        fixations = map(lambda i: fixation_data[i], fixation_indices)
    
        self.features = {}

        numfixations = len(fixations)
        self.features['numfixations'] = numfixations
        self.features['longestfixation'] = -1
        self.features['timetofirstfixation'] = -1
        self.features['timetolastfixation'] = -1
        self.features['proportionnum'] = 0
        totaltimespent = sum(map(lambda x: x.fixationduration, fixations))
        self.features['totaltimespent'] = totaltimespent 
        
        self.features['proportiontime'] = float(totaltimespent)/(endtime - starttime)
        if numfixations > 0:
            self.features['longestfixation'] = max(map(lambda x: x.fixationduration,
            fixations))
            self.features['timetofirstfixation'] = fixations[0].timestamp - starttime
            self.features['timetolastfixation'] = fixations[-1].timestamp - starttime
            self.features['proportionnum'] = float(numfixations)/len(fixation_data)
            self.features['fixationrate'] = numfixations / float(totaltimespent)
        else:
            self.features['longestfixation'] = 0
            self.features['timetofirstfixation'] = 0
            self.features['timetolastfixation'] = 0
            self.features['proportionnum'] = 0
            self.features['fixationrate'] = 0
                
                
            
        #calculating the transitions to and from this AOI and other active AOIs at the moment
        for aoi in active_aois:
            aid = aoi.aid
            self.features['numtransto_%s'%(aid)] =0
            self.features['numtransfrom_%s'%(aid)] = 0

        sumtransto = 0
        sumtransfrom = 0
        for i in fixation_indices:
            if i > 0:
                for aoi in active_aois:
                    aid = aoi.aid
                    polyin = aoi.polyin
                    polyout = aoi.polyout
                    key = 'numtransfrom_%s'%(aid)
                    #self.features[key] = 0 #????? Samad
                    if _fixation_inside_aoi(fixation_data[i-1], polyin, polyout):
                        self.features[key] += 1
                        sumtransfrom += 1
            if i < len(fixation_data)-2:
                for aoi in active_aois:
                    aid = aoi.aid
                    polyin = aoi.polyin
                    polyout = aoi.polyout
                    key = 'numtransto_%s'%(aid)
                    #self.features[key] = 0 #????? Samad
                    if _fixation_inside_aoi(fixation_data[i+1], polyin, polyout):
                        self.features[key] += 1
                        sumtransto += 1

        for aoi in active_aois:
            aid = aoi.aid
            if sumtransto > 0:
                val = self.features['numtransto_%s'%(aid)]
                self.features['proptransto_%s'%(aid)] = float(val) / sumtransto
            else:
                self.features['proptransto_%s'%(aid)] = 0

            if sumtransfrom > 0:
                val = self.features['numtransfrom_%s'%(aid)]
                self.features['proptransfrom_%s'%(aid)] = float(val) / sumtransfrom
            else:
                self.features['proptransfrom_%s'%(aid)] = 0
        self.total_trans_to = sumtransto
        self.total_trans_from = sumtransfrom
        ###endof trnsition calculation
        #Daria: auxiliary features
        #needed for merging TextNormal and TextRestrictedInput
        self.features['sumtransfrom']=sumtransfrom #sum of transitions from all other AOIs to the current
        self.features['sumtransto']=sumtransto #sum of transitions to all other AOIs from the current
        
        self.features['fixationsonscreen']= len(fixation_data)#total number of fixations on screen when aoi was active
        if self.isActive: 
            self.features['proportionnum_dynamic'] = self.features['proportionnum']
            if (partition is not None) and (partition != []):#if partition is performed, we are looking for time interval when AOI was active
                self.features['timeonscreen'] = partition[1]-partition[0] # duration of AOI being available during the current segment
                self.features['proportiontime_dynamic'] = float(totaltimespent)/(partition[1]-partition[0])
                #print self.aoi.aid + ": duration of partitioned AOI is " + str(partition[1]-partition[0])
            else:
                self.features['timeonscreen'] = endtime - starttime
                self.features['proportiontime_dynamic'] = float(totaltimespent)/(endtime-starttime)
                

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
                if name == 'numtransto':
                    featnames += filter(lambda x: x[:10] == 'numtransto', self.features.keys())
                elif name == 'numtransfrom':
                    featnames += filter(lambda x: x[:12] == 'numtransfrom', self.features.keys())
                elif name == 'proptransfrom':
                    featnames += filter(lambda x: x[:11] == 'proptransto', self.features.keys())
                elif name == 'proptransto':
                    featnames += filter(lambda x: x[:13] == 'proptransfrom', self.features.keys())
                elif name in self.features.keys():
                    featnames.append(name)
                else:
                    raise Exception('AOI %s has no such feature: %s'%(self.aoi.aid,
                    name))

        featnames.sort()

        featvals = map(lambda x: self.features[x], featnames)

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
         
