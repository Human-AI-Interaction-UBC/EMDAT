"""
UBC Eye Movement Data Analysis Toolkit
Created on 2011-08-26

@author: skardan


"""
import params
import geometry
from AOI import *
from warnings import warn



class Segment():
    """A Segment is a class that represents the smallest unit of aggregated eye data samples with a conceptual meaning.

    A segment is the smallest unit of aggregated eye data samples that has conceptual meaning. This class is the equivalent
    of segments as defined in Tobii studio. 
    
    Attributes:
        segid: A string containing the id of the Segment.
        alldata: A list of "Datapoint"s for this Segment
        features: A dict with feature names as its keys and feature values as its values 
        completion_time: An integer indicating total duration of the Segment in milliseconds
            minimum is 16 ms (length of one sample with 60Hz sampling rate (ms))
        start: An integer indicating the Segment's start time in milliseconds
        end: An integer indicating the Segment's end time in milliseconds
        sample_start_ind: An integer indicating the index of the first Datapoint for this Segment in the Participant's list of all "Datapoint"s (all_data) 
        sample_end_ind: An integer indicating the index of the last Datapoint for this Segment in the Participant's list of all "Datapoint"s (all_data)
        fixation_start_ind: An integer indicating the index of the first Fixation for this Segment in the Participant's list of all "Fixation"s (fixation_data)
        fixation_end_ind: An integer indicating the index of the first Fixation for this Segment in the Participant's list of all "Fixation"s (fixation_data)
        numfixations: An integer indicating the number of "Fixation"s in this Segment
        time_gaps: a list of tuples of the form (start, end) indicating the start and end of the gaps of invalid samples in the Segement's samples
        largest_data_gap: An integer indicating the length of largest invalid gap for this Segment in milliseconds
        proportion_valid: A float indicating the proportion of valid samples over all the samples in this Segment
        proportion_valid_fix: A float indicating the proportion of (valid + restored) samples over all the samples in this Segment 
        validity1: a boolean indicating whether this Segment is valid using proportion of valid samples threshold 
        validity2: a boolean indicating whether this Segment is valid using largest acceptable gap threshold
        validity3: a boolean indicating whether this Segment is valid using proportion of (valid + restored) samples threshold
        is_valid: a boolean indicating whether this Segment is considered valid by the validity method indicated by params.VALIDITY_METHOD
        length: An integer indicating total duration of the Segment in milliseconds
        numsamples: An integer indicating total number of samples in the Segment 
        fixation_data: A list of "Fixation"s for this Segment
        fixation_start: timestamp of the first entry from list of "Fixation"s for this Segment
        fixation_end: timestamp of the last entry from list of "Fixation"s for this Segment
        aoi_data: A list of AOI_Stat objects for relevant "AOI"s for this Segment
        has_aois: A boolean indicating if this Segment has AOI features calculated for it
        
    """
    def __init__(self, segid, all_data, fixation_data, aois = None, prune_length = None):
        """
        Args:
            segid: A string containing the id of the Segment.
            
            all_data: a list of "Datapoint"s which make up this Segment.
            
            fixation_data: a list of "Fixation"s which make up this Segment.
            
            aois: a list of "AOI"s relevant to this Segment.
         
            prune_length: If not None, an integer that specifies the time interval (in ms) from the beginning of each segment in which
                samples are considered in calculations.  This can be used if, for example, you only wish to consider data in the first 
                1000 ms of each segment. In this case (prune_length = 1000), all data beyond the first 1000ms of the start of the segments
                will be disregarded.
                
        Yields:
            a Segment object
        """
        self.segid = segid
        #self.alldata = all_data
        self.features = {}
        self.completion_time = all_data[-1].timestamp - all_data[0].timestamp
        if self.completion_time == 0:
            raise Exception("Zero length segment")
#            self.completion_time = 16 #length of one sample with 60Hz sampling rate (ms)
#        for d in all_data:
#            d.set_segid(segid)
        self.features['completion_time'] = self.completion_time
        self.start = all_data[0].timestamp
        self.numfixations = len(fixation_data)
        self.time_gaps = []
        self.largest_data_gap = self.calc_largest_validity_gap(all_data)
        self.proportion_valid = self.calc_validity_proportion(all_data)
        self.proportion_valid_fix = self.calc_validity_fixation(all_data)
        self.validity1 = self.calc_validity1()
        self.validity2 = self.calc_validity2()
        self.validity3 = self.calc_validity3()
        self.is_valid = self.get_validity()
        if prune_length:
            all_data = filter(lambda x: x.timestamp <= self.start +
            prune_length, all_data)
            fixation_data = filter(lambda x: x.timestamp <= self.start +
            prune_length, fixation_data)
        self.end = all_data[-1].timestamp
        self.length = self.end - self.start
        self.features['length'] = self.end - self.start
        self.numsamples = self.calc_num_samples(all_data)
        self.features['numsamples'] = self.numsamples
        self.numfixations = len(fixation_data)
#        for f in fixation_data:
#            f.set_segid(segid)
        self.features['numfixations'] = self.numfixations
        self.features['fixationrate'] = float(self.numfixations) / self.length
        if self.numfixations > 0:
            self.fixation_start = fixation_data[0].timestamp
            self.fixation_end = fixation_data[-1].timestamp
            self.features['meanfixationduration'] = mean(map(lambda x: float(x.fixationduration), fixation_data))
            self.features['stddevfixationduration'] = stddev(map(lambda x: float(x.fixationduration), fixation_data))
            self.features['sumfixationduration'] = sum(map(lambda x: x.fixationduration, fixation_data))
            self.features['fixationrate'] = float(self.numfixations)/self.length
            distances = self.calc_distances(fixation_data)
            abs_angles = self.calc_abs_angles(fixation_data)
            rel_angles = self.calc_rel_angles(fixation_data)
        else:
            self.fixation_start = -1
            self.fixation_end = -1            
            self.features['meanfixationduration'] = 0
            self.features['stddevfixationduration'] = 0
            self.features['sumfixationduration'] = 0
            self.features['fixationrate'] = 0
            distances = []
        if len(distances) > 0:
            self.features['meanpathdistance'] = mean(distances)
            self.features['sumpathdistance'] = sum(distances)
            self.features['stddevpathdistance'] = stddev(distances)
            self.features['eyemovementvelocity'] = self.features['sumpathdistance']/self.length
            self.features['sumabspathangles'] = sum(abs_angles)
            self.features['meanabspathangles'] = mean(abs_angles)
            self.features['stddevabspathangles'] = stddev(abs_angles)
            self.features['sumrelpathangles'] = sum(rel_angles)
            self.features['meanrelpathangles'] = mean(rel_angles)
            self.features['stddevrelpathangles'] = stddev(rel_angles)
        else:
            self.features['meanpathdistance'] = 0
            self.features['sumpathdistance'] = 0
            self.features['stddevpathdistance'] = 0
            self.features['sumabspathangles'] = 0
            self.features['meanabspathangles']= 0
            self.features['stddevabspathangles']= 0
            self.features['sumrelpathangles'] = 0
            self.features['meanrelpathangles']= 0
            self.features['stddevrelpathangles'] = 0
        self.has_aois = False
        if aois:
            self.set_aois(aois,fixation_data)
    def set_indices(self,sample_st,sample_end,fix_st,fix_end):
        """Sets the index features
        
        Args:
            sample_st: An integer indicating the index of the first Datapoint for this Segment in the Participant's list of all "Datapoint"s (all_data) 
            sample_end: An integer indicating the index of the last Datapoint for this Segment in the Participant's list of all "Datapoint"s (all_data)
            fix_st: An integer indicating the index of the first Fixation for this Segment in the Participant's list of all "Fixation"s (fixation_data)
            fix_st: An integer indicating the index of the first Fixation for this Segment in the Participant's list of all "Fixation"s (fixation_data)        
        """
        self.sample_start_ind = sample_st
        self.sample_end_ind = sample_end
        self.fixation_start_ind = fix_st
        self.fixation_end_ind = fix_end

    def get_indices(self):
        """Returns the index features
        
        Returns:
            An integer indicating the index of the first Datapoint for this Segment in the Participant's list of all "Datapoint"s (all_data) 
            An integer indicating the index of the last Datapoint for this Segment in the Participant's list of all "Datapoint"s (all_data)
            An integer indicating the index of the first Fixation for this Segment in the Participant's list of all "Fixation"s (fixation_data)
            An integer indicating the index of the first Fixation for this Segment in the Participant's list of all "Fixation"s (fixation_data)   
            
        Raises:
            Exception: An exception is thrown if the values are read before initialization
        """
        if self.sample_start_ind != None:
            return self.sample_start_ind, self.sample_end_ind, self.fixation_start_ind, self.fixation_end_ind 
        raise Exception ('The indices values are accessed before setting the initial value in segement:'+self.segid+'!')

    def set_aois(self, aois, fixation_data):
        """Sets the relevant "AOI"s for this Segment
        
        Args:
            fixation_data: The list of "Fixation"s which make up this Segment
            aois: a list of "AOI"s relevant to this Segment
        """
        if len(aois) == 0:
            warn("no AOIs passed to segment:"+self.segid)
        active_aois=[]
        for aoi in aois:
            #print "checking:",aoi.aid
            if aoi.is_active(self.fixation_start, self.fixation_end):
                active_aois.append(aoi)
        if not(active_aois):
            msg = "no active AOIs passed to segment:%s start:%d end:%d" %(self.segid,self.start,self.end)
            warn(msg)
        self.aoi_data = {}
        for aoi in active_aois:
            aoistat = AOI_Stat(aoi, fixation_data, self.start, self.end, active_aois)
            self.aoi_data[aoi.aid] = aoistat
            self.has_aois = True

    def calc_validity_proportion(self, all_data):
        """Calculates the proportion of "Datapoint"s which are valid.
        
        Args:
            all_data: The list of "Datapoint"s which make up this Segement
            
        Returns:
            A float indicating the proportion of valid samples over all the samples in this Segment
        """
        num_valid = float(0)
        num = 0

        for d in all_data:
            #if d.stimuliname == 'ScreenRec':
            if d.stimuliname != '':
                num += 1
                if d.is_valid:
                    num_valid += 1
#            else:
#                print "###",d.event, d.data1
        if num==0:
            return 0.0
        else:
            return num_valid / num

    def calc_largest_validity_gap(self, all_data):
        """Calculates the largest gap of invalid samples in the "Datapoint"s for this Segment.
        
        Args:
            all_data: The list of "Datapoint"s which make up this Segement
            
        Returns:
            An integer indicating the length of largest invalid gap for this Segment in milliseconds  
        """
        if self.numfixations == 0:
            return all_data[-1].timestamp - all_data[0].timestamp
        self.time_gaps = []
        max = 0
        dindex = 0
        datalen = len(all_data)
        while dindex < datalen:
            d = all_data[dindex]
            while d.is_valid and (dindex < datalen-1):
                dindex += 1
                d = all_data[dindex]
            if not(d.is_valid):
                gap_start = d.timestamp
                while not(d.is_valid) and (dindex < datalen-1):
                    dindex += 1
                    d = all_data[dindex]
                if d.timestamp - gap_start > max:
                    max = d.timestamp - gap_start
                if d.timestamp - gap_start > params.MAX_SEG_TIMEGAP:
                    self.time_gaps.append((gap_start,d.timestamp))
            dindex += 1

        return max

    def getgaps(self):
        """Returns the list of invalid gaps for this Segment
        
        Args:
            a list of invalid gaps for this Segment
        """
        return self.time_gaps

    def calc_validity_fixation(self, all_data):
        """Calculates the proportion of (valid + restored) "Datapoint"s over all "Datapoint"s of the Segment.
        
        Restored samples are the samples which are not valid but they are part of a Fixation.
        The idea is that if the user was looking at a certain point and then we loose the eye data for 
        a short period of time and afterwards the user is looking at the same point we can assume that user
        was looking at that same point during that period. 
        
        Args:
            all_data: The list of "Datapoint"s which make up this Segement
            
        Returns:
            A float indicating the proportion of (valid + restored) samples over all the samples in this Segment
        """
        if self.numfixations == 0:
            return 0.0
        num_valid = float(0)
        num = 0

        for d in all_data:
            #if d.stimuliname == 'ScreenRec':
            if d.stimuliname != '':
                num += 1
                if d.fixationindex!=None:
                    num_valid += 1.0
#            else:
#                print "###",d.event, d.data1
        if num==0:
            return 0.0
        else:
            return num_valid / num
        
    def calc_validity1(self, threshold = params.VALID_PROP_THRESH):
        """Returns a boolean indicating whether this Segment is valid using proportion of valid samples threshold
        
        Args:
            threshold: the minimum proportion of valid samples for a Segment or Scene to be 
                considered valid. By default set to value VALID_PROP_THRESH from module params.py 
        """
        return self.proportion_valid > threshold

    def calc_validity2(self, threshold = params.VALID_TIME_THRESH):
        """Returns a boolean indicating whether this Segment is valid using largest acceptable gap threshold
        """
        return self.largest_data_gap <= threshold

       
    def calc_validity3(self, threshold = params.VALID_PROP_THRESH):
        """Returns a boolean indicating whether this Segment is valid using proportion of (valid + restored) samples threshold
        """
        return self.proportion_valid_fix > threshold
    
    def get_validity(self):
        """Determines if this Segment is valid with the given validity method set in params.VALIDITY_METHOD
        
        Returns:
            A boolean indicating whether this Segment is valid
        """
        if params.VALIDITY_METHOD == 1:
            return self.validity1
        elif params.VALIDITY_METHOD == 2:
            return self.validity2
        elif params.VALIDITY_METHOD == 3:
            return self.validity3
    
    def calc_distances(self, fixdata):
        """returns the Euclidean distances between a sequence of "Fixation"s
    
        Args:
            fixdata: a list of "Fixation"s
        """
        distances = []
        lastx = fixdata[0].mappedfixationpointx
        lasty = fixdata[0].mappedfixationpointy

        for i in xrange(1, len(fixdata)):
            x = fixdata[i].mappedfixationpointx
            y = fixdata[i].mappedfixationpointy
            dist = math.sqrt((x-lastx)**2 + (y-lasty)**2)
            distances.append(dist)
            lastx = x
            lasty = y

        return distances

    def calc_abs_angles(self, fixdata):
        """returns the absolute angles between a sequence of "Fixation"s that build a scan path.
        
        Abosolute angle for each saccade is the angle between that saccade and the horizental axis
    
        Args:
            fixdata: a list of "Fixation"s
            
        Returns:
            a list of absolute angles for the saccades formed by the given sequence of "Fixation"s in Radiant
        """
        abs_angles = []
        lastx = fixdata[0].mappedfixationpointx
        lasty = fixdata[0].mappedfixationpointy

        for i in xrange(1,len(fixdata)):
            x = fixdata[i].mappedfixationpointx
            y = fixdata[i].mappedfixationpointy
            (dist, theta) = geometry.vector_difference((lastx,lasty), (x, y))
            abs_angles.append(abs(theta))
            lastx=x
            lasty=y

        return abs_angles

    def calc_rel_angles(self, fixdata):
        """returns the relative angles between a sequence of "Fixation"s that build a scan path in Radiant
        
        Relative angle for each saccade is the angle between that saccade and the previous saccade.
    
        Args:
            fixdata: a list of "Fixation"s
            
        Returns:
            a list of relative angles for the saccades formed by the given sequence of "Fixation"s in Radiant
        """
        rel_angles = []
        lastx = fixdata[0].mappedfixationpointx
        lasty = fixdata[0].mappedfixationpointy

        for i in xrange(1, len(fixdata)-1):
            x = fixdata[i].mappedfixationpointx
            y = fixdata[i].mappedfixationpointy
            nextx = fixdata[i+1].mappedfixationpointx
            nexty = fixdata[i+1].mappedfixationpointy
            (dist, theta) = geometry.vector_difference((x,y), (lastx, lasty))
            (dist, nextheta) = geometry.vector_difference((x,y), (nextx, nexty))
            theta = abs(theta-nextheta)
            rel_angles.append(theta)
            lastx=x
            lasty=y

        return rel_angles

    def calc_num_samples(self, all_data):
        """Returns the number of samples in the Segment
        
        Args:
            all_data: a list of "Datapoint"s which make up this Segment.
            
        Returns:
            An integer determining the number of samples in the Segment
        
        """
        num = 0
        for d in all_data:
            if d.stimuliname != '':
                num += 1
        return num
    
    def getid(self):
        """Returns the segid for this Segment
        
        Returns: a string conataining the segid for this Segment
        """
        return self.segid
    
    def get_features(self, featurelist = None, aoifeaturelist = None, aoifeaturelabels = None):
        """Returns feature names and their values for this Segment
        
        Args:
            featurelist: if not None, a list containing the name of features to be returned. If this is None all features will be returned
            aoifeaturelist: if not None, a list of features to be returned for each of the "AOI"s relevant to this Segment. 
            aoifeaturelabels: if not None, a list of AOI related features to be returned.
            *Note: while aoifeaturelist is a subset of features that will be returned for all relevant "AOI"s, aoifeaturelabels contains 
            the exact AOI feature name, i.e., a feature of the form: [AOI name]_[feature name]
            For example if an AOI called 'graph' is releveant to this Segment, aoifeaturelabels may contain 'graph_fixationrate'  
            
        Returns:
            featnames: a list of feature names sorted alphabetically
            featvals: a corrsponding list of feature values
            e.g.
            featnames = ['fixationrate', 'length', 'meanabspathangles']
            featvals  = [0.00268522882294', '1529851', '1.60354714212']
        
        """ 
        if featurelist == []:
            featnames = []
        elif not featurelist:       #include all features
            featnames = self.features.keys()
        else:                       #a list of features was given
            featnames = []
            for name in featurelist:
                if name in self.features.keys():
                    featnames.append(name)
                else:
                    raise Exception('Segement %s has no such feature: %s'%(self.getid(),name))

        featnames.sort()

        featvals = map(lambda x: self.features[x], featnames)

        if self.has_aois:
            for aid, aoi in self.aoi_data.iteritems():
                if aoifeaturelabels:    #an exact list of aoifeatures was given 
                    anames, avals = aoi.get_features()
                    anames = map(lambda x: '%s_%s'%(aid, x), anames)
                    featval = zip(anames,avals)
                    newfeatval = filter(lambda x: x[0] in aoifeaturelabels,featval)
                    anames = []
                    avals = []
                    for fn,fv in newfeatval:
                        anames.append(fn)
                        avals.append(fv)
                    if featnames:                    
                        featnames += anames
                        featvals += avals                   
                else:                   #a list of features for each AIO was given
                    anames, avals = aoi.get_features(aoifeaturelist)
                    anames = map(lambda x: '%s_%s'%(aid, x), anames)
                    featnames += anames
                    featvals += avals

        return featnames, featvals
    
    def print_(self):
        """Ourputs all feature names and their values for this Segment on the console        
        """ 
        print"ID", self.getid()
        print"start",self.start 
        print"end",self.end
        print"is_valid",self.is_valid
        print
#        featurelist =["completion_time","numfixations","length","numsamples"]
#        if self.features['numfixations'] > 0:
#            featurelist.extend(["meanfixationduration","stddevfixationduration","sumfixationduration","fixationrate"])
#        
#        featurelist.extend(["meanpathdistance","sumpathdistance","stddevpathdistance","sumabspathangles","meanabspathangles","stddevabspathangles","sumrelpathangles","meanrelpathangles","stddevrelpathangles"])

        fn,fv = self.get_features()
        for i in xrange(len(fn)):
            print fn[i],':',fv[i]
        print
    

        
