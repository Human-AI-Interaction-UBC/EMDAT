"""
UBC Eye Movement Data Analysys Toolkit
Created on 2011-09-30

@author: skardan
"""

import math, geometry
from utils import *
from Segment import *
from copy import deepcopy


class Scene(Segment):
    """A Scene is a class that represent one scene in the experiment.
    
    A Scene is a class that represent one scene in the experiment. The Scene is designed to capture all "Datapoint"s related to a target
    conceptual entity in the experiment. A Scene should have at least one Segment assigned to it. The Scene class is also used to 
    combine multiple "Segment"s and calculate the aggregated statistics for this new entity as a whole. This class is the equivalent
    of scenes as defined in Tobii studio.
    
    Attributes:
        scid: a string containing the Scene ids
        segments: a list of "Segment"s for this Scene
        
    Attributes inherited from Segment:
        alldata: A list of "Datapoint"s for this Scene
        features: A dict with feature names as its keys and feature values as its values 
        completion_time: An integer indicating total duration of the Scene in milliseconds
            minimum is 16 ms (ength of one sample with 60Hz sampling rate (ms)
        start:An integer indicating the Scene's start time in milliseconds
        end: An integer indicating the Scene's end time in milliseconds
        sample_start_ind: An integer indicating the index of the first Datapoint for this Scene in the Participant's list of all "Datapoint"s (all_data) 
        sample_end_ind: An integer indicating the index of the last Datapoint for this Scene in the Participant's list of all "Datapoint"s (all_data)
        fixation_start_ind: An integer indicating the index of the first Fixation for this Scene in the Participant's list of all "Fixation"s (fixation_data)
        fixation_end_ind: An integer indicating the index of the first Fixation for this Scene in the Participant's list of all "Fixation"s (fixation_data)
        numfixations: An integer indicating the number of "Fixation"s in this Scene
        time_gaps: a list of tuples of the form (start, end) indicating the start and end of the gaps of invalid samples in the Segement's samples
        largest_data_gap: An integer indicating the length of largest invalid gap for this Scene in milliseconds
        proportion_valid: A float indicating the proportion of valid samples over all the samples in this Scene
        proportion_valid_fix: A float indicating the proportion of (valid + restored) samples over all the samples in this Scene 
        validity1: a boolean indicating whether this Scene is valid using proportion of valid samples threshold 
        validity2: a boolean indicating whether this Scene is valid using largest acceptable gap threshold
        validity3: a boolean indicating whether this Scene is valid using proportion of (valid + restored) samples threshold
        is_valid: a boolean indicating whether this Scene is considered valid by the validity method indicated by params.VALIDITY_METHOD
        length: An integer indicating total duration of the Scene in milliseconds
        numsamples: An integer indicating total number of samples in the Scene 
        fixation_data: A list of "Fixation"s for this Scene
        fixation_start = fixation_data[0].timestamp
        fixation_end = fixation_data[-1].timestamp
        aoi_data: A list of AOI_Stat objects for relevants "AOI"s for this Scene
        has_aois: A boolean indicating if this Scene has AOI features calculated for it
        
    """

                
    def __init__(self, scid, seglist, all_data, fixation_data, Segments = None, aoilist = None,
                  prune_length= None, require_valid = True, auto_partition = False, rest_pupil_size = 0, export_pupilinfo = False):
        """
        Args:
            scid: A string containing the id of the Scene.
            
            seglist: a list of tuples of the form (segid, start, end) defining the segments
            *Note: this method of defining segments is implemented to make batch processing of
            files defining segments easier
            
            all_data: a list of "Datapoint"s which make up this Scene.
            
            fixation_data: a list of "Fixation"s which make up this Scene.
            
            Segments: a list of "Segment"s which belong to this Scene.
                         
            aoilist: If not None, a list of "AOI"s.
             
            prune_length: If not None, an integer that specifies the time 
                interval (in ms) from the begining of each Segment of this Scene
                which samples are considered in calculations.  This can be used if, 
                for example, you only wish to consider data in the first 
                1000 ms of each Segment. In this case (prune_length = 1000),
                all data beyond the first 1000ms of the start of the "Segment"s
                will be disregarded.
            
            require_valid: a boolean determining whether invalid "Segment"s
                will be ignored when calculating the features or not. default = True 
                
            auto_partition_low_quality_segments: a boolean flag determining whether
                EMDAT should automatically split the "Segment"s which have low sample quality
                into two new ssub "Segment"s discarding the largest invalid sample gap in 
                the "Segment". default = False
            
            rest_pupil_size: rest pupil size for the current scene
            
        Yields:
            a Scene object
        """ 
        
        ########################################
        def partition_segment(new_seg, seg_start, seg_end, rest_pupil_size, export_pupilinfo):
            """ A helper method for splitting a Segment object into new Segments and removing gaps of invalid samples
            
            One way to deal with a low quality Segment is to find the gaps of invalid samples within its "Datapoint"s and 
            splitting the Segment into two Segments one from the beginnning of the Segment to the gap and another from after
            the gap to the end of the Segment. This can be done multiple times resulting multiple "Segment"s with higher
            quality. For example if a Segment S1 started at s1 and ended at e1 and had two invalid gaps between gs1-ge1 and 
            gs2-ge2 milliseconds, this method will generate the following three segments
                SS1: starting at s1 and ending at gs1
                SS2: starting at ge1 and ending at gs2
                SS3: starting at ge2 and ending at e1
            
            Args:
                new_seg: The Segment that is being split
                
                seg_start: An integer showing the start time of the segment in milliseconds
                
                seg_end: An integer showing the end time of the segment in milliseconds 
            
                rest_pupil_size: rest pupil size for the current scene
                
            Returns:
                subsegments: a list of newly generated "Segment"s
                
                samp_inds: a list of tuples of the form (start, end) that detrmines the index of the start and end of each 
                    new Segment in the old Segment's all_data field
                    
                fix_inds: a list of tuples of the form (start, end) that detrmines the index of the start and end of each 
                    new Segment in the old Segment's fixation_data field
            """
            timegaps = new_seg.getgaps()
            subsegments = []
            sub_segid=0
            samp_inds = []
            fix_inds = []
            last_samp_idx = 0
            last_fix_idx = 0
            sub_seg_time_start = seg_start
            for timebounds in timegaps:
                sub_seg_time_end = timebounds[0] #end of this sub_seg is start of this gap
                last_samp_idx, all_start,all_end = get_chunk(all_data, last_samp_idx, sub_seg_time_start, sub_seg_time_end)
                last_fix_idx, fix_start, fix_end = get_chunk(fixation_data, last_fix_idx, sub_seg_time_start, sub_seg_time_end)
                sub_seg_time_start = timebounds[1] #beginning of the next sub_seg is end of this gap
                if fix_end - fix_start>0:
                    try:
                        new_sub_seg = Segment(segid+"_"+str(sub_segid), all_data[all_start:all_end],
                                      fixation_data[fix_start:fix_end], aois=aoilist, prune_length=prune_length, rest_pupil_size = rest_pupil_size, export_pupilinfo=export_pupilinfo)
                    except  Exception as e:
                        warn(str(e))
                        if params.DEBUG:
                            raise
                        else:
                            continue
                else:
                    continue
                subsegments.append(new_sub_seg)
                samp_inds.append((all_start,all_end))
                fix_inds.append((fix_start, fix_end))
                sub_segid +=1
            # handling the last sub_seg
            sub_seg_time_end = seg_end #end of last sub_seg is the end of seg
            last_samp_idx, all_start,all_end = get_chunk(all_data, last_samp_idx, sub_seg_time_start, sub_seg_time_end)
            last_fix_idx, fix_start, fix_end = get_chunk(fixation_data, last_fix_idx, sub_seg_time_start, sub_seg_time_end)
            if fix_end - fix_start>0: #add the last sub_seg
                try:
                    new_sub_seg = Segment(segid, all_data[all_start:all_end],
                                      fixation_data[fix_start:fix_end], aois=aoilist, prune_length=prune_length, rest_pupil_size = rest_pupil_size, export_pupilinfo=export_pupilinfo)
                except  Exception as e:
                    warn(str(e))
                    if params.DEBUG:
                        raise
                    else:
                        new_sub_seg = None
                        
                if new_sub_seg != None:
                    subsegments.append(new_sub_seg)
                    samp_inds.append((all_start,all_end))
                    fix_inds.append((fix_start, fix_end))
            #end of handling the last sub_seg
                
            return subsegments, samp_inds, fix_inds
        ########################################
        
        if len(all_data)<=0:
            raise Exception('A scene with no sample data!')
        if Segments == None:
            self.segments = []
#            print "seglist",seglist
            for (segid, start, end) in seglist:
                print "segid, start, end:",segid, start, end
                if prune_length != None:
				    end = min(end, start+prune_length)
                _, all_start, all_end = get_chunk(all_data, 0, start, end)
                _, fix_start, fix_end = get_chunk(fixation_data, 0, start, end)
                if fix_end - fix_start>0:
                    try:
                        new_seg = Segment(segid, all_data[all_start:all_end],
                                          fixation_data[fix_start:fix_end], aois=aoilist, prune_length=prune_length, rest_pupil_size = rest_pupil_size, export_pupilinfo=export_pupilinfo)
                    except  Exception as e:
                        warn(str(e))
                        if params.DEBUG:
                            raise
                        else:
                            continue
                else:
                    continue
                
                if (new_seg.largest_data_gap > params.MAX_SEG_TIMEGAP) and auto_partition: #low quality segment that needs to be partitioned!
                    new_segs, samp_inds, fix_inds = partition_segment(new_seg, start, end, rest_pupil_size, export_pupilinfo=export_pupilinfo) 
                    for nseg,samp,fix in zip(new_segs, samp_inds, fix_inds):
                            if nseg.length > params.MINSEGSIZE:
                                nseg.set_indices(samp[0],samp[1],fix[0],fix[1])
                                self.segments.append(nseg)
                else:   #good quality segment OR no auto_partition
                    new_seg.set_indices(all_start,all_end,fix_start,fix_end)
                    self.segments.append(new_seg)
        else:
            self.segments = Segments #segments are already generated
        
        self.require_valid_Segments = require_valid
        if require_valid:   #filter out the invalid Segments
            segments = filter(lambda x:x.is_valid,self.segments)
        else:
            segments = self.segments
        if len(segments)==0:
            raise Exception('no segments in scene %s!' %(scid))
        
        fixationlist = []
        sample_list = []
        totalfixations = 0
        firstsegtime = float('infinity')
        firstseg = None 
        for seg in segments:
            sample_st,sample_end,fix_start,fix_end = seg.get_indices()
            if params.DEBUG:
                print "sample_st,sample_end,fix_start,fix_end",sample_st,sample_end,fix_start,fix_end
            sample_list.append(all_data[sample_st:sample_end])
            fixationlist.append(fixation_data[fix_start:fix_end])
            totalfixations += len(fixationlist[-1])
            if seg.start < firstsegtime:
                firstsegtime = seg.start
                firstseg = seg
        
        self.firstseg = firstseg
        self.scid = scid
        self.features = {}
        self.largest_data_gap = maxfeat(self.segments,'largest_data_gap')   #self.segments is used to calculate validity of the scenes instead of segments which is only valid segments
        self.proportion_valid = weightedmeanfeat(self.segments,'numsamples','proportion_valid') #self.segments is used to calculate validity of the scenes instead of segments which is only valid segments
        self.proportion_valid_fix = weightedmeanfeat(self.segments,'numsamples','proportion_valid_fix') #self.segments is used to calculate validity of the scenes instead of segments which is only valid segments
        self.validity1 = self.calc_validity1()
        self.validity2 = self.calc_validity2()
        self.validity3 = self.calc_validity3()
        self.is_valid = self.get_validity()

        self.length = sumfeat(segments,'length')
        if self.length == 0:
            raise Exception('Zero length segments!')
        self.features['numsegments'] = len(segments)
        self.features['length'] = self.length
        self.start = minfeat(segments,'start')
        self.numfixations = sumfeat(segments,'numfixations')
        self.end = maxfeat(segments,'end')
        self.numsamples = sumfeat(segments, 'numsamples')
        self.features['numsamples'] = self.numsamples
        
        self.numfixations = sumfeat(segments, 'numfixations')
        self.features['numfixations'] = self.numfixations
        if prune_length == None:
            if self.numfixations != totalfixations:
                raise Exception('error in fixation count for scene:'+self.scid)
            #warn ('error in fixation count for scene:'+self.scid)
        self.features['fixationrate'] = float(self.numfixations) / self.length
        if self.numfixations > 0:
            self.features['meanfixationduration'] = weightedmeanfeat(segments,'numfixations',"features['meanfixationduration']")
            self.features['stddevfixationduration'] = stddev(map(lambda x: float(x.fixationduration), reduce(lambda x,y: x+y ,fixationlist)))##
            self.features['sumfixationduration'] = sumfeat(segments, "features['sumfixationduration']")
            self.features['fixationrate'] = float(self.numfixations)/self.length
            distances = self.calc_distances(fixationlist)
            abs_angles = self.calc_abs_angles(fixationlist)
            rel_angles = self.calc_rel_angles(fixationlist)
        else:
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
        
        """ calculate pupil dilation features (no rest pupil size adjustments yet)""" 
        
        self.numpupilsizes = sumfeat(segments,'numpupilsizes')
        self.adjvalidpupilsizes = mergevalues(segments, 'adjvalidpupilsizes')
        if self.numpupilsizes > 0: # check if scene has any pupil data
            if export_pupilinfo:
                self.pupilinfo_for_export = mergevalues(segments, 'pupilinfo_for_export') 
            self.features['meanpupilsize'] = weightedmeanfeat(segments, 'numpupilsizes', "features['meanpupilsize']")
            self.features['stddevpupilsize'] = stddev(self.adjvalidpupilsizes)
            self.features['maxpupilsize'] = maxfeat(segments, "features['maxpupilsize']")
            self.features['minpupilsize'] = minfeat(segments, "features['minpupilsize']")
            self.features['startpupilsize'] = segments[0].features['startpupilsize']
            self.features['endpupilsize'] = segments[-1].features['endpupilsize']
        else:
            self.pupilinfo_for_export = [] 
            self.features['meanpupilsize'] = 0
            self.features['stddevpupilsize'] = 0
            self.features['maxpupilsize'] = 0
            self.features['minpupilsize'] = 0
            self.features['startpupilsize'] = 0
            self.features['endpupilsize'] = 0

        """end """

        self.numdistances = sumfeat(segments,'numdistances') #Distance
        self.distances_from_screen = mergevalues(segments, 'distances_from_screen')
        if self.numdistances > 0: # check if scene has any pupil data
            self.features['meandistance'] = weightedmeanfeat(segments, 'numdistances', "features['meandistance']")
            self.features['stddevdistance'] = stddev(self.distances_from_screen)
            self.features['maxdistance'] = maxfeat(segments, "features['maxdistance']")
            self.features['mindistance'] = minfeat(segments, "features['mindistance']")
            self.features['startdistance'] = segments[0].features['startdistance']
            self.features['enddistance'] = segments[-1].features['enddistance']
        else:
            self.features['meandistance'] = 0
            self.features['stddevdistance'] = 0
            self.features['maxdistance'] = 0
            self.features['mindistance'] = 0
            self.features['startdistance'] = 0
            self.features['enddistance'] = 0
        """end """
        
        self.has_aois = False
        if aoilist:
            self.set_aois(segments, aoilist)
        
        self.features['aoisequence'] = self.merge_aoisequences(segments)
            
    def getid(self):
        """Returns the scid for this Scene
        
        Returns: a string conataining the scid for this Scene
        """
        return self.scid
    
    def set_aois(self, segments, aois):
        """Sets the "AOI"s relevant to this Scene
        
        Args:
            segments: a list of "Segment"s which belong to this Scene.

            aois: a list of "AOI"s relevant to this Scene        
        """
        if len(aois) == 0:
            print "no AOI:",self.segid
        self.aoi_data={}
        for seg in segments:
            for aid in seg.aoi_data.keys():
                if seg.aoi_data[aid].isActive:
                    if aid in self.aoi_data:
                        self.aoi_data[aid] = merge_aoistats(self.aoi_data[aid],seg.aoi_data[aid], self.features['length'],self.numfixations)
                    else:
                        self.aoi_data[aid] = deepcopy(seg.aoi_data[aid])
        
        firstsegaois = self.firstseg.aoi_data.keys()            
        for aid in self.aoi_data.keys():
            if aid in firstsegaois:
                self.aoi_data[aid].features['timetofirstfixation'] = deepcopy(self.firstseg.aoi_data[aid].features['timetofirstfixation'])
            else:
                self.aoi_data[aid].features['timetofirstfixation'] = float('inf')
                
        #maois.features['averagetimetofirstfixation'] = ?
        #maois.features['averagettimetolastfixation'] = ?
            self.has_aois = True

    def calc_distances(self, fixdatalists):
        """returns the Euclidean distances between a sequence of "Fixation"s
    
        Args:
            fixdatalists: a list of lists of "Fixation"s
        """
        distances = []
        for fixdata in fixdatalists:
            #print "fixdata", fixdata
            if not(fixdata):
                continue
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
    
    def calc_abs_angles(self, fixdatalists):
        """returns the absolute angles between a sequence of "Fixation"s that build a scan path.
        
        Abosolute angle for each saccade is the angle between that saccade and the horizental axis
    
        Args:
            fixdatalists: a list of lists of "Fixation"s
            
        Returns:
            a list of absolute angles for the saccades formed by the given sequence of "Fixation"s in Radiant
        """
        abs_angles = []
        for fixdata in fixdatalists:
            if not(fixdata):
                continue
            lastx = fixdata[0].mappedfixationpointx
            lasty = fixdata[0].mappedfixationpointy
    
            for i in xrange(1,len(fixdata)):
                x = fixdata[i].mappedfixationpointx
                y = fixdata[i].mappedfixationpointy
                (_, theta) = geometry.vector_difference((lastx,lasty), (x, y))
                abs_angles.append(abs(theta))
                lastx=x
                lasty=y

        return abs_angles

    def calc_rel_angles(self, fixdatalists):
        """returns the relative angles between a sequence of "Fixation"s that build a scan path in Radiant
        
        Relative angle for each saccade is the angle between that saccade and the previous saccade.
    
        Args:
            fixdatalists: a list of lists of  "Fixation"s
            
        Returns:
            a list of relative angles for the saccades formed by the given sequence of "Fixation"s in Radiant
        """
        rel_angles = []
        
        for fixdata in fixdatalists:
            if not(fixdata):
                continue
            lastx = fixdata[0].mappedfixationpointx
            lasty = fixdata[0].mappedfixationpointy
    
            for i in xrange(1, len(fixdata)-1):
                x = fixdata[i].mappedfixationpointx
                y = fixdata[i].mappedfixationpointy
                nextx = fixdata[i+1].mappedfixationpointx
                nexty = fixdata[i+1].mappedfixationpointy
                (_, theta) = geometry.vector_difference((x,y), (lastx, lasty))
                (_, nextheta) = geometry.vector_difference((x,y), (nextx, nexty))
                theta = abs(theta-nextheta)
                rel_angles.append(theta)
                lastx=x
                lasty=y

        return rel_angles

    def merge_aoisequences(self, segments):
        """returns the AOI sequence merged from the AOI sequences in the "Segment"s
        Args:
            segments: a list of "Segment"s which belong to this Scene.
        Returns:
            a list of AOI names that correspond to the sequence of "Fixation"s in this Scene
        """
        sequence = []
        for seg in segments:
            sequence.extend(seg.features['aoisequence'])
        return sequence

    def clean_memory(self):
        for seg in self.segments:
            seg.adjvalidpupilsizes = []
            seg.distances_from_screen = []
        self.adjvalidpupilsizes = []
        self.distances_from_screen = []

def merge_aoistats(main_AOI_Stat,new_AOI_Stat,total_time,total_numfixations):
        """a helper method that updates the AOI_Stat object of this Scene with a new AOI_Stat object
        
        Args:
            main_AOI_Stat: AOI_Stat object of this Scene
            
            new_AOI_Stat: a new AOI_Stat object
            
            total_time:
            
            total_numfixations:
        
        Returns:
            the updated AOI_Sata object
        """   
        maois = main_AOI_Stat
        maois.features['numfixations'] += new_AOI_Stat.features['numfixations']
        maois.features['longestfixation'] = max(maois.features['longestfixation'],new_AOI_Stat.features['longestfixation'])
        maois.features['totaltimespent'] += + new_AOI_Stat.features['totaltimespent'] 
        maois.features['proportiontime'] = float(maois.features['totaltimespent'])/total_time
        maois.features['proportionnum'] = float(maois.features['numfixations'])/total_numfixations
        if maois.features['totaltimespent']>0: 
            maois.features['fixationrate'] = float(maois.features['numfixations'])/maois.features['totaltimespent']
        else:
            maois.features['fixationrate'] = 0.0
                
                
            
        #calculating the transitions to and from this AOI and other active AOIs at the moment
        new_AOI_Stat_transition_aois = filter(lambda x: x.startswith(('numtransto_','numtransfrom_')),new_AOI_Stat.features.keys())
        if params.DEBUG:
            print "segement's transition_aois",new_AOI_Stat_transition_aois
            
        maois.total_tans_to += new_AOI_Stat.total_tans_to       #updating the total number of transition to this AOI
        maois.total_tans_from += new_AOI_Stat.total_tans_from   #updating the total number of transition from this AOI
        for feat in new_AOI_Stat_transition_aois:
            if feat in maois.features:
                maois.features[feat] += new_AOI_Stat.features[feat]
            else:
                maois.features[feat] = new_AOI_Stat.features[feat]
#            if feat.startswith('numtransto_'):
#                sumtransto += maois.features[feat]
#            else:
#                sumtransfrom += maois.features[feat]
    
    
# updating the proportion tansition features based on new transitions to and from this AOI        
        maois_transition_aois = filter(lambda x: x.startswith(('numtransto_','numtransfrom_')),maois.features.keys()) #all the transition features for this AOI should be aupdated even if they are not active for this segment
        for feat in maois_transition_aois:
            if feat.startswith('numtransto_'):
                aid = feat.lstrip('numtransto_')
                if maois.total_tans_to > 0:

                    maois.features['proptransto_%s'%(aid)] = float(maois.features[feat]) / maois.total_tans_to
                else:
                    maois.features['proptransto_%s'%(aid)] = 0
            else:
                aid = feat.lstrip('numtransfrom_')
                if maois.total_tans_from > 0:
                    
                    maois.features['proptransfrom_%s'%(aid)] = float(maois.features[feat]) / maois.total_tans_from
                else:
                    maois.features['proptransfrom_%s'%(aid)] = 0
        ###endof trnsition calculation
        return maois

def weightedmeanfeat(obj_list, totalfeat,ratefeat):
    """a helper method that calculates the weighted average of a target feature over a list of Segments
    
    Args:
        obj_list: a list of Segments which all have a numeric field for which the weighted average is calculated 
        
        totalfeat: a string containing the name of the feature that has the total value of the target feature 
        
        ratefeat: a string containing the name of the feature that has the rate value of the target feature
    
    Returns:
        the weighted average of the ratefeat over the Segments
    """
    num_valid = float(0)
    num = 0

    for obj in obj_list:
        t = eval('obj.'+totalfeat)
        num_valid += t * eval('obj.'+ratefeat)
        num += t
    if num != 0:
        return num_valid / num
    return 0
    

def sumfeat(obj_list, feat):
    """a helper method that calculates the sum of a target feature over a list of objects
    
    Args:
    
        obj_list: a list of objects
        
        feat: a string containing the name of the target feature
    
    Returns:
        the sum of the target feature over the given list of objects
    """
    sum = 0
    for obj in obj_list:
        sum += eval('obj.'+feat)
    return sum

def minfeat(obj_list, feat):
    """a helper method that calculates the min of a target feature over a list of objects
    
    Args:
    
        obj_list: a list of objects
        
        feat: a string containing the name of the target feature
    
    Returns:
        the min of the target feature over the given list of objects
    """
    min = float('+infinity')
    for obj in obj_list:
        val = eval('obj.'+feat)
        if min > val:
            min = val
    return min     
    
def maxfeat(obj_list, feat):
    """a helper method that calculates the max of a target feature over a list of objects
    
    Args:
    
        obj_list: a list of objects
        
        feat: a string containing the name of the target feature
    
    Returns:
        the max of the target feature over the given list of objects
    """
    max = float('-infinity')
    for obj in obj_list:
        val = eval('obj.'+feat)
        if max < val:
            max = val
    return max   
  
def mergevalues(obj_list, field):
    """a helper method that merges lists of values stored in field 
    
    Args:
    
        obj_list: a list of objects
        
        field: name of a field that contains a list of values (string)
    
    Returns:
        a list formed by merging corresponding lists from collection of subjects
    """
    mergedlist = []
    for obj in obj_list:
        mergedlist.extend(eval('obj.'+ field))
    return mergedlist
    