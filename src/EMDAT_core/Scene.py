"""
UBC Eye Movement Data Analysis Toolkit (EMDAT), Version 3
Created on 2011-09-30

Scene class: capture all "Datapoint"s related to a target
conceptual entity in the experiment.

Authors: Samad Kardan (creator), Sebastien Lalle.
Institution: The University of British Columbia.
"""

import math, EMDAT_core.geometry
from EMDAT_core.utils import *
from EMDAT_core.Segment import *
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


    def __init__(self, scid, seglist, all_data, fixation_data, saccade_data = None, event_data = None, Segments = None, aoilist = None,
                  prune_length= None, require_valid = True, auto_partition = False, rest_pupil_size = 0, export_pupilinfo = False):
        """
        Args:
            scid: A string containing the id of the Scene.

            seglist: a list of tuples of the form (segid, start, end) defining the segments
            *Note: this method of defining segments is implemented to make batch processing of
            files defining segments easier

            all_data: a list of "Datapoint"s which make up this Scene.

            fixation_data: a list of "Fixation"s which make up this Scene.

            saccade_data: If not None, a list of "Saccade"s which make up this Scene.

            event_data: If not None, a list of "Event"s which make up this Scene.

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

            auto_partition: a boolean flag determining whether
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

                sac_inds: a list of tuples of the form (start, end) that detrmines the index of the start and end of each
                    new Segment in the old Segment's saccade_data field

                event_inds: a list of tuples of the form (start, end) that detrmines the index of the start and end of each
                    new Segment in the old Segment's event_data field
            """
            timegaps = new_seg.getgaps()
            subsegments = []
            sub_segid = 0
            samp_inds = []
            fix_inds = []
            saccade_inds = []
            event_inds = []
            last_samp_idx = 0
            last_fix_idx = 0
            last_sac_idx = 0
            last_event_idx = 0
            sub_seg_time_start = seg_start
            for timebounds in timegaps:
                sub_seg_time_end = timebounds[0] #end of this sub_seg is start of this gap
                last_samp_idx, all_start,all_end = get_chunk(all_data, last_samp_idx, sub_seg_time_start, sub_seg_time_end)
                last_fix_idx, fix_start, fix_end = get_chunk(fixation_data, last_fix_idx, sub_seg_time_start, sub_seg_time_end)
                if saccade_data != None:
                    last_sac_idx, sac_start, sac_end = get_chunk(saccade_data, last_sac_idx, sub_seg_time_start, sub_seg_time_end)
                    saccade_data_in_part = saccade_data[sac_start:sac_end]
                else:
                    saccade_data_in_part = None
                if event_data != None:
                    last_event_idx, event_start, event_end = get_chunk(event_data, last_event_idx, sub_seg_time_start, sub_seg_time_end)
                    event_data_in_part = event_data[event_start:event_end]
                else:
                    event_data_in_part = None

                sub_seg_time_start = timebounds[1] #beginning of the next sub_seg is end of this gap
                if fix_end - fix_start>0:
                    try:
                        new_sub_seg = Segment(segid+"_"+str(sub_segid), all_data[all_start:all_end], fixation_data[fix_start:fix_end], saccade_data=saccade_data_in_part,
                                      event_data=event_data_in_part, aois=aoilist, prune_length=prune_length, rest_pupil_size = rest_pupil_size, export_pupilinfo = export_pupilinfo)
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
                if saccade_data != None:
                    saccade_inds.append((sac_start, sac_end))
                if event_data != None:
                    event_inds.append((event_start, event_end))
                sub_segid +=1

            # handling the last sub_seg
            sub_seg_time_end = seg_end #end of last sub_seg is the end of seg
            last_samp_idx, all_start,all_end = get_chunk(all_data, last_samp_idx, sub_seg_time_start, sub_seg_time_end)
            last_fix_idx, fix_start, fix_end = get_chunk(fixation_data, last_fix_idx, sub_seg_time_start, sub_seg_time_end)
            if saccade_data != None:
                last_sac_idx, sac_start, sac_end = get_chunk(saccade_data, last_sac_idx, sub_seg_time_start, sub_seg_time_end)
                saccade_data_in_part = saccade_data[sac_start:sac_end]
            else:
                saccade_data_in_part = None
            if event_data != None:
                last_event_idx, event_start, event_end = get_chunk(event_data, last_event_idx, sub_seg_time_start, sub_seg_time_end)
                event_data_in_part = event_data[event_start:event_end]
            else:
                event_data_in_part = None
            if fix_end - fix_start>0: #add the last sub_seg
                try:
                    new_sub_seg = Segment(segid+"_"+str(sub_segid), all_data[all_start:all_end], fixation_data[fix_start:fix_end], saccade_data_in_part,
                                      event_data=event_data_in_part, aois=aoilist, prune_length=prune_length, rest_pupil_size = rest_pupil_size, export_pupilinfo = export_pupilinfo)
                except Exception as e:
                    warn(str(e))
                    if params.DEBUG:
                        raise
                    else:
                        new_sub_seg = None

                if new_sub_seg != None:
                    subsegments.append(new_sub_seg)
                    samp_inds.append((all_start,all_end))
                    fix_inds.append((fix_start, fix_end))
                    if saccade_data != None:
                        saccade_inds.append((sac_start, sac_end))
                    if event_data != None:
                        event_inds.append((event_start, event_end))
            #end of handling the last sub_seg

            return subsegments, samp_inds, fix_inds, saccade_inds, event_inds
        ######################################## end partition_segment()



        if len(all_data)<=0:
            raise Exception('A scene with no sample data!')
        if Segments == None:
            self.segments = []
#            print "seglist",seglist
            for (segid, start, end) in seglist:
                if params.VERBOSE != "QUIET":
                    print("segid, start, end:", segid, start, end)
                # Selecting subsets of points belonging only to the current segment
                if prune_length != None:
                    end = min(end, start+prune_length)
                _, all_start, all_end = get_chunk(all_data, 0, start, end)
                _, fix_start, fix_end = get_chunk(fixation_data, 0, start, end)
                if saccade_data != None:
                    _, sac_start, sac_end = get_chunk(saccade_data, 0, start, end)
                    saccade_data_in_seg = saccade_data[sac_start:sac_end]
                else:
                    sac_start = None
                    sac_end = None
                    saccade_data_in_seg = None
                if event_data != None:
                    _, event_start, event_end = get_chunk(event_data, 0, start, end)
                    event_data_in_seg = event_data[event_start:event_end]
                else:
                    event_start = None
                    event_end = None
                    event_data_in_seg = None

                if fix_end - fix_start>0:
                    try:
                        new_seg = Segment(segid, all_data[all_start:all_end], fixation_data[fix_start:fix_end], saccade_data = saccade_data_in_seg,
							        event_data=event_data_in_seg, aois=aoilist, prune_length=prune_length, rest_pupil_size = rest_pupil_size, export_pupilinfo = export_pupilinfo)
                    except  Exception as e:
                        warn(str(e))
                        if params.DEBUG:
                            raise
                        else:
                            continue
                else:
                    continue

                if (new_seg.largest_data_gap > params.MAX_SEG_TIMEGAP) and auto_partition: #low quality segment that needs to be partitioned!
                    try:
                        new_segs, samp_inds, fix_inds, sac_inds, event_inds = partition_segment(new_seg, start, end, rest_pupil_size, export_pupilinfo=export_pupilinfo)
                        if saccade_data != None and event_data != None:
                            for nseg,samp,fix,sac,eve in zip(new_segs, samp_inds, fix_inds, sac_inds, event_inds):
                                if nseg.length > params.MINSEGSIZE:
                                    nseg.set_indices(samp[0],samp[1],fix[0],fix[1],sac[0],sac[1],eve[0],eve[1])
                                    self.segments.append(nseg)
                        elif saccade_data != None and event_data == None:
                            for nseg,samp,fix,sac in zip(new_segs, samp_inds, fix_inds, sac_inds):
                                if nseg.length > params.MINSEGSIZE:
                                    nseg.set_indices(samp[0],samp[1],fix[0],fix[1],sac[0],sac[1])
                                    self.segments.append(nseg)
                        elif saccade_data == None and event_data != None:
                            for nseg,samp,fix,eve in zip(new_segs, samp_inds, fix_inds, event_inds):
                                if nseg.length > params.MINSEGSIZE:
                                    nseg.set_indices(samp[0],samp[1],fix[0],fix[1],event_st=eve[0],event_end=eve[1])
                                    self.segments.append(nseg)
                        else:
                            for nseg,samp,fix in zip(new_segs, samp_inds, fix_inds):
                                if nseg.length > params.MINSEGSIZE:
                                    nseg.set_indices(samp[0],samp[1],fix[0],fix[1])
                                    self.segments.append(nseg)
                    except Exception as e:
                        raise Exception("Error while partitioning scene. "+str(e))

                else:   #good quality segment OR no auto_partition
                    new_seg.set_indices(all_start,all_end,fix_start,fix_end,sac_start,sac_end,event_start,event_end)
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
        saccadelist = []
        totalfixations = 0
        firstsegtime = float('infinity')
        endsegtime = float(0)
        firstseg = None
        for seg in segments:
            sample_st,sample_end,fix_start,fix_end,sac_st,sac_end,event_st,event_end = seg.get_indices()
            if params.DEBUG or params.VERBOSE == "VERBOSE":
                print("sample_st,sample_end,fix_start,fix_end",sample_st,sample_end,fix_start,fix_end,sac_st,sac_end,event_st,event_end)
            fixationlist.append(fixation_data[fix_start:fix_end])
            totalfixations += len(fixationlist[-1])
            if seg.start < firstsegtime:
                firstsegtime = seg.start
                firstseg = seg
            if seg.end > endsegtime:
                endsegtime = seg.end
                endseg = seg
        fixationlist = []

        self.firstseg = firstseg
        self.endseg = endseg
        self.scid = scid
        self.features = {}
        self.largest_data_gap = maxfeat(self.segments,'largest_data_gap')   #self.segments is used to calculate validity of the scenes instead of segments which is only valid segments
        self.proportion_valid = weightedmeanfeat(self.segments,'numsamples','proportion_valid') #self.segments is used to calculate validity of the scenes instead of segments which is only valid segments
        self.proportion_valid_fix = weightedmeanfeat(self.segments,'numsamples','proportion_valid_fix') #self.segments is used to calculate validity of the scenes instead of segments which is only valid segments
        self.validity1 = self.calc_validity1()
        self.validity2 = self.calc_validity2()
        self.validity3 = self.calc_validity3()
        self.is_valid = self.get_validity()

        self.length = sumfeat(segments,"features['length']")
        if self.length == 0:
            raise Exception('Zero length segments!')

        self.length_invalid = self.get_length_invalid()

        self.features['numsegments'] = len(segments)
        self.features['length'] = self.length
        self.start = minfeat(segments,'start')
        self.numfixations = sumfeat(segments,'numfixations')
        self.end = maxfeat(segments,'end')
        self.numsamples = sumfeat(segments, 'numsamples')
        self.features['numsamples'] = self.numsamples

        if prune_length == None:
            if self.numfixations != totalfixations:
                if params.DEBUG:
                    raise Exception('Error in fixation count for scene: '+self.scid)
                else:
                    warn('Error in fixation count for scene: '+self.scid)

        self.merge_fixation_features(segments)

        self.merge_path_angle_features(segments)

        self.merge_blink_features(segments)

        self.merge_pupil_features(export_pupilinfo, segments)

        self.merge_distance_data(segments)

        self.merge_saccade_data(saccade_data, segments)

        self.merge_event_data(event_data, segments)

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
        if len(aois) == 0 and params.VERBOSE != "QUIET":
            print("No AOI in segment ", self.segid)

        self.aoi_data={}
        for seg in segments:
            for aid in seg.aoi_data.keys():
                    if aid in self.aoi_data:
                        if seg.aoi_data[aid].isActive:
                            self.aoi_data[aid] = merge_aoistats(self.aoi_data[aid],seg.aoi_data[aid], self.features['length'], self.numfixations, self.start)
                    else:
                        self.aoi_data[aid] = deepcopy(seg.aoi_data[aid])
                        if seg.aoi_data[aid].isActive:
                            self.aoi_data[aid].features['timetofirstfixation'] += self.aoi_data[aid].starttime - self.start
                            self.aoi_data[aid].features['timetolastfixation'] += self.aoi_data[aid].starttime - self.start

                            if self.firstseg.aoi_data[aid].features['timetofirstleftclic'] != -1:
                                self.aoi_data[aid].features['timetofirstleftclic'] += self.aoi_data[aid].starttime - self.start
                            if self.firstseg.aoi_data[aid].features['timetofirstrightclic'] != -1:
                                self.aoi_data[aid].features['timetofirstrightclic'] += self.aoi_data[aid].starttime - self.start
                            if self.firstseg.aoi_data[aid].features['timetofirstdoubleclic'] != -1:
                                self.aoi_data[aid].features['timetofirstdoubleclic'] += self.aoi_data[aid].starttime - self.start

                            if self.firstseg.aoi_data[aid].features['timetolastleftclic'] != -1:
                                self.aoi_data[aid].features['timetolastleftclic'] += self.aoi_data[aid].starttime - self.start
                            if self.firstseg.aoi_data[aid].features['timetolastrightclic'] != -1:
                                self.aoi_data[aid].features['timetolastrightclic'] += self.aoi_data[aid].starttime - self.start
                            if self.firstseg.aoi_data[aid].features['timetolastdoubleclic'] != -1:
                                self.aoi_data[aid].features['timetolastdoubleclic'] += self.aoi_data[aid].starttime - self.start
        #Merge stdev
        #For each seg, compute: T = [(numfix-1) * Variance + numfix * power( meanfixduration_in_seg - meanfixduration_in_scene, 2)]
        #At the Scene level: [ SQRT( SUM(T_seg1...Tsegn) / (numfix-1) ]
        for aid in self.aoi_data.keys():
            temp = 0
            numdata = 0
            for seg in segments:
                    temp += (seg.aoi_data[aid].features['numfixations']-1) * seg.aoi_data[aid].variance + seg.aoi_data[aid].features['numfixations'] * math.pow(seg.aoi_data[aid].features['meanfixationduration'] - self.aoi_data[aid].features['meanfixationduration'], 2)
                    numdata += seg.aoi_data[aid].features['numfixations']
            self.aoi_data[aid].features['stddevfixationduration'] = math.sqrt(temp / (numdata-1) ) if numdata > 1 else 0
        """
        firstsegaois = self.firstseg.aoi_data.keys()
        for aid in self.aoi_data.keys():
            if aid in firstsegaois:
                self.aoi_data[aid].features['timetofirstfixation'] = deepcopy(self.firstseg.aoi_data[aid].features['timetofirstfixation'])
                if self.firstseg.aoi_data[aid].features['timetofirstleftclic'] != -1:
                    self.aoi_data[aid].features['timetofirstleftclic'] = deepcopy(self.firstseg.aoi_data[aid].features['timetofirstleftclic'])
                    self.aoi_data[aid].features['timetofirstrightclic'] = deepcopy(self.firstseg.aoi_data[aid].features['timetofirstrightclic'])
                    self.aoi_data[aid].features['timetofirstdoubleclic'] = deepcopy(self.firstseg.aoi_data[aid].features['timetofirstdoubleclic'])
            else:
                self.aoi_data[aid].features['timetofirstfixation'] = float('inf')
                self.aoi_data[aid].features['timetofirstleftclic'] = float('inf')
                self.aoi_data[aid].features['timetofirstrightclic'] = float('inf')
                self.aoi_data[aid].features['timetofirstdoubleclic'] = float('inf')
        """
        if len(self.aoi_data) > 0:
            self.has_aois = True


    def merge_fixation_features(self, segments):
        """ Merge fixation features such as
                meanfixationduration:     mean duration of fixations
                stddevfixationduration    standard deviation of duration of fixations
                sumfixationduration:      sum of durations of fixations
                fixationrate:             rate of fixation datapoints relative to all datapoints
            Args:
                segments: The list of Segments for this Scene with pre-calculated features
        """
        self.numfixations = sumfeat(segments, 'numfixations')
        self.features['numfixations'] = self.numfixations
        self.features['fixationrate'] = float(self.numfixations) / (self.length - self.length_invalid)

        if self.numfixations > 0:
            self.features['meanfixationduration'] = weightedmeanfeat(segments,'numfixations',"features['meanfixationduration']")
            self.features['stddevfixationduration'] = aggregatestddevfeat(segments, 'numfixations', "features['stddevfixationduration']", "features['meanfixationduration']", self.features['meanfixationduration'])
            self.features['sumfixationduration'] = sumfeat(segments, "features['sumfixationduration']")
            self.features['fixationrate'] = float(self.numfixations)/(self.length - self.length_invalid)
        else:
            self.features['meanfixationduration'] = -1
            self.features['stddevfixationduration'] = -1
            self.features['sumfixationduration'] = -1
            self.features['fixationrate'] = -1


    def merge_path_angle_features(self, segments):
        """ Merge path and angle features such as
                meanpathdistance:         mean of path distances
                sumpathdistance:          sum of path distances
                eyemovementvelocity:      average eye movement velocity
                sumabspathangles:         sum of absolute path angles
                abspathanglesrate:        ratio of absolute path angles relative to all datapoints
                stddevabspathangles:      standard deviation of absolute path angles
                sumrelpathangles:         sum of relative path angles
                relpathanglesrate:        ratio of relative path angles relative to all datapoints
                stddevrelpathangles:      standard deviation of relative path angles
            Args:
                segments: The list of Segments for this Scene with pre-calculated features
        """
        self.numfixdistances = sumfeat(segments, "numfixdistances")
        self.numabsangles = sumfeat(segments, "numabsangles")
        self.numrelangles = sumfeat(segments, "numrelangles")

        if self.numfixations > 1:
            self.features['meanpathdistance'] = weightedmeanfeat(segments,'numfixdistances',"features['meanpathdistance']")
            self.features['sumpathdistance'] = sumfeat(segments, "features['sumpathdistance']")
            self.features['stddevpathdistance'] = aggregatestddevfeat(segments, 'numfixdistances', "features['stddevpathdistance']", "features['meanpathdistance']", self.features['meanpathdistance'])
            self.features['eyemovementvelocity'] = self.features['sumpathdistance']/(self.length - self.length_invalid)
            self.features['sumabspathangles'] = sumfeat(segments, "features['sumabspathangles']")
            self.features['meanabspathangles'] = weightedmeanfeat(segments,'numabsangles',"features['meanabspathangles']")
            self.features['abspathanglesrate'] = self.features['sumabspathangles']/(self.length - self.length_invalid)
            self.features['stddevabspathangles'] = aggregatestddevfeat(segments, 'numabsangles', "features['stddevabspathangles']", "features['meanabspathangles']", self.features['meanabspathangles'])
            self.features['sumrelpathangles'] = sumfeat(segments, "features['sumrelpathangles']")
            self.features['meanrelpathangles'] = weightedmeanfeat(segments,'numrelangles',"features['meanrelpathangles']")
            self.features['relpathanglesrate'] = self.features['sumrelpathangles']/(self.length - self.length_invalid)
            self.features['stddevrelpathangles'] = aggregatestddevfeat(segments, 'numrelangles', "features['stddevrelpathangles']", "features['meanrelpathangles']", self.features['meanrelpathangles'])
        else:
            self.features['meanpathdistance'] = -1
            self.features['sumpathdistance'] = -1
            self.features['stddevpathdistance'] = -1
            self.features['eyemovementvelocity'] = -1
            self.features['sumabspathangles'] = -1
            self.features['abspathanglesrate'] = -1
            self.features['meanabspathangles']= -1
            self.features['stddevabspathangles']= -1
            self.features['sumrelpathangles'] = -1
            self.features['relpathanglesrate'] = -1
            self.features['meanrelpathangles']= -1
            self.features['stddevrelpathangles'] = -1


    def merge_blink_features(self, segments):
        """ Merge blink features asuch as
                blink_num:                 number of blinks
                blink_duration_total:       sum of the blink durations
                blink_duration_mean:        mean of the blink durations
                blink_duration_std:         standard deviation of blink durations
                blink_duration_max:         maximal blink duration
                blink_duration_min:         minimal blink duration
                blink_rate:                 rate of blinks
                blink_time_distance_mean:   mean time difference between consequtive blinks
                blink_time_distance_std:    std time difference between consequtive blinks
                blink_time_distance_min:    minimal time difference between consequtive blinks
                blink_time_distance_max:    maximal time difference between consequtive blinks
            Args:
                segments: The list of Segments for this Scene with pre-calculated features
        """
        self.features['blinknum'] = sumfeat(segments, "features['blinknum']")
        if self.features['blinknum'] > 0:
            self.features['blinkdurationtotal']     = sumfeat(segments, "features['blinkdurationtotal']")
            self.features['blinkdurationmean']      = weightedmeanfeat(segments, "features['blinknum']", "features['blinkdurationmean']")
            self.features['blinkdurationstd']       = aggregatestddevfeat(segments, "features['blinknum']", "features['blinkdurationstd']",
                                                      "features['blinkdurationmean']", self.features['blinkdurationmean'])
            self.features['blinkdurationmin']       = minfeat(segments, "features['blinkdurationmin']", -1)
            self.features['blinkdurationmax']       = maxfeat(segments, "features['blinkdurationmax']")
            self.features['blinkrate']              = float(self.features['blinknum']) / (self.length - self.length_invalid)
            self.features['blinktimedistancemean']  = weightedmeanfeat(segments,
                                                      "features['blinknum']", "features['blinktimedistancemean']")
            self.features['blinktimedistancestd']   = aggregatestddevfeat(segments, "features['blinknum']",
                                                      "features['blinktimedistancestd']", "features['blinktimedistancemean']",
                                                      self.features['blinktimedistancemean'])
            self.features['blinktimedistancemin']   = minfeat(segments, "features['blinktimedistancemin']", -1)
            self.features['blinktimedistancemax']   = maxfeat(segments, "features['blinktimedistancemax']")
        else:
            self.features['blinkdurationtotal']     = -1
            self.features['blinkdurationmean']      = -1
            self.features['blinkdurationstd']       = -1
            self.features['blinkdurationmin']       = -1
            self.features['blinkdurationmax']       = -1
            self.features['blinkrate']              = -1
            self.features['blinktimedistancemean']  = -1
            self.features['blinktimedistancestd']   = -1
            self.features['blinktimedistancemin']   = -1
            self.features['blinktimedistancemax']   = -1


    def merge_pupil_features(self, export_pupilinfo, segments):
        """ Merge pupil features asuch as
                mean_pupil_size:            mean of pupil sizes
                stddev_pupil_size:          standard deviation of pupil sizes
                min_pupil_size:             smallest pupil size
                max_pupil_size:             largest pupil size
                mean_pupil_velocity:        mean of pupil velocities
                stddev_pupil_velocity:      standard deviation of pupil velocities
                min_pupil_velocity:         smallest pupil velocity
                max_pupil_velocity:         largest pupil velocity
            Args:
                segments: The list of Segments for this Scene with pre-calculated features
                export_pupilinfo: True to export raw pupil data in EMDAT output (False by default).
        """
        self.numpupilsizes    = sumfeat(segments,'numpupilsizes')
        self.numpupilvelocity = sumfeat(segments,'numpupilvelocity')

        if self.numpupilsizes > 0: # check if scene has any pupil data
            if export_pupilinfo:
                self.pupilinfo_for_export = mergevalues(segments, 'pupilinfo_for_export')
            self.features['meanpupilsize'] = weightedmeanfeat(segments, 'numpupilsizes', "features['meanpupilsize']")
            self.features['stddevpupilsize'] = aggregatestddevfeat(segments, 'numpupilsizes', "features['stddevpupilsize']", "features['meanpupilsize']", self.features['meanpupilsize']) #stddev(self.adjvalidpupilsizes)
            self.features['maxpupilsize'] = maxfeat(segments, "features['maxpupilsize']")
            self.features['minpupilsize'] = minfeat(segments, "features['minpupilsize']", -1)
            self.features['startpupilsize'] = self.firstseg.features['startpupilsize']
            self.features['endpupilsize'] = self.endseg.features['endpupilsize']
        else:
            self.pupilinfo_for_export = []
            self.features['meanpupilsize'] = -1
            self.features['stddevpupilsize'] = -1
            self.features['maxpupilsize'] = -1
            self.features['minpupilsize'] = -1
            self.features['startpupilsize'] = -1
            self.features['endpupilsize'] = -1

        if self.numpupilvelocity > 0: # check if scene has any pupil velocity data
            self.features['meanpupilvelocity'] = weightedmeanfeat(segments, 'numpupilvelocity', "features['meanpupilvelocity']")
            self.features['stddevpupilvelocity'] = aggregatestddevfeat(segments, 'numpupilvelocity', "features['stddevpupilvelocity']", "features['meanpupilvelocity']", self.features['meanpupilvelocity']) #stddev(self.valid_pupil_velocity)
            self.features['maxpupilvelocity'] = maxfeat(segments, "features['maxpupilvelocity']")
            self.features['minpupilvelocity'] = minfeat(segments, "features['minpupilvelocity']", -1)
        else:
            self.features['meanpupilvelocity'] = -1
            self.features['stddevpupilvelocity'] = -1
            self.features['maxpupilvelocity'] = -1
            self.features['minpupilvelocity'] = -1


    def merge_distance_data(self, segments):
        """ Merge distance features such as
                mean_distance:            mean of distances from the screen
                stddev_distance:          standard deviation of distances from the screen
                min_distance:             smallest distance from the screen
                max_distance:             largest distance from the screen
                start_distance:           distance from the screen in the beginning of this scene
                end_distance:             distance from the screen in the end of this scene

            Args:
                segments: The list of Segments for this Scene with pre-calculated features
        """
        self.numdistancedata = sumfeat(segments,'numdistancedata') #Distance
        if self.numdistancedata > 0: # check if scene has any pupil data
            self.features['meandistance'] = weightedmeanfeat(segments, 'numdistancedata', "features['meandistance']")
            self.features['stddevdistance'] = aggregatestddevfeat(segments, 'numdistancedata', "features['stddevdistance']", "features['meandistance']", self.features['meandistance'])
            self.features['maxdistance'] = maxfeat(segments, "features['maxdistance']")
            self.features['mindistance'] = minfeat(segments, "features['mindistance']", -1)
            self.features['startdistance'] = self.firstseg.features['startdistance']
            self.features['enddistance'] = self.endseg.features['enddistance']
        else:
            self.features['meandistance'] = -1
            self.features['stddevdistance'] = -1
            self.features['maxdistance'] = -1
            self.features['mindistance'] = -1
            self.features['startdistance'] = -1
            self.features['enddistance'] = -1


    def merge_saccade_data(self, saccade_data, segments):
        """ Merge saccade features such as
                numsaccades:              number of saccades in the segment
                sumsaccadedistance:       sum of distances during each saccade
                meansaccadedistance:      mean of distances during each saccade
                stddevsaccadedistance:    standard deviation of distances during each saccade
                longestsaccadedistance:   distance of longest saccade
                sumsaccadeduration:       total time spent on saccades in this segment
                meansaccadeduration:      average saccade duration
                stddevsaccadeduration:    standard deviation of saccade durations
                longestsaccadeduration:   longest duration of saccades in this segment
                meansaccadespeed:         average speed of saccades in this segment
                stddevsaccadespeed:       standard deviation of speed of saccades in this segment
                maxsaccadespeed:          highest saccade speed in this segment
                minsaccadespeed:          lowest saccade speed in this  segment
                fixationsaccadetimeratio: fixation to saccade time ratio for this segment
            Args:
                saccade_data: The list of saccade datapoints for this Scene
                segments: The list of Segments for this Scene with pre-calculated features
        """
        if saccade_data != None:
            self.features['numsaccades'] = sumfeat(segments,'numsaccades')
            self.features['sumsaccadedistance'] = sumfeat(segments, "features['sumsaccadedistance']")
            self.features['meansaccadedistance'] = weightedmeanfeat(self.segments,'numsaccades',"features['meansaccadedistance']")
            self.features['stddevsaccadedistance'] = aggregatestddevfeat(segments, 'numsaccades', "features['stddevsaccadedistance']", "features['meansaccadedistance']", self.features['meansaccadedistance'])
            self.features['longestsaccadedistance'] = maxfeat(segments, "features['longestsaccadedistance']")
            self.features['sumsaccadeduration'] = sumfeat(segments,"features['sumsaccadeduration']")
            self.features['meansaccadeduration'] = weightedmeanfeat(self.segments,'numsaccades',"features['meansaccadeduration']")
            self.features['stddevsaccadeduration'] = aggregatestddevfeat(segments, 'numsaccades', "features['stddevsaccadeduration']", "features['meansaccadeduration']", self.features['meansaccadeduration'])
            self.features['longestsaccadeduration'] = maxfeat(segments, "features['longestsaccadeduration']")
            self.features['meansaccadespeed'] = weightedmeanfeat(self.segments,'numsaccades',"features['meansaccadespeed']")
            self.features['stddevsaccadespeed'] = aggregatestddevfeat(segments, 'numsaccades', "features['stddevsaccadespeed']", "features['meansaccadespeed']", self.features['meansaccadespeed'])
            self.features['maxsaccadespeed'] = maxfeat(segments, "features['maxsaccadespeed']")
            self.features['minsaccadespeed'] = minfeat(segments, "features['minsaccadespeed']", -1)
            self.features['fixationsaccadetimeratio'] = sumfeat(segments, "features['fixationsaccadetimeratio']") / float(len(segments))
        else:
            self.features['numsaccades'] = 0
            self.features['sumsaccadedistance'] = -1
            self.features['meansaccadedistance'] = -1
            self.features['stddevsaccadedistance'] = -1
            self.features['longestsaccadedistance'] = -1
            self.features['sumsaccadeduration'] = -1
            self.features['meansaccadeduration'] = -1
            self.features['stddevsaccadeduration'] = -1
            self.features['longestsaccadeduration'] = -1
            self.features['meansaccadespeed'] = -1
            self.features['stddevsaccadespeed'] = -1
            self.features['maxsaccadespeed'] = -1
            self.features['minsaccadespeed'] = -1
            self.features['fixationsaccadetimeratio'] = -1


    def merge_event_data(self, event_data, segments):
        """ Merge event features such as
                numevents:                number of events in the segment
                numleftclic:              number of left clinks in the segment
                numrightclic:             number of right clinks in the segment
                numdoubleclic:            number of double clinks in the segment
                numkeypressed:            number of times a key was pressed in the segment
                leftclicrate:             the rate of left clicks (relative to all datapoints) in this segment
                rightclicrate:            the rate of right clicks (relative to all datapoints) in this segment
                doubleclicrate:           the rate of double clicks (relative to all datapoints) in this segment
                keypressedrate:           the rate of key presses (relative to all datapoints) in this segment
                timetofirstleftclic:      time until the first left click in this segment
                timetofirstrightclic:     time until the first right click in this segment
                timetofirstdoubleclic:    time until the first double click in this segment
                timetofirstkeypressed:    time until the first key pressed in this segment
            Args:
                event_data: The list of events for this Scene
                segments: The list of Segments for this Scene with pre-calculated features
        """
        if event_data != None:
            self.features['numevents'] = sumfeat(segments,'numevents')
            self.features['numleftclic'] = sumfeat(segments,"features['numleftclic']")
            self.features['numrightclic'] = sumfeat(segments, "features['numrightclic']")
            self.features['numdoubleclic'] = sumfeat(segments, "features['numdoubleclic']")
            self.features['numkeypressed'] = sumfeat(segments, "features['numkeypressed']")
            self.features['leftclicrate'] = float(self.features['numleftclic'])/(self.length - self.length_invalid)
            self.features['rightclicrate'] = float(self.features['numrightclic'])/(self.length - self.length_invalid)
            self.features['doubleclicrate'] = float(self.features['numdoubleclic'])/(self.length - self.length_invalid)
            self.features['keypressedrate'] = float(self.features['numkeypressed'])/(self.length - self.length_invalid)
            self.features['timetofirstleftclic'] = self.firstseg.features['timetofirstleftclic']
            self.features['timetofirstrightclic'] = self.firstseg.features['timetofirstrightclic']
            self.features['timetofirstdoubleclic'] = self.firstseg.features['timetofirstdoubleclic']
            self.features['timetofirstkeypressed'] = self.firstseg.features['timetofirstkeypressed']
        else:
            self.features['numevents'] = 0
            self.features['numleftclic'] = 0
            self.features['numrightclic'] = 0
            self.features['numdoubleclic'] = 0
            self.features['numkeypressed'] = 0
            self.features['leftclicrate'] = -1
            self.features['rightclicrate'] = -1
            self.features['doubleclicrate'] = -1
            self.features['keypressedrate'] = -1
            self.features['timetofirstleftclic'] = -1
            self.features['timetofirstrightclic'] = -1
            self.features['timetofirstdoubleclic'] = -1
            self.features['timetofirstkeypressed'] = -1

    def merge_aoisequences(self, segments):
        """returns the AOI sequence merged from the AOI sequences in the "Segment"s
        Args:
            segments: a list of "Segment"s which belong to this Scene.
        Returns:
            a list of AOI names that correspond to the sequence of "Fixation"s in this Scene
        """
        sequence = []
        for seg in segments:
            sequence.extend(seg.features.get('aoisequence', []))
        return sequence

    def get_length_invalid(self):
        length = 0
        for segment in self.segments:
            length += segment.length_invalid
        return length

    def clean_memory(self):
        return
        #for seg in self.segments:
        #   seg.adjvalidpupilsizes = []
        #    seg.distances_from_screen = []
        #self.adjvalidpupilsizes = []
        #self.distances_from_screen = []

def merge_aoistats(main_AOI_Stat,new_AOI_Stat,total_time,total_numfixations,sc_start=0):
        """a helper method that updates the AOI_Stat object of this Scene with a new AOI_Stat object

        Args:
            main_AOI_Stat: AOI_Stat object of this Scene (must have been initialised)

            new_AOI_Stat: a new AOI_Stat object

            total_time: duration of the scene

            total_numfixations: number of fixations in the scene

            sc_start: start time (timestamp) of the scene

        Returns:
            the updated AOI_Sata object
        """
        maois = main_AOI_Stat
        merge_aoi_fixations(maois, new_AOI_Stat, total_time, total_numfixations, sc_start)
        #calculating the transitions to and from this AOI and other active AOIs at the moment
        new_AOI_Stat_transition_aois = filter(lambda x: x.startswith('numtransfrom_'), new_AOI_Stat.features.keys())
        if params.DEBUG or params.VERBOSE == "VERBOSE":
            print("Segment's transition_aois", new_AOI_Stat_transition_aois)

        merge_aoi_events(maois, new_AOI_Stat, total_time, sc_start)

        maois.total_trans_from += new_AOI_Stat.total_trans_from   #updating the total number of transition from this AOI
        for feat in new_AOI_Stat_transition_aois:
            if feat in maois.features:
                maois.features[feat] += new_AOI_Stat.features[feat]
            else:
                maois.features[feat] = new_AOI_Stat.features[feat]
#               sumtransfrom += maois.features[feat]

        merge_aoi_distance(maois, new_AOI_Stat)
        merge_aoi_pupil(maois, new_AOI_Stat)
        # updating the proportion tansition features based on new transitions to and from this AOI
        maois_transition_aois = filter(lambda x: x.startswith('numtransfrom_'),maois.features.keys()) #all the transition features for this AOI should be aupdated even if they are not active for this segment
        for feat in maois_transition_aois:
            aid = feat[len('numtransfrom_'):]
            if maois.total_trans_from > 0:
                maois.features['proptransfrom_%s'%(aid)] = float(maois.features[feat]) / maois.total_trans_from
            else:
                maois.features['proptransfrom_%s'%(aid)] = 0
        ###endof transition calculation
        return maois


def merge_aoi_fixations(maois, new_AOI_Stat, total_time, total_numfixations, sc_start):
    """ Merge fixation features such as
            meanfixationduration:     mean duration of fixations
            stddevfixationduration    standard deviation of duration of fixations
            sumfixationduration:      sum of durations of fixations
            fixationrate:             rate of fixation datapoints relative to all datapoints
        Args:
            main_AOI_Stat: AOI_Stat object of this Scene (must have been initialised)

            new_AOI_Stat: a new AOI_Stat object

            total_time: duration of the scene

            total_numfixations: number of fixations in the scene

            sc_start: start time (timestamp) of the scene
    """
    if new_AOI_Stat.features['numfixations'] > 0:
        aoi_list = [maois, new_AOI_Stat]
        numfixations = sumfeat(aoi_list, "features['numfixations']")
        maois.features['longestfixation'] = maxfeat(aoi_list, "features['longestfixation']")
        maois.features['totaltimespent'] += new_AOI_Stat.features['totaltimespent']
        aggregate_meanfixationduration = maois.features['totaltimespent'] / numfixations
        maois.features['stddevfixationduration'] = aggregatestddevfeat(aoi_list, "features['numfixations']", "features['stddevfixationduration']", "features['meanfixationduration']", aggregate_meanfixationduration)
        maois.features['numfixations'] +=  new_AOI_Stat.features['numfixations']
        maois.features['meanfixationduration'] = aggregate_meanfixationduration
        maois.features['proportiontime'] = float(maois.features['totaltimespent'])/total_time
        maois.features['proportionnum'] = float(maois.features['numfixations'])/total_numfixations

        if maois.features['totaltimespent'] > 0:
            maois.features['fixationrate'] = float(maois.features['numfixations']) / maois.features['totaltimespent']
        else:
            maois.features['fixationrate'] = -1

        if new_AOI_Stat.features['timetofirstfixation'] != -1:
            maois.features['timetofirstfixation'] = min(maois.features['timetofirstfixation'], deepcopy(new_AOI_Stat.features['timetofirstfixation']) + new_AOI_Stat.starttime - sc_start)
        if new_AOI_Stat.features['timetolastfixation'] != -1:
            maois.features['timetolastfixation'] = max(maois.features['timetolastfixation'], deepcopy(new_AOI_Stat.features['timetolastfixation']) + new_AOI_Stat.starttime - sc_start)


def merge_aoi_distance(maois, new_AOI_Stat):
    """ Merge distance features such as
            mean_distance:            mean of distances from the screen
            stddev_distance:          standard deviation of distances from the screen
            min_distance:             smallest distance from the screen
            max_distance:             largest distance from the screen
            start_distance:           distance from the screen in the beginning of this scene
            end_distance:             distance from the screen in the end of this scene

        Args:
            maois: AOI_Stat object of this Scene (must have been initialised)
            new_AOI_Stat: a new AOI_Stat object
    """
    aoi_list = [maois, new_AOI_Stat]
    if new_AOI_Stat.numdistancedata > 0:
        total_distances = sumfeat(aoi_list, 'numdistancedata')
        aggregate_mean_distance = weightedmeanfeat(aoi_list, 'numdistancedata', "features['meandistance']")
        maois.features['stddevdistance'] = aggregatestddevfeat(aoi_list, 'numdistancedata', "features['stddevdistance']",
                                                                    "features['meandistance']", aggregate_mean_distance)
        maois.features['maxdistance'] = maxfeat(aoi_list, "features['maxdistance']")
        maois.features['mindistance'] = minfeat(aoi_list, "features['mindistance']")
        maois.features['meandistance'] = aggregate_mean_distance
        if maois.starttime > new_AOI_Stat.starttime:
            maois.features['startdistance'] = new_AOI_Stat.features['startdistance']
        if maois.endtime < new_AOI_Stat.endtime:
            maois.features['enddistance'] = new_AOI_Stat.features['enddistance']
        maois.numdistancedata += new_AOI_Stat.numdistancedata

def merge_aoi_pupil(maois, new_AOI_Stat):
    """ Merge pupil features asuch as
            mean_pupil_size:            mean of pupil sizes
            stddev_pupil_size:          standard deviation of pupil sizes
            min_pupil_size:             smallest pupil size
            max_pupil_size:             largest pupil size
            mean_pupil_velocity:        mean of pupil velocities
            stddev_pupil_velocity:      standard deviation of pupil velocities
            min_pupil_velocity:         smallest pupil velocity
            max_pupil_velocity:         largest pupil velocity
        Args:
            maois: AOI_Stat object of this Scene (must have been initialised)
            new_AOI_Stat: a new AOI_Stat object
    """
    aoi_list = [maois, new_AOI_Stat]
    if (new_AOI_Stat.numpupilsizes > 0):
        aggregate_mean_pupil = weightedmeanfeat(aoi_list, 'numpupilsizes', "features['meanpupilsize']")
        maois.features['stddevpupilsize'] = aggregatestddevfeat(aoi_list, 'numpupilsizes', "features['stddevpupilsize']",
                                                                        "features['meanpupilsize']", aggregate_mean_pupil)
        maois.features['maxpupilsize'] = maxfeat(aoi_list, "features['maxpupilsize']")
        maois.features['minpupilsize'] = minfeat(aoi_list, "features['minpupilsize']")
        maois.features['meanpupilsize'] = aggregate_mean_pupil
        if maois.starttime > new_AOI_Stat.starttime:
            maois.features['startpupilsize'] = new_AOI_Stat.features['startpupilsize']
        if maois.endtime < new_AOI_Stat.endtime:
            maois.features['endpupilsize'] = new_AOI_Stat.features['endpupilsize']
        maois.numpupilsizes += new_AOI_Stat.numpupilsizes

    if (new_AOI_Stat.numpupilvelocity > 0):
        aggregate_mean_velocity =  weightedmeanfeat(aoi_list, 'numpupilvelocity', "features['meanpupilvelocity']")
        maois.features['stddevpupilvelocity'] = aggregatestddevfeat(aoi_list, 'numpupilvelocity', "features['stddevpupilvelocity']",
                                                                        "features['meanpupilvelocity']", aggregate_mean_velocity)
        maois.features['maxpupilvelocity'] = maxfeat(aoi_list, "features['maxpupilvelocity']")
        maois.features['minpupilvelocity'] = minfeat(aoi_list, "features['minpupilvelocity']")
        maois.features['meanpupilvelocity'] = aggregate_mean_velocity
        maois.numpupilvelocity += new_AOI_Stat.numpupilvelocity

def merge_aoi_events(maois, new_AOI_Stat, total_time, sc_start):
    """ Merge event features such as
            numevents:                number of events in the segment
            numleftclic:              number of left clinks in the segment
            numrightclic:             number of right clinks in the segment
            numdoubleclic:            number of double clinks in the segment
            numkeypressed:            number of times a key was pressed in the segment
            leftclicrate:             the rate of left clicks (relative to all datapoints) in this segment
            rightclicrate:            the rate of right clicks (relative to all datapoints) in this segment
            doubleclicrate:           the rate of double clicks (relative to all datapoints) in this segment
            keypressedrate:           the rate of key presses (relative to all datapoints) in this segment
            timetofirstleftclic:      time until the first left click in this segment
            timetofirstrightclic:     time until the first right click in this segment
            timetofirstdoubleclic:    time until the first double click in this segment
            timetofirstkeypressed:    time until the first key pressed in this segment
        Args:
            maois: AOI_Stat object of this Scene (must have been initialised)
            new_AOI_Stat: a new AOI_Stat object
            total_time: duration of the scene
            sc_start: start time (timestamp) of the scene
    """
    if new_AOI_Stat.features['numevents']>0:
        maois.features['numevents'] += new_AOI_Stat.features['numevents']
        maois.features['numleftclic'] += new_AOI_Stat.features['numleftclic']
        maois.features['numrightclic'] += new_AOI_Stat.features['numrightclic']
        maois.features['numdoubleclic'] += new_AOI_Stat.features['numdoubleclic']
        maois.features['leftclicrate'] = float(maois.features['numleftclic'])/total_time
        maois.features['rightclicrate'] = float(maois.features['numrightclic'])/total_time
        maois.features['doubleclicrate'] = float(maois.features['numdoubleclic'])/total_time

        if new_AOI_Stat.features['timetofirstleftclic'] != -1:
            maois.features['timetofirstleftclic'] = min(maois.features['timetofirstleftclic'], deepcopy(new_AOI_Stat.features['timetofirstleftclic']) + new_AOI_Stat.starttime - sc_start)
        if new_AOI_Stat.features['timetofirstrightclic'] != -1:
            maois.features['timetofirstrightclic'] = min(maois.features['timetofirstrightclic'], deepcopy(new_AOI_Stat.features['timetofirstrightclic']) + new_AOI_Stat.starttime - sc_start)
        if new_AOI_Stat.features['timetofirstdoubleclic'] != -1:
            maois.features['timetofirstdoubleclic'] = min(maois.features['timetofirstdoubleclic'], deepcopy(new_AOI_Stat.features['timetofirstdoubleclic']) + new_AOI_Stat.starttime - sc_start)

        if new_AOI_Stat.features['timetolastleftclic'] != -1:
            maois.features['timetolastleftclic'] = max(maois.features['timetolastleftclic'], deepcopy(new_AOI_Stat.features['timetolastleftclic']) + new_AOI_Stat.starttime - sc_start)
        if new_AOI_Stat.features['timetolastrightclic'] != -1:
            maois.features['timetolastrightclic'] = max(maois.features['timetolastrightclic'], deepcopy(new_AOI_Stat.features['timetolastrightclic']) + new_AOI_Stat.starttime - sc_start)
        if new_AOI_Stat.features['timetolastdoubleclic'] != -1:
            maois.features['timetolastdoubleclic'] = max(maois.features['timetolastdoubleclic'], deepcopy(new_AOI_Stat.features['timetolastdoubleclic']) + new_AOI_Stat.starttime - sc_start)


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

def aggregatestddevfeat(obj_list, totalfeat, sdfeat, meanfeat, meanscene):
    """a helper method that calculates the aggregated standard deviation of a target feature over a list of Segments

    Args:
        obj_list: a list of Segments which all have a numeric field for which the stdev is calculated

        totalfeat: a string containing the name of the feature that has the total value of the target feature

        ratefeat: a string containing the name of the feature that has the rate value of the target feature

    Returns:
        the weighted average of the ratefeat over the Segments
    """
    num = float(0)
    den = float(0)

    for obj in obj_list:
        t = eval('obj.'+totalfeat)
        if t > 0:
            sd = eval('obj.'+sdfeat)
            if math.isnan(sd): sd = 0
            meanobj = eval('obj.'+meanfeat)

            num += (t-1) * sd**2 + t * (meanobj-meanscene)**2
            den += t

    if den > 1:
        return math.sqrt(float(num)/(den-1))
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

def minfeat(obj_list, feat, nonevalue = None):
    """a helper method that calculates the min of a target feature over a list of objects

    Args:

        obj_list: a list of objects

        feat: a string containing the name of the target feature

        nonevalue: value to be ignored when computing the min (typically -1 in EMDAT)

    Returns:
        the min of the target feature over the given list of objects
    """
    min = float('+infinity')
    for obj in obj_list:
        val = eval('obj.'+feat)
        if min > val and val != nonevalue:
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
